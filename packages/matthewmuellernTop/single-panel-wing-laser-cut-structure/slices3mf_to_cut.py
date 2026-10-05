#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["numpy"]
# ///
"""
Convert planar slice profiles stored in a 3MF file into flat SVG files for
laser cutting - one SVG per slice plane (or per part with --split-parts).

Supported 3MF content:
  * Beam-lattice extension (b:beamlattice) - beams chained into polylines
  * Slice extension (s:slicestack)         - polygons per slice height
  * Build-item / component transforms, multi-part (p:path) models, all units

Every group of coplanar loops is flattened into its own 2D frame at true size
(millimeters). Outer profiles are drawn red, holes blue, and any chain that
could not be closed green (check those before cutting).

Usage:
    python slices3mf_to_cut.py model.3mf                 # SVGs into ./model_svg/
    python slices3mf_to_cut.py model.3mf -o out/         # choose output folder
    python slices3mf_to_cut.py a.3mf b.3mf               # several files at once
    python slices3mf_to_cut.py model.3mf --split-parts   # one SVG per separate part
    python slices3mf_to_cut.py model.3mf --gap-tol 1.0   # close gaps up to 1 mm

Requires Python 3.8+ and numpy. With uv installed, `uv run slices3mf_to_cut.py
model.3mf` installs numpy automatically; otherwise run `pip install numpy`.
"""
import argparse
import collections
import math
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

try:
    import numpy as np
except ImportError:
    sys.exit("This script needs numpy. Install it with:  python -m pip install numpy\n"
             "(or run it with:  uv run slices3mf_to_cut.py <file.3mf>)")

UNIT_TO_MM = {
    "micron": 0.001, "millimeter": 1.0, "centimeter": 10.0,
    "inch": 25.4, "foot": 304.8, "meter": 1000.0,
}
ROOT_MODEL = "/3D/3dmodel.model"

COLOR = {"outer": "#ff0000", "inner": "#0000ff", "open": "#00aa00"}


def local(tag):
    return tag.rsplit("}", 1)[-1]


def attr(el, name, default=None):
    """Attribute lookup ignoring namespace prefix (e.g. p:path, s:slicestackid)."""
    for k, v in el.attrib.items():
        if local(k) == name:
            return v
    return default


def child(el, name):
    return next((c for c in el if local(c.tag) == name), None)


def children(el, name):
    return [c for c in el if local(c.tag) == name]


def parse_transform(s):
    """3MF 'm00 m01 m02 m10 ... m32' (row vectors) -> 4x4 matrix for column points."""
    M = np.eye(4)
    if s:
        v = [float(x) for x in s.split()]
        M[:3, :3] = np.array(v[:9]).reshape(3, 3).T
        M[:3, 3] = v[9:12]
    return M


def apply(M, P):
    return P @ M[:3, :3].T + M[:3, 3]


# ----------------------------------------------------------------------------
# 3MF reading
# ----------------------------------------------------------------------------
class Package:
    def __init__(self, path):
        if not os.path.isfile(path):
            sys.exit(f"Input file not found: {path}")
        try:
            self.zip = zipfile.ZipFile(path)
        except zipfile.BadZipFile:
            sys.exit(f"Not a valid 3MF (zip) file: {path}")
        self.names = {"/" + n.lstrip("/"): n for n in self.zip.namelist()}
        self.models = {}
        self.root_path = self._find_root()

    def _find_root(self):
        rels = self.names.get("/_rels/.rels")
        if rels:
            for r in ET.fromstring(self.zip.read(rels)).iter():
                if local(r.tag) == "Relationship" and r.get("Type", "").endswith("/3dmodel"):
                    return "/" + r.get("Target").lstrip("/")
        if ROOT_MODEL in self.names:
            return ROOT_MODEL
        models = [n for n in self.names if n.lower().endswith(".model")]
        if not models:
            sys.exit("No .model part found in 3MF")
        return models[0]

    def model(self, path):
        if path not in self.models:
            key = self.names.get(path) or next(
                (v for k, v in self.names.items() if k.lower() == path.lower()), None)
            if key is None:
                sys.exit(f"3MF references missing part {path}")
            root = ET.fromstring(self.zip.read(key))
            res = child(root, "resources")
            res = res if res is not None else root
            self.models[path] = {
                "root": root,
                "scale": UNIT_TO_MM.get(root.get("unit", "millimeter"), 1.0),
                "objects": {o.get("id"): o for o in children(res, "object")},
                "slicestacks": {s.get("id"): s for s in children(res, "slicestack")},
            }
        return self.models[path]


def beams_of(obj):
    """Return (Nx3 vertices, [(v1, v2)]) of an object's mesh/beam lattice."""
    mesh = child(obj, "mesh")
    if mesh is None:
        return None, []
    vs = child(mesh, "vertices")
    V = np.array([(float(v.get("x")), float(v.get("y")), float(v.get("z")))
                  for v in (children(vs, "vertex") if vs is not None else [])]).reshape(-1, 3)
    edges = []
    for bl in mesh.iter():
        if local(bl.tag) == "beam":
            edges.append((int(bl.get("v1")), int(bl.get("v2"))))
    return V, edges


def slices_of(pkg, mpath, ssid, depth=0):
    """Yield (Nx3 points in mm, closed) from a slicestack, following slicerefs.

    Points are scaled by the unit of the model part that holds the slicestack,
    which can differ from the referencing object's part.
    """
    m = pkg.model(mpath)
    ss = m["slicestacks"].get(ssid)
    if ss is None or depth > 8:
        return
    for sl in children(ss, "slice"):
        z = float(sl.get("ztop"))
        vs = child(sl, "vertices")
        v2 = [(float(v.get("x")), float(v.get("y"))) for v in (children(vs, "vertex") if vs is not None else [])]
        for poly in children(sl, "polygon"):
            idx = [int(poly.get("startv"))] + [int(s.get("v2")) for s in children(poly, "segment")]
            pts = np.array([(v2[i][0], v2[i][1], z) for i in idx]) * m["scale"]
            closed = len(idx) > 2 and idx[0] == idx[-1]
            yield (pts[:-1] if closed else pts), closed
    for ref in children(ss, "sliceref"):
        p = attr(ref, "slicepath") or mpath
        yield from slices_of(pkg, p, ref.get("slicestackid"), depth + 1)


def collect_polylines(pkg):
    """Walk the build tree and return world-space polylines in mm."""
    out = []

    def visit(mpath, oid, M, depth=0):
        m = pkg.model(mpath)
        obj = m["objects"].get(oid)
        if obj is None or depth > 16:
            return
        comps = child(obj, "components")
        if comps is not None:
            for c in children(comps, "component"):
                visit(attr(c, "path") or mpath, c.get("objectid"),
                      M @ parse_transform(c.get("transform")), depth + 1)
        V, edges = beams_of(obj)
        if edges:
            out.extend(chain_edges(apply(M, V) * m["scale"], edges))
        ssid = attr(obj, "slicestackid")
        if ssid:
            for pts, closed in slices_of(pkg, mpath, ssid):
                # Transforms are in model units; translation is scaled with the points.
                S = M.copy()
                S[:3, 3] *= m["scale"]
                out.append((apply(S, pts), closed))

    root = pkg.model(pkg.root_path)
    build = child(root["root"], "build")
    items = children(build, "item") if build is not None else []
    if items:
        for it in items:
            visit(attr(it, "path") or pkg.root_path, it.get("objectid"), parse_transform(it.get("transform")))
    else:  # no build section: take every object
        for oid in root["objects"]:
            visit(pkg.root_path, oid, np.eye(4))
    return out


# ----------------------------------------------------------------------------
# Geometry
# ----------------------------------------------------------------------------
def chain_edges(V, edges):
    """Walk an edge graph into polylines. Returns list of (points, closed)."""
    adj = collections.defaultdict(list)
    for a, b in edges:
        if a != b and 0 <= a < len(V) and 0 <= b < len(V):
            adj[a].append(b)
            adj[b].append(a)
    used = set()

    def ekey(a, b):
        return (a, b) if a < b else (b, a)

    def walk(start):
        path, cur = [start], start
        while True:
            nxt = next((n for n in adj[cur] if ekey(cur, n) not in used), None)
            if nxt is None:
                return path
            used.add(ekey(cur, nxt))
            path.append(nxt)
            cur = nxt
            if len(adj[cur]) != 2:      # stop at junctions / ends
                return path

    out = []
    # Start at ends / junctions first so open chains stay whole, then pure cycles.
    for s in [v for v in adj if len(adj[v]) != 2] + list(adj):
        while any(ekey(s, n) not in used for n in adj[s]):
            path = walk(s)
            closed = len(path) > 3 and path[0] == path[-1]
            out.append((V[path[:-1] if closed else path], closed))
    return out


def clean(pts, closed, eps):
    """Drop consecutive duplicate points."""
    keep = [pts[0]]
    for p in pts[1:]:
        if np.linalg.norm(p - keep[-1]) > eps:
            keep.append(p)
    if closed and len(keep) > 1 and np.linalg.norm(keep[0] - keep[-1]) <= eps:
        keep.pop()
    return np.array(keep)


def close_small_gaps(polylines, gap_tol):
    """Join open chains end-to-end and close chains whose ends nearly meet."""
    closed = [p for p in polylines if p[1]]
    open_ = [p[0] for p in polylines if not p[1]]
    while True:
        best = None  # (dist, i, j, flip_i, flip_j) or (dist, i, None) for self-close
        for i, a in enumerate(open_):
            if len(a) > 2:
                d = np.linalg.norm(a[0] - a[-1])
                if d <= gap_tol and (best is None or d < best[0]):
                    best = (d, i, None, False, False)
            for j in range(i + 1, len(open_)):
                b = open_[j]
                for fi in (False, True):
                    for fj in (False, True):
                        d = np.linalg.norm((a[0] if fi else a[-1]) - (b[-1] if fj else b[0]))
                        if d <= gap_tol and (best is None or d < best[0]):
                            best = (d, i, j, fi, fj)
        if best is None:
            break
        _, i, j, fi, fj = best
        if j is None:
            closed.append((open_.pop(i), True))
        else:
            a = open_[i][::-1] if fi else open_[i]
            b = open_[j][::-1] if fj else open_[j]
            open_[i] = np.vstack([a, b])
            open_.pop(j)
    return closed + [(p, False) for p in open_]


def fit_plane(P):
    m = P.mean(0)
    _, s, vt = np.linalg.svd(P - m, full_matrices=False)
    if len(s) < 3 or s[1] < 1e-9 * max(s[0], 1e-12):
        return None  # collinear / degenerate
    n = vt[2]
    if n[np.argmax(np.abs(n))] < 0:
        n = -n
    return n, float(n @ m), float(s[2] / math.sqrt(len(P)))


def group_by_plane(polylines, dist_tol, ang_tol_deg=0.5):
    groups = []  # [normal, offset, [polylines]]
    cos_tol = math.cos(math.radians(ang_tol_deg))
    for pts, closed in polylines:
        fit = fit_plane(pts)
        if fit is None:
            # straight segment: attach to any plane that contains it
            g = next((g for g in groups if np.all(np.abs(pts @ g[0] - g[1]) < dist_tol)), None)
            if g is None:
                print(f"  warning: skipping straight open chain of {len(pts)} pts (no plane)")
            else:
                g[2].append((pts, closed))
            continue
        n, d, resid = fit
        if resid > dist_tol:
            print(f"  warning: loop with {len(pts)} pts is not planar (rms {resid:.3f} mm)")
        for g in groups:
            if g[0] @ n > cos_tol and abs(g[1] - d) < dist_tol:
                g[2].append((pts, closed))
                break
        else:
            groups.append([n, d, [(pts, closed)]])
    return groups


def plane_frame(n):
    """In-plane axes (u, v); v follows global Z (else Y) so parts come out 'upright'."""
    for up in (np.array([0, 0, 1.0]), np.array([0, 1.0, 0]), np.array([1.0, 0, 0])):
        v = up - (up @ n) * n
        if np.linalg.norm(v) > 0.3:
            v /= np.linalg.norm(v)
            return np.cross(v, n), v
    raise ValueError("degenerate normal")


def plane_name(n, d):
    ax = int(np.argmax(np.abs(n)))
    if abs(n[ax]) > 0.9999:
        name = f"{'XYZ'[ax]}{d:.2f}"
    else:
        ang = math.degrees(math.acos(min(1.0, abs(n[ax]))))
        name = f"oblique{'XYZ'[ax]}_{ang:.1f}deg_d{d:.2f}"
    return name.replace("-", "m").replace(".", "p")


def signed_area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def point_in_poly(pt, poly):
    x, y = pt
    xs, ys = poly[:, 0], poly[:, 1]
    xn, yn = np.roll(xs, -1), np.roll(ys, -1)
    cond = (ys > y) != (yn > y)
    with np.errstate(divide="ignore", invalid="ignore"):
        xint = xs + (y - ys) * (xn - xs) / (yn - ys)
    return int(np.count_nonzero(cond & (x < xint))) % 2 == 1


def loop_inside(inner, outer):
    """Majority vote over a few sample points (robust to touching edges)."""
    idx = np.linspace(0, len(inner) - 1, min(len(inner), 7)).astype(int)
    return sum(point_in_poly(inner[i], outer) for i in idx) * 2 > len(idx)


def classify(loops2d):
    """Tag loops as outer/inner by nesting depth; return list of (pts, closed, kind, depth, parent)."""
    areas = [abs(signed_area(p)) if c and len(p) > 2 else 0.0 for p, c in loops2d]
    tagged = []
    for i, (p, c) in enumerate(loops2d):
        containers = [j for j, (q, cq) in enumerate(loops2d)
                      if j != i and cq and areas[j] > areas[i] and loop_inside(p, q)]
        depth = len(containers)
        parent = min(containers, key=lambda j: areas[j]) if containers else None
        kind = "open" if not c else ("outer" if depth % 2 == 0 else "inner")
        tagged.append((p, c, kind, depth, parent))
    return tagged


# ----------------------------------------------------------------------------
# SVG
# ----------------------------------------------------------------------------
def write_svg(path, loops, w, h, stroke_mm):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}mm" height="{h:.3f}mm" '
           f'viewBox="0 0 {w:.3f} {h:.3f}">']
    for kind in ("inner", "outer", "open"):          # holes first = safer cut order
        paths = [(p, c) for p, c, k in loops if k == kind]
        if not paths:
            continue
        out.append(f'  <g id="{kind}" fill="none" stroke="{COLOR[kind]}" stroke-width="{stroke_mm}">')
        for p, c in paths:
            d = "M" + " L".join(f"{x:.4f},{h - y:.4f}" for x, y in p) + (" Z" if c else "")
            out.append(f'    <path d="{d}"/>')
        out.append("  </g>")
    out.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


# ----------------------------------------------------------------------------
def convert(input_path, outdir=None, gap_tol=None, margin=2.0, split_parts=False,
            stroke_mm=0.1, quiet=False):
    log = (lambda *a: None) if quiet else print
    outdir = outdir or os.path.splitext(input_path)[0] + "_svg"
    base = os.path.splitext(os.path.basename(input_path))[0]

    polylines = collect_polylines(Package(input_path))
    polylines = [(p, c) for p, c in polylines if len(p) >= 2]
    if not polylines:
        sys.exit("No beam-lattice or slice-stack profiles found in this 3MF.")

    seg = np.concatenate([np.linalg.norm(np.diff(p, axis=0), axis=1) for p, _ in polylines])
    med = float(np.median(seg[seg > 0])) if np.any(seg > 0) else 1.0
    polylines = [(clean(p, c, med * 1e-3), c) for p, c in polylines]
    polylines = [(p, c and len(p) >= 3) for p, c in polylines if len(p) >= 2]

    gap_tol = gap_tol if gap_tol is not None else 3 * med
    n_open = sum(not c for _, c in polylines)
    polylines = close_small_gaps(polylines, gap_tol)
    n_left = sum(not c for _, c in polylines)
    log(f"{len(polylines)} loops; {n_open} open chains joined/closed with gap tol "
        f"{gap_tol:.3f} mm, {n_left} still open")

    span = float(np.ptp(np.vstack([p for p, _ in polylines]), axis=0).max())
    groups = group_by_plane(polylines, dist_tol=max(1e-3, 1e-5 * span, 0.05 * med))
    groups.sort(key=lambda g: (int(np.argmax(np.abs(g[0]))), tuple(np.round(g[0], 3)), g[1]))

    os.makedirs(outdir, exist_ok=True)
    written = []
    for gi, (n, d, pls) in enumerate(groups, 1):
        u, v = plane_frame(n)
        tagged = classify([(np.column_stack([p @ u, p @ v]), c) for p, c in pls])

        if split_parts:
            def owner(i):
                """Nearest enclosing outer profile of loop i (None if free-standing)."""
                p = tagged[i][4]
                while p is not None and tagged[p][2] != "outer":
                    p = tagged[p][4]
                return p

            parts = []
            for oi, t in enumerate(tagged):
                if t[2] == "open" and owner(oi) is None:
                    parts.append([t])
                elif t[2] == "outer":
                    parts.append([t] + [s for si, s in enumerate(tagged)
                                        if s[2] != "outer" and owner(si) == oi])
        else:
            parts = [tagged]

        pname = plane_name(n, d)
        for pi, part in enumerate(parts, 1):
            allp = np.vstack([t[0] for t in part])
            mn, mx = allp.min(0), allp.max(0)
            off = mn - margin
            w, h = (mx - mn) + 2 * margin
            stem = f"{base}_{gi:02d}_{pname}" + (f"_part{pi}" if len(parts) > 1 else "")
            fp = os.path.join(outdir, stem + ".svg")
            write_svg(fp, [(t[0] - off, t[1], t[2]) for t in part], w, h, stroke_mm)
            kinds = collections.Counter(t[2] for t in part)
            written.append({"file": fp, "size": (float(mx[0] - mn[0]), float(mx[1] - mn[1])),
                            "outer": kinds["outer"], "inner": kinds["inner"], "open": kinds["open"]})
            log(f"  {stem}.svg: {kinds['outer']} outer, {kinds['inner']} holes"
                + (f", {kinds['open']} OPEN (green)" if kinds["open"] else "")
                + f", {mx[0] - mn[0]:.1f} x {mx[1] - mn[1]:.1f} mm")
    log(f"Wrote {len(written)} SVG(s) to {outdir}")
    return written


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", metavar="input", help="input .3mf file(s)")
    ap.add_argument("-o", "--outdir", help="output folder (default: <input>_svg next to each input)")
    ap.add_argument("--gap-tol", type=float, default=None,
                    help="max gap (mm) to auto-close open chains (default: 3x median segment length)")
    ap.add_argument("--margin", type=float, default=2.0, help="margin around part in mm (default 2)")
    ap.add_argument("--stroke", type=float, default=0.1, help="stroke width in mm (default 0.1)")
    ap.add_argument("--split-parts", action="store_true",
                    help="write each separate outer profile (with its holes) as its own SVG")
    a = ap.parse_args()
    for path in a.inputs:
        if len(a.inputs) > 1:
            print(f"== {path}")
        convert(path, a.outdir, a.gap_tol, a.margin, a.split_parts, a.stroke)


if __name__ == "__main__":
    main()
