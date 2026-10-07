# Publication record

Package: `matthewmuellernTop/lesher-teal-hackathon-starter` 1.0.1, prepared 2026-10-07 (1.0.0 prepared 2026-10-06).

## Source

- Source notebook (saved 2026-10-06 16:24): SHA-256 `e990373c82699405d7846951ab89392c6069e51da88aedf6c208274309e0a3bf`

## Published files

| File | Bytes | SHA-256 |
|---|---|---|
| `LICENSE` | 1075 | `6c0df087d26fb6ac0c06b3dc7b6488d7fa6f49bd87bcfcd1bcd00ead84adc4eb` |
| `README.md` | 6242 | `eee62a0c548a7c30e39ee3e28ab2ae4980ba4a27d9f4fef2ef96a07b43793cb5` |
| `aero-output-example.png` | 110669 | `4285643a13f9f23d019dc95cd5ddd2f6364f98ecf0864b712176800c3cab0f0e` |
| `cover.png` | 299994 | `56612e9e3f490ab31d7d7c98d1d90813ed4113ab695befcf828538402446d8aa` |
| `lesher-teal-hackathon-starter.ntop` | 2321716 | `57fe3b2527f4f66cbb9518269eff86f7ded24cb2e138a9424786f6d9e143a08e` |
| `manifest.json` | 799 | `3f021569a33cabceb166c7137b110722c09fd453cf13466634f327435c47035d` |
| `requirements.txt` | 17 | `edc84a836b67546af019cc82546366ab0ea10c84f76c057e5a72cb36e368416e` |
| `teal_aero.py` | 16189 | `086b256143d8eac6c5e085c79bb47e3ac414beb2948e11dac4e66c2f9285b704` |
| `lesher-teal-hackathon-starter.zip` | 358087 | `4c02312659e1d8e00f99a2a1732c94c2d3a01139e60689c790d4cf001b496cbb` |

## 1.0.1 changes

- `packageFile` now points at `lesher-teal-hackathon-starter.zip` (the `.ntop`, `teal_aero.py`, `requirements.txt`, `README.md` and `LICENSE`), so the site download includes the Python script.
- README Files section updated to describe the zip. Notebook and script are unchanged from 1.0.0.

## Changes from the source notebook

- Notebook description: two reference images of unknown license replaced with a CC BY-SA 3.0 Wikimedia Commons photo (credited) and setup text.
- `Aero Tool Folder` set from a personal path to `C:/TealAero`; the Run Command result was refreshed from that folder.
- Flow analysis left paused with no cached results.
- Everything else unchanged (made through the nTop console, then saved as a separate copy).

## Checks

- Byte scan of the published notebook: no user names, home-directory paths or email addresses; old description images absent.
- Run Command chain evaluated in nTop build 43139 with the published settings: cruise CL 0.2145, L/D 14.17, neutral point 2.753 m.
- `teal_aero.py` baseline run from a terminal gives the same values.
- Manifest checked against `packages/_schema/manifest.schema.json` with an equivalent Python check (Node wasn't available locally); CI runs the official validator.
- Not done: reopening this copy in a public nTop 6.2 release.
