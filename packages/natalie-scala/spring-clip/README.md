# Serpent Spring Clip

This block creates a customizable serpentine spring clip with a toggle and retractable tongue, driven by inputs like Bend Radius, Unit Count, Spring Thickness, Spring Width, and the Tongue and Toggle dimensions.

The block produces a single implicit body of the clip. It can be permanently attached to or integrated into a larger Object A (e.g. an access panel) by its frame, while its tongue temporarily snaps into a recess in Object B (e.g. a fuselage) to lock the assembly in place.

## Installation

Clone this repo or copy the package folder into your nTop workspace:

```bash
git clone https://github.com/nTopology/Utilities-community.git
```

The package lives at `packages/natalie-scala/spring-clip/`.

## Usage

1. Open the provided `.ntop` file in nTop 4.12+.
2. Set the spring geometry inputs (Bend Radius, Unit Count, Spring Thickness, Spring Width) to size the clip's compressibility and length.
3. Set the Tongue and Toggle dimensions to fit the alignment hole in Object B and for ergonomic actuation.
4. Attach the resulting body's frame to Object A; the tongue snaps into a recess in Object B to lock the assembly.

## Components

| Component | Description |
|-----------|-------------|
| Spring | The serpentine (zig-zag) portion that compresses for clip actuation |
| Tongue | The extension at the end of the spring that interfaces with the alignment hole in Object B |
| Toggle | The protruding tab used to manually compress the spring and retract the tongue |
| Frame | The outer border that integrates the clip into Object A |

## Inputs & outputs

| Name | Notes |
|------|-------|
| `Bend Radius` | Radius of the spring arcs — impacts spring length and compressibility. |
| `Unit Count` | Number of complete snaking units in the spring (one direction plus its return) — impacts spring length and compressibility. |
| `Spring Thickness` | Diameter of the serpentine spring — impacts compressibility. |
| `Spring Width` | Length of the straightaways of the spring — impacts dimensions and compressibility. |
| `Tongue Length` | Total length of the tongue geometry. Not accurate to how much it actually protrudes from the frame — check the "True Tongue Protrusion" variable at the bottom of the custom block for that. |
| `Tongue Width` / `Tongue Thickness` | Dimension and strength considerations for latching engagement. |
| `Toggle Length` / `Toggle Width` / `Toggle Height` | Sizing for user ergonomics. |
| Output | Main result — a single implicit body of the clip. |

## License

MIT.
