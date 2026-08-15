"""Generate the motion GIF asset used by README.md.

The fifth-mark animation shows the visual thesis of the profile in motion:
four neutral marks fixed at baseline, one accent mark starting 12px above
(mirroring the Phase-01 divider displacement) and settling slowly into
alignment (the Phase-04 resolved state).

Motion principles:
  - slow > fast
  - long hold > constant movement
  - ease-in-out > linear
  - one motion moment per profile > many distractions
"""
from pathlib import Path
from math import cos, pi
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "motion"
OUT.mkdir(parents=True, exist_ok=True)

# Palette — matches the SVG design system
ACCENT = (190, 104, 72, 255)    # #BE6848 terracotta
NEUTRAL = (140, 145, 138, 255)  # #8C918A quiet neutral
TRANSPARENT = (0, 0, 0, 0)


def ease_in_out(t: float) -> float:
    """Smooth step: slow start, accelerate through middle, slow to rest."""
    return (1 - cos(pi * t)) / 2


def save_gif(frames: list, path: Path, duration: int) -> None:
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        disposal=2,
        transparency=0,
    )


def fifth_mark() -> None:
    """
    Accent mark descends from 12px above the neutral baseline to alignment.
    Mirrors the Phase-01 → Phase-04 divider progression shown statically
    across the full profile — here compressed into a single motion moment.

    Timing: 60 frames at 130ms each = ~7.8s loop.
    Settlement: first 42% of frames (25 frames, ~3.3s).
    Hold at rest: remaining 35 frames (~4.5s) before restart.
    """
    frames = []
    total = 60
    settle_fraction = 0.42   # fraction of total frames used for settling
    baseline_y = 23          # y where neutral marks sit
    start_y = 11             # 12px above baseline (mirrors Phase-01 displacement)
    mark_h = 28              # mark height (matches the divider mark proportions)
    mark_w = 5

    for i in range(total):
        image = Image.new("RGBA", (460, 64), TRANSPARENT)
        draw = ImageDraw.Draw(image)

        # Four neutral marks — fixed at baseline, establishing the target
        for x in (282, 316, 350, 384):
            draw.rounded_rectangle(
                (x, baseline_y, x + mark_w, baseline_y + mark_h),
                radius=2,
                fill=NEUTRAL,
            )

        # Accent mark — eases from start_y to baseline_y, then holds
        progress = min(i / (total * settle_fraction), 1.0)
        y = round(start_y + (baseline_y - start_y) * ease_in_out(progress))
        draw.rounded_rectangle(
            (418, y, 418 + mark_w, y + mark_h),
            radius=2,
            fill=ACCENT,
        )
        frames.append(image)

    save_gif(frames, OUT / "fifth-mark.gif", duration=130)
    print(f"Generated {(OUT / 'fifth-mark.gif').relative_to(ROOT)}")


if __name__ == "__main__":
    fifth_mark()
