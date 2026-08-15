"""Render committed PNG assets from the editable SVG source files."""
from pathlib import Path
import cairosvg

ROOT = Path(__file__).resolve().parents[1]

TARGETS = {
    ROOT / "assets" / "identity" / "hero-light.svg": (ROOT / "assets" / "identity" / "hero-light.png", 2400),
    ROOT / "assets" / "identity" / "hero-dark.svg": (ROOT / "assets" / "identity" / "hero-dark.png", 2400),
    ROOT / "assets" / "motif" / "phase-01.svg": (ROOT / "assets" / "motif" / "phase-01.png", 2400),
    ROOT / "assets" / "motif" / "phase-02.svg": (ROOT / "assets" / "motif" / "phase-02.png", 2400),
    ROOT / "assets" / "motif" / "phase-03.svg": (ROOT / "assets" / "motif" / "phase-03.png", 2400),
    ROOT / "assets" / "motif" / "phase-04.svg": (ROOT / "assets" / "motif" / "phase-04.png", 2400),
}

for source, (target, width) in TARGETS.items():
    cairosvg.svg2png(url=str(source), write_to=str(target), output_width=width)
    print(f"Rendered {target.relative_to(ROOT)}")
