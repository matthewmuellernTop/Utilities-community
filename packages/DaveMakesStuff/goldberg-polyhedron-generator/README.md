# Goldberg Polyhedron Generator

Generate a Goldberg polyhedron using inputs m and n to modify the number and orientation of faces.

[Watch the Tutorial Video](https://youtu.be/fglKoqLZsY0)

To create a mesh, drag and drop the graph vertices into the "Delaunay Volume Mesh" block.

To create an implicit, drag and drop the mesh into the “Implicit Body from Mesh” block.


## Installation

Clone this repo or copy the package folder into your nTop workspace:

```bash
git clone https://github.com/nTopology/Utilities-community.git
```

The package lives at `packages/DaveMakesStuff/goldberg-polyhedron-generator/`.

## Usage

1. Open the provided `.ntop` file in nTop 4.26+.
2. Input values for radius, m, and n variables.
3. Select "Icosahedral" or "spherical" output

## Inputs & outputs

| Name | Type | Notes |
|------|------|-------|
| `Radius` | Scalar value | Radius of polyhedron |
| `m` | Integer value | Defines the number and orientation of faces | 
| `n` | Integer value | Defines the number and orientation of faces | 
| `Cage Type` | Choice | Select "Icosahedral" or "spherical" output |
| `Goldberg Polyhedron` | Graph | Main result |

## License

MIT.
