"""Enable the theme switch only after the light hero exists."""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
readme = root / "README.md"
assert (root / "assets/identity/hero-gold-light.png").is_file()
old = "<img src=\"./assets/identity/hero-gold.png\" alt=\"Tushar Gour — Software Engineer\" width=\"100%\">"
new = "<picture>\n  <source media=\"(prefers-color-scheme: dark)\" srcset=\"./assets/identity/hero-gold.png\">\n  <source media=\"(prefers-color-scheme: light)\" srcset=\"./assets/identity/hero-gold-light.png\">\n  <img src=\"./assets/identity/hero-gold.png\" alt=\"Tushar Gour — Software Engineer\" width=\"100%\">\n</picture>"
text = readme.read_text(encoding="utf-8")
if old in text and new not in text:
    readme.write_text(text.replace(old, new, 1), encoding="utf-8")
elif new not in text:
    raise SystemExit("Unexpected README hero markup")
