# Profile assets

The profile uses the current charcoal, amber-gold and warm ivory design.

- `identity/hero-gold.png`: approved dark tiger crest and world-map banner. `identity/hero-gold-light.png` is its ivory and bronze light-mode counterpart.
- `skills/toolchain-{dark,light}.svg`: engineering stack with animated signal lanes and selective border shines. `rocket.png` is a required generator input.
- `telemetry/pulse-52w-{dark,light}.svg`: engineering activity.
- `telemetry/domain-spectrum-{dark,light}.svg`: language footprint.
- `footer/`: current individually linked GitHub, LinkedIn and email SVGs.
- `../tools/skillicons_cache/`: source icons required to rebuild the engineering stack.
- `../generated/metrics.json`: generated telemetry snapshot.

## Regeneration

Run from the repository root with Python 3.11 or newer. The stack and telemetry generators use the Python standard library. Pillow and NumPy are needed only for the light hero.

```bash
python tools/build_all_skills_toolchain.py
python tools/update_all_telemetry.py
python tools/check_readme.py
```

The telemetry workflow refreshes the activity and language SVGs daily. The dark hero is the original PNG. To rebuild the matching light hero, install Pillow and NumPy and run `python tools/build_light_hero.py`. Both theme assets are selected using `<picture>`.

Only active artwork and generator inputs are retained in the working tree.

The shared `tools/profile_design.py` module defines the 1120-unit card system, serif heading, semantic palette and common padding.
