"""Generate the two small, non-essential GIF motion assets used by README.md."""
from pathlib import Path
from math import cos, pi
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "motion"
OUT.mkdir(parents=True, exist_ok=True)

ACCENT = (190, 104, 72, 255)
NEUTRAL = (140, 145, 138, 255)
TRANSPARENT = (0, 0, 0, 0)


def ease_in_out(t: float) -> float:
    return (1 - cos(pi * t)) / 2


def save_gif(frames, path: Path, duration: int) -> None:
    # Pillow handles RGBA -> GIF palette conversion and preserves transparency.
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
    frames = []
    total = 40
    for i in range(total):
        image = Image.new("RGBA", (460, 64), TRANSPARENT)
        draw = ImageDraw.Draw(image)

        baseline_y = 23
        for x in (282, 316, 350, 384):
            draw.rounded_rectangle((x, baseline_y, x + 5, baseline_y + 28), radius=2, fill=NEUTRAL)

        # Move only during the first 45% of the loop, then hold the resolved state.
        progress = min(i / (total * 0.45), 1.0)
        y = round(7 + (baseline_y - 7) * ease_in_out(progress))
        draw.rounded_rectangle((418, y, 423, y + 28), radius=2, fill=ACCENT)
        frames.append(image)

    save_gif(frames, OUT / "fifth-mark.gif", duration=260)


def settle_line() -> None:
    frames = []
    total = 44
    width = 1200
    for i in range(total):
        image = Image.new("RGBA", (width, 18), TRANSPARENT)
        draw = ImageDraw.Draw(image)

        progress = min(i / (total * 0.52), 1.0)
        end = round(1030 + (1168 - 1030) * ease_in_out(progress))
        draw.line((0, 9, end, 9), fill=NEUTRAL, width=1)
        draw.rounded_rectangle((end + 10, 6, end + 14, 12), radius=2, fill=ACCENT)
        frames.append(image)

    save_gif(frames, OUT / "settle-line.gif", duration=260)


if __name__ == "__main__":
    fifth_mark()
    settle_line()
    print(f"Generated motion assets in {OUT}")
