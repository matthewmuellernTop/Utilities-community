# Fuselage from Rails

Create a fuselage from three rails using a conic section sweep by tangents, controlling rho values and close radii for tip and tail.

## Installation

Clone this repo or copy the package folder into your nTop workspace:

```bash
git clone https://github.com/nTopology/Utilities-community.git
```

The package lives at `packages/matthewmuellernTop/fuselage-from-rails/`.

## Usage

1. Open the provided `.ntop` file in nTop 6.0+.
2. Connect your input geometry / fields to the exposed inlets.
3. Tune parameters. Export via the standard nTop exporters.

## Inputs & outputs

| Name | Type | Notes |
|------|------|-------|
| `input_1` | Body | Required. |
| `output_1` | Implicit Body | Main result. |

## License

MIT.
