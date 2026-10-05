# Pilatus PC-12 Parametric Airplane

A fully parametric model of the Pilatus PC-12, a civilian turboprop utility aircraft. Eight exposed inputs drive the wing design and are the variable set intended for parametric sweeps and nTopCL automation (profile, span, chord, sweep, taper, dihedral, and wing position); everything else in the notebook is derived from them or held constant.

## Installation

Clone this repo or copy the package folder into your nTop workspace:

```bash
git clone https://github.com/nTopology/Utilities-community.git
```

The package lives at `packages/orcunbulat/pilatus-pc-12-parametric-airplane/`.

## Usage

1. Open the provided `.ntop` file in nTop 5.53+.
2. Connect your input geometry / fields to the exposed inlets.
3. Tune parameters. Export via the standard nTop exporters.

## Inputs

- **Root Chord** — Wing chord at the fuselage centerline. Together with span and the taper ratios it sets wing area (PC-12 reference area 25.81 m²).
- **Wing Span** — Full span, tip to tip. The wing CB receives half of this per side; with winglets enabled, the span-compensation formula keeps this value exact.
- **NACA Code** — The PC-12 uses the NASA/Langley low-speed series (GA(W)-1 derivatives): LS(1)-0417MOD at the root and LS(1)-0313 at the tip (17% and 13% thick respectively), blended along the span. NACA 2417 is selected as the closest match.
- **Taper Ratio Inner** — Chord reduction across the inner panel. PC-12: constant chord inboard (1.0).
- **QC Angle Inner** — Sweep at the quarter-chord line of the inner panel; positive sweeps back. The PC-12 is essentially unswept — the visible leading-edge sweep comes from taper alone.
- **Dihedral Angle** — Upward V-angle of the wing for roll stability. PC-12 reference ≈ 5°.
- **Wings Root Height** — Vertical position of the wing root; negative places the wing low on the fuselage (the PC-12 is a low-wing aircraft).
- **Wing Root X** — Longitudinal station of the wing root leading edge. Tie to Aircraft Length so the wing keeps its position on stretched variants.

## Output

- **Multi Region Mesh** — the assembled implicit geometry meshed via `multi_region_mesh_from_implicit`.

## License

MIT.
