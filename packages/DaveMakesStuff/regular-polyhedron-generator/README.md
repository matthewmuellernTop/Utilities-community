# Regular Polyhedron Generator

Generate the five platonic polyhedra (tetrahedron, cube, octahedron, icosahedron, dodecahedron) with options to create uniform truncated, rectified, omnitruncated or custom versions. 

[Watch the Tutorial Video](https://youtu.be/fglKoqLZsY0)

To create a mesh, drag and drop the graph vertices into the "Delaunay Volume Mesh" block.

To create an implicit, drag and drop the mesh into the “Implicit Body from Mesh” block.


## Installation

Clone this repo or copy the package folder into your nTop workspace:

```bash
git clone https://github.com/nTopology/Utilities-community.git
```

The package lives at `packages/DaveMakesStuff/regular-polyhedron-generator/`.

## Usage

1. Open the provided `.ntop` file in nTop 4.26+.
2. Select base Platonic polyhedron and radius
3. Select modifications to be performed

## Inputs & outputs

| Name | Type | Notes |
|------|------|-------|
| `Base Polyhedron` | Choice | Select base polyhedron (tetrahedron, cube, octahedron, icosahedron, dodecahedron) |
| `Radius` | Scalar Value| Radius of polyhedron |
| `Modify` | Choice | Select from a series of geometric modifications to be performed on the base polyhedron (uniform truncated, rectified, omnitruncated or custom) |
| `u` | Scalar Value | An input value to use when "Custom" is selected as a "Modify" choice |
| `v` | Scalar Value | An input value to use when "Custom" is selected as a "Modify" choice |
| `Regular Polyhedron` | Graph | Main output |

## License

MIT.
