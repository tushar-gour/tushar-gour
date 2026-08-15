"""Render committed PNG assets from the editable SVG source files.

Uses svglib + reportlab (with pycairo backend) to render SVGs to PNG.

Requires:
    pip install svglib reportlab Pillow rlPyCairo

On Windows, rlPyCairo may prefer cairocffi (which requires a system DLL).
We block cairocffi here so rlPyCairo uses the self-contained pycairo instead.
This is the correct approach on Windows without GTK/MSYS2 installed.

Run:
    python tools/render_static.py
"""
import sys
# Block cairocffi so that rlPyCairo falls through to pycairo (self-contained on Windows)
if "cairocffi" not in sys.modules:
    sys.modules["cairocffi"] = None  # type: ignore[assignment]
from pathlib import Path
from io import BytesIO

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

# SVG source → (output PNG path, output width in pixels)
TARGETS: dict[Path, tuple[Path, int]] = {
    ROOT / "assets" / "identity" / "hero-light.svg": (
        ROOT / "assets" / "identity" / "hero-light.png", 2400,
    ),
    ROOT / "assets" / "identity" / "hero-dark.svg": (
        ROOT / "assets" / "identity" / "hero-dark.png", 2400,
    ),
    ROOT / "assets" / "motif" / "phase-01.svg": (
        ROOT / "assets" / "motif" / "phase-01.png", 2400,
    ),
    ROOT / "assets" / "motif" / "phase-02.svg": (
        ROOT / "assets" / "motif" / "phase-02.png", 2400,
    ),
    ROOT / "assets" / "motif" / "phase-03.svg": (
        ROOT / "assets" / "motif" / "phase-03.png", 2400,
    ),
    ROOT / "assets" / "motif" / "phase-04.svg": (
        ROOT / "assets" / "motif" / "phase-04.png", 2400,
    ),
}


def svg_to_png(svg_path: Path, png_path: Path, output_width: int) -> None:
    drawing = svg2rlg(str(svg_path))
    if drawing is None:
        raise RuntimeError(f"svglib could not parse {svg_path}")

    # Scale to the target width
    scale = output_width / drawing.width
    drawing.width  = output_width
    drawing.height = drawing.height * scale
    drawing.transform = (scale, 0, 0, scale, 0, 0)

    # Render to PNG bytes via reportlab
    buf = BytesIO()
    renderPM.drawToFile(drawing, buf, fmt="PNG", bg=0xFFFFFF)
    buf.seek(0)

    # Re-open with Pillow to strip the white background where transparency is
    # expected (motif dividers should be transparent) and save with optimise.
    img = Image.open(buf)

    # For motif dividers, convert white backgrounds to transparent
    if "motif" in str(png_path):
        img = img.convert("RGBA")
        data = img.getdata()
        new_data = []
        for r, g, b, a in data:
            # White-ish pixels → transparent (dividers sit on any background)
            if r > 240 and g > 240 and b > 240:
                new_data.append((r, g, b, 0))
            else:
                new_data.append((r, g, b, a))
        img.putdata(new_data)

    img.save(png_path, "PNG", optimize=True)
    print(f"Rendered {png_path.relative_to(ROOT)}")


if __name__ == "__main__":
    for source, (target, width) in TARGETS.items():
        svg_to_png(source, target, width)
    print("Done.")
