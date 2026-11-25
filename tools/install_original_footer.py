"""Install the approved footer as lossless, individually clickable PNG slices."""
from pathlib import Path
from PIL import Image, ImageChops
import hashlib
import base64
import io
from profile_design import palette
from footer_motion import static_top, render_wave
import re
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "assets/footer"
SOURCE = DIR / "footer-original.png"
KEYS = ("github", "linkedin", "email", "resume")
EXPECTED = "e144bf32ad10ad63a56947861c23f64862efa7de9129bb03f254447093c40c8b"

def framed_slice(image, key, x, theme):
    """Keep the PNG pixels unchanged beneath a single shared outer frame."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    b = base64.b64encode(buffer.getvalue()).decode("ascii")
    stroke = palette(theme == "dark")["line"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{x} 0 543 724" width="543" height="724" overflow="hidden" role="img" aria-label="{key} contact">
<defs><clipPath id="frame" clipPathUnits="userSpaceOnUse"><rect width="2172" height="724" rx="28.314"/></clipPath></defs>
<g clip-path="url(#frame)"><image x="{x}" y="0" width="543" height="724" xlink:href="data:image/png;base64,{b}"/></g>
<rect x="1.164" y="1.164" width="2169.672" height="721.672" rx="27.15" fill="none" stroke="{stroke}" stroke-width="2.328"/>
</svg>
'''


def main():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED:
        raise ValueError("Upload the exact approved footer-original.png, without resaving it")
    dark = Image.open(SOURCE).convert("RGB")
    assert dark.size == (2172, 724)
    # Light is explicitly a palette adaptation; dark is never recolored.
    a = np.asarray(dark, dtype=np.float32)/255
    r,g,b = a.transpose(2,0,1)
    y = .2126*r + .7152*g + .0722*b
    paper = np.array([250,247,242], dtype=np.float32)
    ink = np.array([40,35,30], dtype=np.float32)
    bronze = np.array([153,86,23], dtype=np.float32)
    warmth = np.clip((r-b-.045)/.42,0,1)[...,None]
    contrast = np.clip((y-.045)/.82,0,1)[...,None]
    tone = ink*(1-warmth)+bronze*warmth
    light = Image.fromarray(np.uint8(np.clip(paper*(1-contrast)+tone*contrast,0,255)))
    for theme, image in (("dark",dark),("light",light)):
        rebuilt = Image.new("RGB", image.size)
        for i,key in enumerate(KEYS):
            x = i*543
            path = DIR / f"connect-{key}-{theme}.svg"
            crop = image.crop((x,0,x+543,724))
            svg = static_top(framed_slice(crop, key, x, theme), x, theme)
            path.write_text(svg, encoding="utf-8")
            payload = svg.split("data:image/png;base64,",1)[1].split('"',1)[0]
            rebuilt.paste(Image.open(io.BytesIO(base64.b64decode(payload))).convert("RGB"),(x,0))
        assert ImageChops.difference(image,rebuilt).getbbox() is None, "Slice pixels changed"
        (DIR / f"footer-wave-{theme}.svg").write_text(render_wave(theme), encoding="utf-8")
    readme = ROOT / "README.md"
    old = readme.read_text(encoding="utf-8")
    pattern = r"(assets/footer/connect-(?:github|linkedin|email|resume)-(?:dark|light))\.(?:png|svg)"
    new, n = re.subn(pattern,r"\1.svg",old)
    if n != 12:
        raise ValueError(f"Unexpected footer layout: {n} image references")
    assert 'mailto:official@tushargour.com' in new
    assert 'https://www.linkedin.com/in/tushar-gour/' in new
    readme.write_text(new,encoding="utf-8")
    for key in KEYS:
        for theme in ("dark","light"):
            (DIR / f"connect-{key}-{theme}.png").unlink(missing_ok=True)
    SOURCE.unlink()
    docs = ROOT / "assets/README.md"
    content = docs.read_text(encoding="utf-8")
    content = re.sub(r"^- `footer/`:.*$", "- `footer/`: two visually connected rows forming one 2172 × 724 card. Four static upper contact tiles (543 × 444 each) preserve the original embedded PNGs and individual links. One full-width lower SVG (2172 × 280) per theme uses a single seven-second animation timeline for 26 morphing vector strands, eliminating independently timed seams. Matching backgrounds and shared outer frame join at y=444. Reduced motion displays a static ribbon.",content,flags=re.M)
    docs.write_text(content,encoding="utf-8")
    print("Verified all original dark pixels and clickable footer references")

if __name__ == "__main__":
    main()
