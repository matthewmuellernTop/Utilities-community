"""
teal_aero.py - quick aero performance estimates for the nTop Lesher Teal notebook.

The aircraft is described entirely by key=value arguments, so nTop's Run Command
block can send the current geometry on every change (no files, no API). Any key
you leave out keeps its Lesher Teal baseline value. The airplane is rebuilt in
AeroSandbox and analyzed with AeroBuildup (fast semi-empirical buildup with
NeuralFoil airfoil polars) in a few seconds.

    pip install aerosandbox
    python teal_aero.py                                  # baseline Teal
    python teal_aero.py wing.span=8 wing.x=2.4 mass=520  # change anything
    python teal_aero.py --list                           # show every key

Units: lengths in m, angles in deg, mass in kg, speed in m/s.

Components are named by prefix. Which kind a component is comes from its keys:
  span=...    symmetric lifting surface (wing, hstab, canard, ...), built like
              nTop's "Basic 1 Panel Wing": x,y,z = root leading edge, chord = root
              chord, sweep at quarter chord, twist ramped over the full span.
  height=...  fin, built like "Single Panel Vertical Stabilizer". mirror=1 adds
              a copy at -y, down=1 points it down instead of up.
  top_x=...   fuselage from rails (":"-separated lists): top_x/top_z,
              side_x/side_y, bottom_x/bottom_z.
"""

import argparse
import csv
import json
import math
import os
import sys

import numpy as np

PROP_EFFICIENCY = 0.80

# Lesher Teal baseline (matches the starter notebook).
BASELINE = {
    "mass": 500.0,       # kg, Teal max takeoff weight
    "speed": 82.0,       # m/s, 160 kn cruise
    "altitude": 0.0,     # m
    "xcg": 2.53,         # m
    "wing.x": 2.3, "wing.y": 0.0, "wing.z": 0.38, "wing.chord": 0.903, "wing.naca": "3418",
    "wing.span": 7.26, "wing.sweep": 0.0, "wing.taper": 0.7, "wing.twist": 0.0, "wing.dihedral": 2.0,
    "hstab.x": 4.95, "hstab.y": 0.0, "hstab.z": 0.12, "hstab.chord": 0.55, "hstab.naca": "0012",
    "hstab.span": 1.9, "hstab.sweep": 5.0, "hstab.taper": 0.85, "hstab.twist": 0.0, "hstab.dihedral": 0.0,
    "vstab.x": 5.052, "vstab.y": 0.93, "vstab.z": 0.12, "vstab.chord": 0.47, "vstab.naca": "0010",
    "vstab.height": 0.5, "vstab.sweep": 25.0, "vstab.taper": 0.6, "vstab.mirror": 1, "vstab.down": 0,
    "ventral.x": 4.95, "ventral.y": 0.0, "ventral.z": 0.0, "ventral.chord": 0.55, "ventral.naca": "0010",
    "ventral.height": 0.4, "ventral.sweep": 25.0, "ventral.taper": 0.6, "ventral.mirror": 0, "ventral.down": 1,
    "fuse.top_x": "0:0.45:1.05:1.55:2.05:2.6:3.4:4.4:5.3:5.87",
    "fuse.top_z": "-0.1:0.1:0.3:0.6:0.64:0.54:0.4:0.24:0.14:0.1",
    "fuse.side_x": "0:0.35:0.9:1.7:2.6:3.6:4.6:5.87",
    "fuse.side_y": "0.01:0.17:0.3:0.36:0.35:0.26:0.15:0.05",
    "fuse.bottom_x": "0:0.35:0.9:1.8:2.8:3.8:4.8:5.87",
    "fuse.bottom_z": "-0.1:-0.28:-0.4:-0.44:-0.4:-0.26:-0.1:0.04",
}
SURFACE_KEYS = ["x", "y", "z", "chord", "naca", "span", "sweep", "taper", "twist", "dihedral"]
FIN_KEYS = ["x", "y", "z", "chord", "naca", "height", "sweep", "taper", "mirror", "down"]
FUSE_KEYS = ["top_x", "top_z", "side_x", "side_y", "bottom_x", "bottom_z"]

# Values printed for nTop with --ntop, in this order (the notebook reads them by index).
NTOP_OUTPUTS = ["CL_cruise", "CD_cruise", "LD_cruise", "x_neutral_point_m",
                "static_margin_pct_MAC", "LD_max", "alpha_cruise_deg"]


def parse_params(tokens):
    params = dict(BASELINE)
    for tok in tokens:
        key, sep, value = tok.partition("=")
        if not sep:
            raise SystemExit(f"Expected key=value, got '{tok}'")
        params[key.strip()] = value.strip()
    return params


def components(params):
    comps = {}
    for key, value in params.items():
        if "." in key:
            prefix, field = key.split(".", 1)
            comps.setdefault(prefix, {})[field] = value
    return comps


def build_airplane(params):
    import aerosandbox as asb

    wings, fuselages, summary = [], [], []
    for name, c in components(params).items():
        if "span" in c or "height" in c:
            fin = "height" in c
            required = FIN_KEYS[:8] if fin else SURFACE_KEYS
            missing = [k for k in required if k not in c]
            if missing:
                raise SystemExit(f"{name}: missing {', '.join(name + '.' + k for k in missing)}")
            f = {k: float(v) for k, v in c.items() if k != "naca"}
            root = np.array([f["x"], f["y"], f["z"]])
            cr, ct = f["chord"], f["chord"] * f["taper"]
            half = f["height"] if fin else f["span"] / 2
            sweep = math.radians(f["sweep"])
            # Root LE at (x, y, z); sweep measured on the quarter-chord line.
            tip_dx = 0.25 * cr + half * math.tan(sweep) - 0.25 * ct
            naca = str(c["naca"]).strip().zfill(4)
            af = asb.Airfoil(f"naca{naca}")
            if fin:
                le_tips = [root + [tip_dx, 0, -half if f.get("down") else half]]
                roots = [root]
                if f.get("mirror"):
                    roots.append(root * [1, -1, 1])
                    le_tips.append(le_tips[0] * [1, -1, 1])
                for i, (r, t) in enumerate(zip(roots, le_tips)):
                    wings.append(asb.Wing(name=f"{name}{'_mirror' if i else ''}", symmetric=False, xsecs=[
                        asb.WingXSec(xyz_le=r, chord=cr, airfoil=af),
                        asb.WingXSec(xyz_le=t, chord=ct, airfoil=af)]))
            else:
                # Dihedral is a rotation about the global X axis, as in the nTop block.
                g = math.radians(f["dihedral"])
                R = np.array([[1, 0, 0], [0, math.cos(g), -math.sin(g)], [0, math.sin(g), math.cos(g)]])
                le_root = R @ root
                le_root[1] = 0.0
                le_tip = R @ (root + [tip_dx, half, 0])
                # The block ramps twist over the full span, so the tip sees half of it.
                # Positive twist is read as washout (tip nose-down).
                tip_twist = -f["twist"] / 2
                wings.append(asb.Wing(name=name, symmetric=True, xsecs=[
                    asb.WingXSec(xyz_le=le_root, chord=cr, airfoil=af),
                    asb.WingXSec(xyz_le=le_tip, chord=ct, twist=tip_twist, airfoil=af)]))
            summary.append((name, f"NACA {naca}, {'height' if fin else 'span'} {2 * half if not fin else half:.3f} m, "
                                  f"root chord {cr:.3f} m, taper {f['taper']:.2f}, sweep {f['sweep']:.1f} deg"
                                  + (", mirrored" if fin and f.get("mirror") else "")))
        elif "top_x" in c:
            fuselages.append(_fuselage(asb, c))
            summary.append((name, "fuselage from top/side/bottom rails"))
        else:
            raise SystemExit(f"Don't know what '{name}' is: give it span= (wing), height= (fin) "
                             f"or rails (fuselage). Keys seen: {', '.join(c)}")

    lifting = [w for w in wings if w.symmetric]
    if not lifting:
        raise SystemExit("Need at least one symmetric lifting surface (a component with span=).")
    # Main wing = biggest symmetric surface; it sets the reference values.
    main = max(lifting, key=lambda w: w.area())
    wings.sort(key=lambda w: w is not main)
    plane = asb.Airplane(name="Teal", wings=wings, fuselages=fuselages,
                         s_ref=main.area(), c_ref=main.mean_aerodynamic_chord(), b_ref=main.span())
    return plane, main, summary


def _fuselage(asb, c):
    """Elliptic cross sections through the top, side and bottom rails."""
    from scipy.interpolate import PchipInterpolator

    arr = {k: np.array([float(v) for v in str(c[k]).split(":")]) for k in FUSE_KEYS}
    f = lambda xk, vk: PchipInterpolator(arr[xk], arr[vk], extrapolate=True)
    x0 = min(arr["top_x"][0], arr["side_x"][0], arr["bottom_x"][0])
    x1 = max(arr["top_x"][-1], arr["side_x"][-1], arr["bottom_x"][-1])
    xs = x0 + (x1 - x0) * 0.5 * (1 - np.cos(np.linspace(0, np.pi, 40)))
    zt, zb = f("top_x", "top_z")(xs), f("bottom_x", "bottom_z")(xs)
    ys = np.abs(f("side_x", "side_y")(xs))
    xsecs = [asb.FuselageXSec(xyz_c=[x, 0, (a + b) / 2], width=2 * y, height=max(a - b, 0), shape=2.0)
             for x, a, b, y in zip(xs, zt, zb, ys)]
    return asb.Fuselage(name="Fuselage", xsecs=xsecs)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze(plane, main, mass, speed, altitude, x_cg):
    import aerosandbox as asb

    atmo = asb.Atmosphere(altitude=altitude)
    rho = float(atmo.density())
    W = mass * 9.81
    S, c, b = plane.s_ref, plane.c_ref, plane.b_ref

    alphas = np.linspace(-6, 20, 53)
    op = asb.OperatingPoint(atmosphere=atmo, velocity=speed, alpha=alphas)
    aero = asb.AeroBuildup(airplane=plane, op_point=op, xyz_ref=[x_cg, 0, 0]).run()
    CL, CD, Cm = (np.asarray(aero[k], float) for k in ("CL", "CD", "Cm"))
    LD = CL / CD

    lin = (alphas >= -2) & (alphas <= 4)
    CLa = np.polyfit(np.radians(alphas[lin]), CL[lin], 1)[0]
    Cma = np.polyfit(np.radians(alphas[lin]), Cm[lin], 1)[0]
    i_max = int(np.argmax(CL))
    i_ld = int(np.argmax(LD))
    x_np = x_cg - Cma / CLa * c

    q = 0.5 * rho * speed ** 2
    CL_cruise = W / (q * S)
    up = slice(0, i_max + 1)  # pre-stall branch for interpolation
    a_cruise = float(np.interp(CL_cruise, CL[up], alphas[up]))
    CD_cruise = float(np.interp(a_cruise, alphas, CD))
    D_cruise = CD_cruise * q * S

    res = {
        "S_ref_m2": S, "span_m": b, "MAC_m": c, "aspect_ratio": b ** 2 / S,
        "mass_kg": mass, "speed_mps": speed, "altitude_m": altitude, "x_cg_m": x_cg,
        "CL_alpha_per_rad": CLa,
        "CD0": float(np.interp(0.0, CL[up], CD[up])),
        "CL_max": float(CL[i_max]), "alpha_CLmax_deg": float(alphas[i_max]),
        "LD_max": float(LD[i_ld]), "alpha_LDmax_deg": float(alphas[i_ld]),
        "V_best_LD_mps": math.sqrt(2 * W / (rho * S * CL[i_ld])),
        "V_stall_mps": math.sqrt(2 * W / (rho * S * CL[i_max])),
        "CL_cruise": CL_cruise, "alpha_cruise_deg": a_cruise, "CD_cruise": CD_cruise,
        "LD_cruise": CL_cruise / CD_cruise, "drag_cruise_N": D_cruise,
        "power_cruise_kW": D_cruise * speed / PROP_EFFICIENCY / 1000,
        "Cm_alpha_per_rad": Cma, "x_neutral_point_m": x_np,
        "static_margin_pct_MAC": 100 * (x_np - x_cg) / c,
    }
    polar = {"alpha": alphas, "CL": CL, "CD": CD, "Cm": Cm, "LD": LD}
    return res, polar


def plot(plane, res, polar, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    a = polar["alpha"]
    fig = plt.figure(figsize=(13, 8))
    ax = [fig.add_subplot(2, 3, i) for i in (1, 2, 4, 5)]
    ax[0].plot(a, polar["CL"]); ax[0].set(xlabel="alpha [deg]", ylabel="CL", title="Lift curve")
    ax[1].plot(polar["CD"], polar["CL"]); ax[1].set(xlabel="CD", ylabel="CL", title="Drag polar")
    ax[2].plot(a, polar["LD"]); ax[2].set(xlabel="alpha [deg]", ylabel="L/D", title="Lift-to-drag")
    ax[3].plot(a, polar["Cm"]); ax[3].set(xlabel="alpha [deg]", ylabel="Cm about CG", title="Pitching moment")
    ax[1].plot(res["CD_cruise"], res["CL_cruise"], "o", label="cruise"); ax[1].legend()
    for x in ax:
        x.grid(alpha=0.3)

    # Top and side views, to check the geometry came through correctly.
    for k, (i, j, title) in enumerate([(1, 0, "Top view"), (0, 2, "Side view")]):
        g = fig.add_subplot(2, 3, 3 + 3 * k)
        for w in plane.wings:
            le = np.array([xs.xyz_le for xs in w.xsecs])
            te = le + np.array([[xs.chord, 0, 0] for xs in w.xsecs])
            outline = np.vstack([le, te[::-1], le[:1]])
            for sgn in ([1, -1] if w.symmetric else [1]):
                pts = outline * [1, sgn, 1]
                g.plot(pts[:, i], pts[:, j], "b-")
        for f in plane.fuselages:
            xc = np.array([xs.xyz_c for xs in f.xsecs])
            if title == "Top view":
                w = np.array([xs.width / 2 for xs in f.xsecs])
                g.plot(xc[:, 1] + w, xc[:, 0], "k-", xc[:, 1] - w, xc[:, 0], "k-")
            else:
                h = np.array([xs.height / 2 for xs in f.xsecs])
                g.plot(xc[:, 0], xc[:, 2] + h, "k-", xc[:, 0], xc[:, 2] - h, "k-")
        if title == "Top view":
            g.plot(0, res["x_cg_m"], "ro", label="CG")
            g.plot(0, res["x_neutral_point_m"], "gx", label="neutral pt")
            g.invert_yaxis(); g.set(xlabel="y [m]", ylabel="x [m]"); g.legend(fontsize=8)
        else:
            g.set(xlabel="x [m]", ylabel="z [m]")
        g.set_aspect("equal"); g.set_title(title); g.grid(alpha=0.3)

    fig.suptitle(f"L/D max {res['LD_max']:.1f}   |   cruise L/D {res['LD_cruise']:.1f}   |   "
                 f"static margin {res['static_margin_pct_MAC']:.0f}% MAC")
    fig.tight_layout()
    fig.savefig(path, dpi=110)


# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="Quick aero estimates for the nTop Lesher Teal.",
                                epilog="Example: python teal_aero.py wing.span=8 hstab.chord=0.6 mass=520")
    p.add_argument("params", nargs="*", metavar="key=value",
                   help="geometry/flight values; anything left out keeps the Teal baseline")
    p.add_argument("--list", action="store_true", help="print every key with its baseline value")
    p.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "aero_results"),
                   help="output file prefix (default: aero_results next to this script)")
    p.add_argument("--csv", help="append one row of inputs+results to this CSV (for DOE)")
    p.add_argument("--no-plot", action="store_true")
    p.add_argument("--ntop", action="store_true",
                   help="quiet mode for nTop's Run Command block: prints only " + ",".join(NTOP_OUTPUTS))
    args = p.parse_args()

    if args.list:
        for k, v in BASELINE.items():
            print(f"{k}={v}")
        return

    params = parse_params(args.params)
    say = (lambda *a: None) if args.ntop else print  # keep stdout clean for nTop

    plane, main_wing, summary = build_airplane(params)
    say("\nGeometry:")
    for name, desc in summary:
        say(f"  {name:10s} {desc}")

    res, polar = analyze(plane, main_wing, float(params["mass"]), float(params["speed"]),
                         float(params["altitude"]), float(params["xcg"]))

    say("\nQuick aero estimate (AeroSandbox AeroBuildup):")
    fmt = {"S_ref_m2": "Wing area [m^2]", "span_m": "Span [m]", "aspect_ratio": "Aspect ratio",
           "MAC_m": "MAC [m]", "CL_alpha_per_rad": "CL_alpha [/rad]", "CD0": "CD0",
           "CL_max": "CL_max (rough)", "LD_max": "Max L/D", "alpha_LDmax_deg": "  at alpha [deg]",
           "V_best_LD_mps": "  at speed [m/s]", "V_stall_mps": "Stall speed [m/s] (rough)",
           "CL_cruise": "Cruise CL", "alpha_cruise_deg": "Cruise alpha [deg]",
           "LD_cruise": "Cruise L/D", "drag_cruise_N": "Cruise drag [N]",
           "power_cruise_kW": f"Cruise power [kW] (prop eff {PROP_EFFICIENCY})",
           "x_neutral_point_m": "Neutral point x [m]", "x_cg_m": "CG x [m]",
           "static_margin_pct_MAC": "Static margin [% MAC]"}
    for k, label in fmt.items():
        say(f"  {label:38s} {res[k]:10.4g}")

    with open(args.out + ".json", "w") as f:
        json.dump({"inputs": params, "results": res}, f, indent=2)
    if not args.no_plot:
        plot(plane, res, polar, args.out + ".png")
    if args.csv:
        row = {**{f"in:{k}": v for k, v in params.items()}, **res}
        new = not os.path.exists(args.csv)
        with open(args.csv, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(row))
            if new:
                w.writeheader()
            w.writerow(row)
    say(f"\nWrote {args.out}.json" + ("" if args.no_plot else f" and {args.out}.png") +
        (f", appended to {args.csv}" if args.csv else ""))
    if args.ntop:
        sys.stdout.write(",".join(f"{res[k]:.6g}" for k in NTOP_OUTPUTS))


if __name__ == "__main__":
    main()
