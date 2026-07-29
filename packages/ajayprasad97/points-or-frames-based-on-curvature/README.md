# Points or Frames based on Curvature

Generates a set of points (and matching reference frames) distributed non-uniformly along a spline, packing more points into high-curvature regions and fewer into flat/straight regions.

## Why not just space points evenly?

Evenly-spaced points either waste density on straight sections or under-resolve sharp bends. This block instead builds a curvature-weighted arc-length reparameterization, so point density tracks local geometric complexity.

## How it works

1. Sample curvature densely along the curve (step size = `Increment`).
2. Convert curvature into a weight list (higher curvature → higher weight, with a floor so flat regions still get some density).
3. Build a running total of the weights — a discrete integral.
4. Normalize that into a monotonic 0→1 curve — effectively a CDF (cumulative distribution function) over arc length, weighted by curvature.
5. Pick `Target Points` evenly-spaced levels in that 0→1 range.
6. For each level, invert the CDF to find the actual arc-length distance it corresponds to.
7. Evaluate the curve at each resulting distance to get the final point/frame outputs.

## Installation

Clone this repo or copy the package folder into your nTop workspace:

```bash
git clone https://github.com/nTopology/Utilities-community.git
```

The package lives at `packages/ajayprasad97/points-or-frames-based-on-curvature/`.

## Usage

1. Open the provided `.ntop` file in nTop 5.47+.
2. Input a spline.
3. Set `Target Points` to the total number of points/frames to generate.

## Inputs & outputs

| Name | Type | Notes |
|------|------|-------|
| `Spline` | Spline | The curve to distribute points along. Any degree, open or closed. |
| `Target Points` | Integer | Total number of output points/frames. Distributed non-uniformly by curvature, not spread evenly. Default: 50. |
| `Point` | Point List | Output points, dense at high curvature. |
| `Frame` | Frame List | Local coordinate frames at those same points, useful for sweeps, cross-sections, or lattice orientation. |

## Tuning

- `Increment`: controls sampling resolution of the underlying curvature scan. Smaller = more accurate but slower. Should scale with curve length rather than staying a fixed absolute value.
- The internal weight ramp (currently 0.2 → 1.0) controls how aggressively curvature pulls in extra points vs. how much minimum density flat sections retain. Raise the floor for more even coverage; lower it for more aggressive clustering at bends.

## Known limitations

- Very short or near-straight curves may need a smaller `Increment` to resolve curvature accurately.
- Cumulative sum is computed with an O(n²) custom block, fine at the ~400-500 sample counts used by default; revisit if curvature sampling resolution grows much finer.

## License

MIT.
