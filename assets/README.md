# Profile assets

The profile uses the current charcoal, amber-gold and warm ivory design.

- `identity/hero-gold.png`: approved tiger crest and world-map banner, used in both themes.
- `skills/toolchain-{dark,light}.svg`: engineering stack with animated signal lanes and selective border shines. `rocket.png` is a required generator input.
- `telemetry/pulse-52w-{dark,light}.svg`: engineering activity.
- `telemetry/domain-spectrum-{dark,light}.svg`: language footprint.
- `footer/`: current individually linked GitHub, LinkedIn and email SVGs.
- `../tools/skillicons_cache/`: source icons required to rebuild the engineering stack.
- `../generated/metrics.json`: generated telemetry snapshot.

## Regeneration

Run from the repository root with Python 3.11 or newer. No third-party Python packages are required.

```bash
python tools/build_all_skills_toolchain.py
python tools/update_all_telemetry.py
python tools/check_readme.py
```

The telemetry workflow refreshes the activity and language SVGs daily. The hero is a static PNG; changing it requires replacing the image and updating its README reference if the filename changes.

Only active artwork and generator inputs are retained in the working tree.
