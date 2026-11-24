"""Install the approved footer as lossless, individually clickable PNG slices."""
from pathlib import Path
from PIL import Image, ImageChops
import hashlib
import re
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "assets/footer"
SOURCE = DIR / "footer-original.png"
KEYS = ("github", "linkedin", "email", "resume")
EXPECTED = "701d4f2650a4264d33e283699fbb9abb6334d7062da459cdc275c749a5d42ec8"

def main():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED:
        raise ValueError("Upload the exact approved footer-original.png, without resaving it")
    dark = Image.open(SOURCE).convert("RGB")
    assert dark.size == (2048, 682)
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
            x = i*512
            path = DIR / f"connect-{key}-{theme}.png"
            image.crop((x,0,x+512,682)).save(path,optimize=True)
            rebuilt.paste(Image.open(path).convert("RGB"),(x,0))
        assert ImageChops.difference(image,rebuilt).getbbox() is None, "Slice pixels changed"
    readme = ROOT / "README.md"
    old = readme.read_text(encoding="utf-8")
    pattern = r"(assets/footer/connect-(?:github|linkedin|email|resume)-(?:dark|light))\.svg"
    new, n = re.subn(pattern,r"\1.png",old)
    if n != 12:
        raise ValueError(f"Unexpected footer layout: {n} image references")
    assert 'mailto:official@tushargour.com' in new
    assert 'https://www.linkedin.com/in/tushar-gour/' in new
    readme.write_text(new,encoding="utf-8")
    for key in KEYS:
        for theme in ("dark","light"):
            (DIR / f"connect-{key}-{theme}.svg").unlink(missing_ok=True)
    SOURCE.unlink()
    docs = ROOT / "assets/README.md"
    content = docs.read_text(encoding="utf-8")
    content = re.sub(r"^- `footer/`:.*$", "- `footer/`: four lossless PNG slices of the approved 2048 × 682 dark contact banner, plus a matching light-palette adaptation. Each slice is independently linked. No duplicate original or obsolete SVG artwork is retained.",content,flags=re.M)
    docs.write_text(content,encoding="utf-8")
    print("Verified all original dark pixels and clickable footer references")

if __name__ == "__main__":
    main()
