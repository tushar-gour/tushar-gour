"""Verify that local README asset references resolve to nonempty files."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
readme = (ROOT / "README.md").read_text(encoding="utf-8")
refs = sorted(set(re.findall(r"\./assets/[\w./\-]+", readme)))
missing = []
for ref in refs:
    path = ROOT / ref.removeprefix("./")
    ok = path.is_file() and path.stat().st_size > 0
    print(f"{'OK' if ok else 'MISSING':8s} {ref}")
    if not ok:
        missing.append(ref)
if missing or not refs:
    raise SystemExit("README asset validation failed")
print(f"All {len(refs)} asset references OK")
