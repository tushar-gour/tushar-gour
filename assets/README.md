# Profile assets

The profile uses the current charcoal, amber-gold and warm ivory design.

- `identity/hero-gold.png`: approved dark tiger crest and world-map banner. `identity/hero-gold-light.png` is its ivory and bronze light-mode counterpart.
- `skills/toolchain-{dark,light}.svg`: engineering stack with animated signal lanes and selective border shines. `rocket.png` is a required generator input.
- `telemetry/pulse-52w-{dark,light}.svg`: engineering activity.
- `telemetry/domain-spectrum-{dark,light}.svg`: language footprint.
- `section-gap.svg`: shared transparent spacing between all five profile sections.
- `footer/`: four lossless embedded PNG slices of the approved 2172 × 724 dark contact banner, plus a matching light-palette adaptation, wrapped in SVGs with a continuous rounded outer frame. Each slice is independently linked. The frame matches the shared 1120-unit card design (14-unit radius, 1.2-unit stroke). No duplicate artwork is retained.
- `../tools/skillicons_cache/`: source icons required to rebuild the engineering stack.
- `../generated/metrics.json`: generated telemetry snapshot.

## Regeneration

Run from the repository root with Python 3.11 or newer. The stack and telemetry generators use the Python standard library. Pillow and NumPy are needed only for the light hero.

```bash
python tools/build_all_skills_toolchain.py
python tools/update_all_telemetry.py
python tools/check_readme.py
```

The telemetry workflow refreshes the activity and language SVGs every two hours. The hero PNGs use the same exact 1978 × 600 crop, with no outer image margins. To rebuild the matching light hero, install Pillow and NumPy and run `python tools/build_light_hero.py`. Both theme assets are selected using `<picture>`.

Only active artwork and generator inputs are retained in the working tree.

The shared `tools/profile_design.py` module defines the 1120-unit card system, serif heading, semantic palette and common padding.

Repository totals: add an owner-authorized classic PAT with `repo` scope as the Actions secret `PROFILE_READ_TOKEN`. The pipeline reads the authenticated owner's public/private totals. Without this secret (or on error), it keeps the last verified count and explicitly labels it as such. Never commit the token to the repository.

Language footprint uses an adjusted public-repository estimate: the TypeScript display bucket is the larger of aggregate JavaScript and TypeScript bytes, not their sum. This is a heuristic to reduce possible compiled-JavaScript duplication, not an exact source-code measurement. All other language byte counts remain unchanged and percentages are normalized against the adjusted total. The manifest retains both raw byte totals.
