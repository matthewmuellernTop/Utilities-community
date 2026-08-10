# Snub Polyhedron Generator

Generate a Snub Cuboctahedron or Snub Icosidodecahedron with an option to select right or left chirality. 

[Watch the Tutorial Video](https://youtu.be/fglKoqLZsY0)

To create a mesh, drag and drop the graph vertices into the "Delaunay Volume Mesh" block.

To create an implicit, drag and drop the mesh into the “Implicit Body from Mesh” block.


## Installation

Clone this repo or copy the package folder into your nTop workspace:

```bash
git clone https://github.com/nTopology/Utilities-community.git
```

The package lives at `packages/DaveMakesStuff/snub-polyhedron-generator/`.

## Usage

1. Open the provided `.ntop` file in nTop 4.26+.
2. Select shape, chirality and radius


## Inputs & outputs

| Name | Type | Notes |
|------|------|-------|
| `Shape` | Choice | Select Snub Shape |
| `Chirality` | Choice | Select right or left orientation |
| `Radius` | Scalar value | Radius of polyhedron |
| `Snub Polyhedron` | Graph | Main output |

## License

MIT.
