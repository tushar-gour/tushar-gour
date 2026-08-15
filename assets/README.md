# Asset system

This profile uses a deliberately small asset surface.

- `identity/` contains editable SVG source plus committed light/dark PNG renders selected through `<picture>` and `prefers-color-scheme`.
- `motif/` contains four SVG source phases of **The Fifth Mark** plus committed PNG renders. The first four ticks stay fixed while the fifth resolves into alignment as the reader moves down the profile.
- `motion/` contains two tiny GIFs. They are ornamental, slow, and non-essential to understanding the README.

## Why the README embeds PNG, not SVG

GitHub can display SVG, but GitHub's current documentation notes that SVGs may not render in Firefox and that SVG inline scripting/animation is unsupported. The profile therefore keeps SVG as the editable source format and embeds deterministic PNG renders for the identity and divider artwork. Motion uses committed GIFs, which GitHub explicitly supports.

## Palette

- Warm paper: `#F7F4EE`
- Charcoal: `#151816`
- Ink: `#202320`
- Quiet neutral: `#8C918A`
- Signature terracotta: `#BE6848` (light) / `#D98362` (dark hero)

The accent is intentionally warm rather than neon or blue-purple: it adds human optimism to an otherwise precise neutral system.

## Rebuilding assets

```bash
python -m pip install -r requirements-dev.txt
python tools/render_static.py
python tools/render_motion.py
```

Generated assets are committed so the profile has no runtime dependency on third-party badge, stats, or animation services.
