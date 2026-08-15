# Asset system

This profile uses a deliberately small asset surface.
All committed binary assets are generated from source — no third-party services.

## Directory map

- `identity/` — editable SVG source for the hero panel + committed PNG renders.
  Light and dark variants, selected via `<picture>` and `prefers-color-scheme`.

- `motif/` — four SVG phase dividers + committed PNG renders.
  Together they form the **Signal / Resolve** arc: the accent mark is displaced
  in Phase 01 and settles to exact alignment by Phase 04.

- `motion/` — one GIF: `fifth-mark.gif`.
  Shows the same arc compressed into a single ~7.8s motion moment.
  Transparent background; works on both light and dark GitHub themes.

## The Signal / Resolve motif

The Fifth Mark is the structural concept of this profile.

Four neutral marks establish a baseline. The fifth (accent, terracotta) starts
out of alignment and progressively resolves:

| Asset | Accent position | Displacement from baseline |
|---|---|---|
| `hero` (bottom row) | y = 306–322 | −12 px |
| `phase-01` | y = −3–13 (top 3px clipped) | −12 px |
| `phase-02` | y = 3–19 | −6 px |
| `phase-03` | y = 7–23 | −2 px |
| `phase-04` | y = 9–25 | 0 px — fully resolved |

The `fifth-mark.gif` animates the same 12px → 0px journey in the motion domain.

## Why PNG, not SVG

GitHub renders SVG via `<img>` but SVG animation is unsupported in that context,
and Firefox has historically shown rendering inconsistencies with `<img src="*.svg">`.
The profile commits deterministic PNG renders (2× resolution for retina) from
well-structured SVG source, eliminating runtime rendering variance.

Motion is handled by committed GIF, which GitHub explicitly supports.

## Palette

| Token | Light | Dark | Semantic role |
|---|---|---|---|
| Background | `#F7F4EE` | `#151816` | Warm paper / deep charcoal |
| Primary text | `#202320` | `#F1EEE7` | Ink — slightly warm, not stark |
| Secondary text | `#6F716D` | `#A4A9A4` | Labels, captions |
| Rule | `#D6D1C7` | `#2C322E` | Dividing lines |
| Neutral marks | `#8C918A` | `#A4A9A4` | The four settled marks |
| Accent | `#BE6848` | `#D98362` | The fifth mark, links |

The terracotta accent is intentionally warm rather than neon or blue-purple.
Against the precision of the neutral system it signals: this engineer is a person,
not a machine.

## Rebuilding assets

```bash
python -m pip install -r requirements-dev.txt
python tools/render_static.py   # regenerate hero and motif PNGs
python tools/render_motion.py   # regenerate fifth-mark.gif
```

Generated assets are committed so the profile has no runtime dependency
on any external service.
