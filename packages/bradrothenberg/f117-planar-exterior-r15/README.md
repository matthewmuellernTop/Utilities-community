# F-117 R15: editable planar exterior

**Built with Astra.**

Study native planar solids and integrated inlet transitions in an editable F-117 appearance reconstruction.

![F-117 R15: editable planar exterior](cover.png)

R15 joins the retained inlet planes to the fuselage with shared planar regions. The recorded notebook has 61 field checks. Hidden surfaces and transition details are inferred. The original 99 percent reference-fit target remains unmet.

## Installation and use

1. Download the package files and keep them together.
2. Open `f117-planar-exterior-r15.ntop` in the matching licensed nTop build.
3. Save a working copy before editing. Expand the relevant section and change one control at a time.
4. Inspect the rebuilt bodies and block states before accepting the changed model.

Recorded native build: **6.0.0-rc 42594**. The catalogue version field cannot encode the custom build number. Public release compatibility has not been re-tested. The application and license are not included.

## Inputs and outputs

| Direction | Contents |
|---|---|
| Input | Named planar vertices, cuts and feature controls |
| Output | Separate colored native exterior bodies |

Named scalar controls include `Published length`, `Published wingspan`, `CHECK body inside`, `CHECK nose outside`, `CHECK wing inside`, `CHECK above body`, `CHECK full model inside`, `VERIFY Right grille bar`, `VERIFY Right grille hole`, `VERIFY Right clear aperture`, `VERIFY Left grille bar`, `VERIFY Left grille hole`. Some are computed values; inspect their upstream construction before changing them.

## Files

- [f117-planar-exterior-r15.ntop](f117-planar-exterior-r15.ntop)

## Evidence and source

Publication checks are offline: native-container round trips, export-path changes, collapsed presentation, dependency inspection, and binary payload preservation. These checks do not constitute new native execution. See [publication-checks.json](publication-checks.json).

## License

MIT. See [LICENSE](LICENSE). This license covers the original example models, saved recipes, and supporting material in this package.
