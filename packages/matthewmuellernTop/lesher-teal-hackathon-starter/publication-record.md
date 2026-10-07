# Publication record

Package: `matthewmuellernTop/lesher-teal-hackathon-starter` 1.1.0, prepared 2026-10-07 (1.0.1 prepared 2026-10-07, 1.0.0 prepared 2026-10-06).

## Source

- 1.1.0 notebook (saved 2026-10-07 16:43): published as-is, SHA-256 `1cdb66b990361baab88b4f63f7baa9391e9f8c77849763e821556ad7912fa75f`
- 1.0.x source notebook (saved 2026-10-06 16:24): SHA-256 `e990373c82699405d7846951ab89392c6069e51da88aedf6c208274309e0a3bf`

## Published files

| File | Bytes | SHA-256 |
|---|---|---|
| `LICENSE` | 1075 | `6c0df087d26fb6ac0c06b3dc7b6488d7fa6f49bd87bcfcd1bcd00ead84adc4eb` |
| `README.md` | 6582 | `b3b4d824fa3af2bd71b6c2a1ed0531fe7203efb22b8846603f313c44013c597e` |
| `aero-output-example.png` | 110669 | `4285643a13f9f23d019dc95cd5ddd2f6364f98ecf0864b712176800c3cab0f0e` |
| `cover.png` | 299994 | `56612e9e3f490ab31d7d7c98d1d90813ed4113ab695befcf828538402446d8aa` |
| `lesher-teal-hackathon-starter.ntop` | 6770502 | `1cdb66b990361baab88b4f63f7baa9391e9f8c77849763e821556ad7912fa75f` |
| `manifest.json` | 780 | `401d3e8b96dbb4dcbf11359d6bd8312d0a5a53a73c0520e828ee6a249afc0d93` |
| `requirements.txt` | 17 | `edc84a836b67546af019cc82546366ab0ea10c84f76c057e5a72cb36e368416e` |
| `teal_aero.py` | 16189 | `086b256143d8eac6c5e085c79bb47e3ac414beb2948e11dac4e66c2f9285b704` |
| `lesher-teal-hackathon-starter.zip` | 860068 | `d9bab58c9ade8553a1f483adf05e3e3fc1301dd452b07a0ce74e9f7013f8bd19` |

## 1.1.0 changes

- New **Mass Estimate** section: named mass (kg) and location (m) variables for payload (95 kg), engine (105 kg), structures (220 kg) and fuel (80 kg), totalling the 500 kg max takeoff weight. They are rough engineering estimates, not Teal data.
- The **CB - Group Weight Statement** custom block (Raymer table 15.1) turns them into `Total Mass` and `Mass Statement CG`, which now drive `Aircraft Mass` and `CG X` in the Quick Aero Estimate section instead of typed values.
- README "Using it" section and table describe the new inputs. The zip was rebuilt with the new notebook and README. `teal_aero.py` is unchanged.
- The notebook grew from 2.3 MB to 6.8 MB. The flow analysis is still paused with no cached results.

## 1.0.1 changes

- `packageFile` now points at `lesher-teal-hackathon-starter.zip` (the `.ntop`, `teal_aero.py`, `requirements.txt`, `README.md` and `LICENSE`), so the site download includes the Python script.
- README Files section updated to describe the zip. Notebook and script are unchanged from 1.0.0.

## Changes from the source notebook

- Notebook description: two reference images of unknown license replaced with a CC BY-SA 3.0 Wikimedia Commons photo (credited) and setup text.
- `Aero Tool Folder` set from a personal path to `C:/TealAero`; the Run Command result was refreshed from that folder.
- Flow analysis left paused with no cached results.
- Everything else unchanged (made through the nTop console, then saved as a separate copy).

## Checks

- 1.1.0 byte scan of the published notebook: no user names, home-directory paths or email addresses; `Aero Tool Folder` is `C:/TealAero`.
- 1.1.0 Run Command chain evaluated in the internal nTop build with the published settings (total mass 500 kg, CG X 2.720 m): cruise CL 0.2145, L/D 14.17, neutral point 2.753 m, static margin +4.2 % MAC.
- 1.1.0 zip contents checked byte-for-byte against the package files.
- Byte scan of the published notebook: no user names, home-directory paths or email addresses; old description images absent.
- Run Command chain evaluated in nTop build 43139 with the published settings: cruise CL 0.2145, L/D 14.17, neutral point 2.753 m.
- `teal_aero.py` baseline run from a terminal gives the same values.
- Manifest checked against `packages/_schema/manifest.schema.json` with an equivalent Python check (Node wasn't available locally); CI runs the official validator.
- Not done: reopening this copy in a public nTop 6.2 release.
