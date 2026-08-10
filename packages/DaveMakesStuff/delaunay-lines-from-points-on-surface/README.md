# Delaunay Lines from Points on Surface

Create a network of Delaunay lines from points on a surface with an option to output full network or boundary only.

This block is useful in situations that require more control over the generation of Delaunay lines than would be possible with a mesh or re-mesh block. Best results are achieved using the "Spatial Weighting" option in the "Random Points on Mesh" block to generate input points.

This block is essentially outputting the dual of the "Voronoi Surface Lattice" block.

## Installation

Clone this repo or copy the package folder into your nTop workspace:

```bash
git clone https://github.com/nTopology/Utilities-community.git
```

The package lives at `packages/DaveMakesStuff/delaunay-lines-from-points-on-surface/`.

## Usage

1. Open the provided `.ntop` file in nTop 4.26+.
2. Input a "Mesh Surface" and a list of "Points" positioned on that surface
3. Select whether to output the full network or boundary lines only.

## Inputs & outputs

| Name | Type | Notes |
|------|------|-------|
| Points | Point list| Points to use when generating Daluanay lines |
| Mesh Surface | Mesh | Surface on which to generate Delaunay lines |
| Output | Choice | Select full network or boundary lines only |
| Delaunay Lines | Line list | Main output |

## License

MIT.
