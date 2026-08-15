#!/usr/bin/env python3
"""
gen_domain_spectrum.py — Generate language footprint SVGs from GitHub API.

Aggregates real language bytes across all public repositories for a given user,
then renders two SVG files (dark + light) matching the editorial design.

Usage:
    python tools/gen_domain_spectrum.py

Environment variables:
    GITHUB_TOKEN   GitHub token for authenticated requests (5 000 req/hr)
                   Without it, 60 req/hr unauthenticated — may hit limits on large accounts.
    GITHUB_USER    GitHub username (default: tushar-gour)
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

# ─── Config ──────────────────────────────────────────────────────────────────
GITHUB_USER = os.getenv("GITHUB_USER", "tushar-gour")
TOKEN       = os.getenv("GITHUB_TOKEN", "")
OUT_DIR     = os.path.join(os.path.dirname(__file__), "..", "assets", "telemetry")
TOP_N       = 5    # Top languages shown individually; the rest collapse to "Other"

# Languages to exclude (config / markup / build files — not authored code)
SKIP_LANGS = {
    "Makefile", "CMake", "Dockerfile", "Shell", "Batchfile", "PowerShell",
    "YAML", "JSON", "TOML", "XML", "Markdown", "Text", "INI",
    "HCL", "Nix", "Meson",
}

# Merge these language names into a unified display name
MERGE_LANGS = {
    "C":   "C++ / Native",
    "C++": "C++ / Native",
}


# ─── GitHub API helpers ───────────────────────────────────────────────────────
def gh_get(path: str):
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", f"{GITHUB_USER}/readme-gen/2.0")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"  ⚠  HTTP {e.code}  {url}", file=sys.stderr)
        return {} if path.endswith("/languages") else []
    except Exception as e:
        print(f"  ⚠  {e}  {url}", file=sys.stderr)
        return {}


def fetch_all_repos() -> list:
    repos, page = [], 1
    while True:
        chunk = gh_get(f"/users/{GITHUB_USER}/repos?type=owner&per_page=100&page={page}")
        if not isinstance(chunk, list) or not chunk:
            break
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    return repos


def aggregate_languages(repos: list) -> dict:
    totals: dict = {}
    for repo in repos:
        # Skip forks and archived repos
        if repo.get("fork") or repo.get("archived"):
            continue
        langs = gh_get(f"/repos/{GITHUB_USER}/{repo['name']}/languages")
        time.sleep(0.06)  # Stay well within rate limits
        for lang, byte_count in langs.items():
            if lang in SKIP_LANGS:
                continue
            key = MERGE_LANGS.get(lang, lang)
            totals[key] = totals.get(key, 0) + byte_count
    return totals


# ─── SVG palettes ────────────────────────────────────────────────────────────
DARK = {
    "bg":    "#0C1018",   "border": "#1C2632",
    "txt":   "#DED5C6",   "accent": "#C97B4B",
    "muted": "#4A6070",   "meta":   "#374A5C",
    # Spectrum bar segment colors (left stacked bar)
    "spec":  ["#C97B4B", "#D0C8B8", "#9AB0C0", "#6A8090", "#4A6070", "#2E3E4E"],
    # Right panel progress bar fills
    "bars":  ["#C97B4B", "#B0A898", "#7A8A9A", "#4A6070", "#3A5060", "#2E3E4E"],
}

LIGHT = {
    "bg":    "#FFFFFF",   "border": "#D0D7DE",
    "txt":   "#1F2328",   "accent": "#B85C3F",
    "muted": "#8A9299",   "meta":   "#59636E",
    "spec":  ["#B85C3F", "#7A8A9A", "#9AAFBE", "#B8CCDA", "#CCD8E4", "#DDE8F0"],
    "bars":  ["#B85C3F", "#6A7A8A", "#90A8B8", "#B0C8D8", "#C8D8E8", "#D8E8F0"],
}


# ─── SVG generator ───────────────────────────────────────────────────────────
def xe(s: str) -> str:
    """XML-escape a string."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_svg(rows: list, total_bytes: int, c: dict) -> str:
    """
    rows  = [(display_name, pct_float), ...]   sorted descending
    total_bytes = raw byte total
    c     = palette dict
    """
    mb = total_bytes / 1_048_576

    # ── Left spectrum bar ─────────────────────────────────────────
    SX, SY, SW, SH, SGAP = 42, 190, 320, 18, 3
    segs = []
    cx = SX
    for i, (_, pct) in enumerate(rows):
        w = max(3, round(SW * pct / 100))
        col = c["spec"][i] if i < len(c["spec"]) else c["spec"][-1]
        segs.append(f'  <rect x="{cx}" y="{SY}" width="{w}" height="{SH}" rx="3" fill="{col}"/>')
        cx += w + SGAP
    dot_cx = cx + 8
    dot_cy = SY + SH // 2

    # ── Right panel rows ──────────────────────────────────────────
    RX   = 460    # x start of right panel
    RMAX = 698    # max bar width  (1158 - 460)
    RH   = 46     # row height
    RS   = 42     # row start y
    right_rows = []
    for i, (name, pct) in enumerate(rows):
        ry  = RS + i * RH
        bw  = max(4, round(RMAX * pct / 100))
        pct_col = c["accent"] if i == 0 else c["txt"]
        bar_col = c["bars"][i] if i < len(c["bars"]) else c["bars"][-1]
        right_rows.append(
            f'  <text class="s" x="{RX}" y="{ry + 16}" font-size="16" font-weight="500"'
            f' fill="{c["txt"]}">{xe(name)}</text>\n'
            f'  <text class="m" x="1158" y="{ry + 16}" font-size="14" font-weight="700"'
            f' fill="{pct_col}" text-anchor="end">{pct:.1f}%</text>\n'
            f'  <rect x="{RX}" y="{ry + 24}" width="{bw}" height="7" rx="3.5" fill="{bar_col}"/>'
        )

    spec_block  = "\n".join(segs)
    right_block = "\n".join(right_rows)
    bg, bd = c["bg"], c["border"]
    txt, acc, mu, me = c["txt"], c["accent"], c["muted"], c["meta"]

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 340" width="100%" height="100%">\n'
        f'  <defs><style>'
        f'.m{{font-family:\'SF Mono\',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}'
        f'.s{{font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Helvetica,Arial,sans-serif}}'
        f'</style></defs>\n\n'
        f'  <rect width="1200" height="340" rx="10" fill="{bg}"/>\n'
        f'  <rect width="1200" height="340" rx="10" fill="none" stroke="{bd}" stroke-width="1.2"/>\n\n'

        f'  <!-- ── LEFT PANEL ── -->\n'
        f'  <text class="m" x="42" y="58" font-size="12" font-weight="800" fill="{acc}" letter-spacing="2">LANGUAGE</text>\n'
        f'  <text class="s" x="42" y="128" font-size="56" font-weight="900" fill="{txt}" letter-spacing="-2">FOOTPRINT</text>\n'
        f'  <text class="m" x="42" y="158" font-size="11" font-weight="600" fill="{mu}" letter-spacing="2">AGGREGATED REPOSITORY BYTES</text>\n\n'

        f'  <!-- Spectrum bar -->\n'
        f'{spec_block}\n'
        f'  <!-- Marker dot -->\n'
        f'  <circle cx="{dot_cx}" cy="{dot_cy}" r="8" fill="none" stroke="{acc}" stroke-width="1.8"/>\n'
        f'  <circle cx="{dot_cx}" cy="{dot_cy}" r="3.5" fill="{acc}"/>\n\n'

        f'  <!-- Database icon -->\n'
        f'  <ellipse cx="51" cy="248" rx="9" ry="3.5" fill="none" stroke="{me}" stroke-width="1.3"/>\n'
        f'  <line x1="42" y1="248" x2="42" y2="260" stroke="{me}" stroke-width="1.3"/>\n'
        f'  <line x1="60" y1="248" x2="60" y2="260" stroke="{me}" stroke-width="1.3"/>\n'
        f'  <ellipse cx="51" cy="260" rx="9" ry="3.5" fill="none" stroke="{me}" stroke-width="1.3"/>\n'
        f'  <text class="m" x="70" y="262" font-size="11.5" font-weight="600" fill="{mu}" letter-spacing="1">TOTAL INDEXED: {mb:.1f} MB</text>\n\n'

        f'  <!-- Shield icon -->\n'
        f'  <path d="M 51 276 Q 42 272 42 265 L 42 282 Q 42 294 51 298 Q 60 294 60 282 L 60 265 Q 60 272 51 276 Z"'
        f' fill="none" stroke="{me}" stroke-width="1.3"/>\n'
        f'  <text class="m" x="70" y="294" font-size="11.5" font-weight="600" fill="{me}" letter-spacing="1">SOURCE: VERIFIED CODEBASE BYTES</text>\n\n'

        f'  <!-- Divider -->\n'
        f'  <line x1="424" y1="20" x2="424" y2="320" stroke="{bd}" stroke-width="1"/>\n\n'

        f'  <!-- ── RIGHT PANEL ── -->\n'
        f'{right_block}\n'
        f'</svg>'
    )


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"🔍  Fetching repositories for {GITHUB_USER}…")
    repos = fetch_all_repos()
    owned = [r for r in repos if not r.get("fork") and not r.get("archived")]
    print(f"    {len(owned)} owned, non-archived repos found (of {len(repos)} total)")

    print("📊  Aggregating language bytes…")
    raw = aggregate_languages(repos)
    if not raw:
        print("⚠  No language data retrieved. Check GITHUB_TOKEN and username.", file=sys.stderr)
        sys.exit(1)

    total = sum(raw.values())
    sorted_langs = sorted(raw.items(), key=lambda x: x[1], reverse=True)

    top = sorted_langs[:TOP_N]
    rest = sorted_langs[TOP_N:]
    other_bytes = sum(v for _, v in rest)
    other_names  = [n for n, _ in rest[:4]]
    other_label  = ("Other (" + ", ".join(other_names) + ")") if other_names else "Other"

    rows = [(n, v / total * 100) for n, v in top]
    if other_bytes:
        rows.append((other_label, other_bytes / total * 100))

    print("    Language breakdown:")
    for name, pct in rows:
        print(f"      {name:<34} {pct:5.1f}%")
    print(f"    Total: {total:,} bytes  ({total / 1_048_576:.2f} MB)")

    for theme, palette in [("dark", DARK), ("light", LIGHT)]:
        out_path = os.path.join(OUT_DIR, f"domain-spectrum-{theme}.svg")
        svg_content = generate_svg(rows, total, palette)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(svg_content)
        print(f"✅  {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()
