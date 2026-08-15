"""Quick audit: verify all asset references in README.md resolve to files on disk."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
readme = (ROOT / "README.md").read_text(encoding="utf-8")

pattern = re.compile(r"\./assets/[\w./\-]+")
refs = pattern.findall(readme)

print("Asset references in README.md:")
all_ok = True
for r in refs:
    p = ROOT / r.lstrip("./")
    ok = p.exists()
    if not ok:
        all_ok = False
    print(f"  {'OK' if ok else 'MISSING':8s}  {r}")

print()
print("settle-line.gif:", "FOUND (error)" if "settle-line" in readme else "absent (correct)")
n = readme.count("linkedin.com")
print(f"LinkedIn links: {n} (expected 1)")
print()
print("All references OK" if all_ok else "WARNING: missing references found")
