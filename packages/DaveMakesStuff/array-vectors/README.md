# Array Vectors

Use this block in conjunction with the "Translate Object" or "Translation Transform" blocks to create a three-dimensional array of any object.

## Installation

Clone this repo or copy the package folder into your nTop workspace:

```bash
git clone https://github.com/nTopology/Utilities.git
```

The package lives at `packages/DaveMakesStuff/array-vectors/`.

## Usage

1. Open the provided `.ntop` file in nTop 4.12+.
2. Open a "Translate Object" or "Translation Transform" block and input the object you wish to array.
3. Input array parameters into "Array Vector" block
3. Drag and drop "Array Vector" block into above "Translate Object" or "Translation Transform" block

## Inputs & outputs

| Name | Type | Notes |
|------|------|-------|
| `Count` | Scalar Body | Determines the number of items across three dimensions |
| `Spacing` | Scalar Body | Determines the spacing of items across three dimensions |
| `Center` | Bool | Option to center arrayed objects around origin |
| `Output Vectors` | Vector List | Main result |

## License

MIT.
