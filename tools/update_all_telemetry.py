#!/usr/bin/env python3
"""
tools/update_all_telemetry.py

Fetches 100% REAL dynamic GitHub metrics and contribution telemetry for tushar-gour:
- Live 52-week contribution pulse (discrete weeks, peak week, current week, active days, 365D total)
- Live language footprint byte aggregation across all user repositories
- Generates pixel-perfect Dark and Light SVG assets and generated/metrics.json.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from profile_design import palette, card, text, line, rect

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
USERNAME = os.getenv("GITHUB_USER", "tushar-gour")
TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

OWNER_TOKEN = os.getenv("PROFILE_READ_TOKEN", "").strip()
# ─────────────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets" / "telemetry"
GENERATED_DIR = ROOT / "generated"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

# Languages to exclude (build/config files)
SKIP_LANGS = {
    "Makefile", "CMake", "Dockerfile", "Shell", "Batchfile", "PowerShell",
    "YAML", "JSON", "TOML", "XML", "Markdown", "Text", "INI",
    "HCL", "Nix", "Meson",
}

def gh_api_request(url: str) -> dict | list:
    req = urllib.request.Request(url)
    req.add_header("User-Agent", f"{USERNAME}-telemetry-pipeline")
    req.add_header("Accept", "application/vnd.github.v3+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"API notice on {url}: {e}", file=sys.stderr)
        return {}

def fetch_live_contributions() -> dict:
    """Fetch live 365-day contribution calendar."""
    print("Fetching live contribution calendar...")
    # Primary: GraphQL if TOKEN exists
    if TOKEN:
        query = """
        query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    contributionCount
                    date
                  }
                }
                months {
                  name
                  year
                }
              }
            }
          }
        }
        """
        req_data = json.dumps({"query": query, "variables": {"login": USERNAME}}).encode("utf-8")
        req = urllib.request.Request("https://api.github.com/graphql", data=req_data)
        req.add_header("Authorization", f"Bearer {TOKEN}")
        req.add_header("User-Agent", f"{USERNAME}-telemetry-pipeline")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                cal = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]
                weeks_raw = cal["weeks"]
                total_contribs = cal["totalContributions"]
                
                days = []
                for w in weeks_raw:
                    for d in w["contributionDays"]:
                        days.append(d)
                
                active_days = sum(1 for d in days if d["contributionCount"] > 0)
                
                # 52 weeks sum
                weekly_52 = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks_raw[-52:]]
                while len(weekly_52) < 52:
                    weekly_52.insert(0, 0)
                
                months = [m["name"][:3].upper() for m in cal.get("months", [])]
                
                return {
                    "total": total_contribs,
                    "active_days": active_days,
                    "peak_week": max(weekly_52),
                    "current_week": weekly_52[-1],
                    "weekly_52": weekly_52,
                    "months": months
                }
        except Exception as e:
            print(f"GraphQL request failed ({e}), falling back to public feed.")

    # Fallback to public contributions service
    try:
        url = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y=last"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            total_contribs = data.get("total", {}).get("lastYear", 0)
            contributions = data.get("contributions", [])
            active_days = sum(1 for c in contributions if c.get("count", 0) > 0)
            
            days_364 = contributions[-364:] if len(contributions) >= 364 else contributions
            weekly_52 = []
            for i in range(0, len(days_364), 7):
                chunk = days_364[i:i+7]
                weekly_52.append(sum(c.get("count", 0) for c in chunk))
            
            if len(weekly_52) > 52:
                weekly_52 = weekly_52[-52:]
            elif len(weekly_52) < 52:
                weekly_52 = [0] * (52 - len(weekly_52)) + weekly_52

            return {
                "total": total_contribs,
                "active_days": active_days,
                "peak_week": max(weekly_52),
                "current_week": weekly_52[-1],
                "weekly_52": weekly_52,
                "months": ["SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG"]
            }
    except Exception as e:
        raise RuntimeError("Contribution feeds unavailable; preserving the last published snapshot") from e


def fetch_repository_count():
    """Read owner-visible public and private totals. Never count a restricted Actions token as owner access."""
    if OWNER_TOKEN:
        req = urllib.request.Request("https://api.github.com/user", headers={
            "Authorization": f"Bearer {OWNER_TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{USERNAME}-telemetry-pipeline",
        })
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                user = json.loads(response.read().decode("utf-8"))
                scopes = {s.strip() for s in response.headers.get("X-OAuth-Scopes", "").split(",")}
            if user.get("login","").lower() != USERNAME.lower() or "repo" not in scopes:
                raise ValueError("PROFILE_READ_TOKEN must be an owner classic PAT with repo scope")
            public, private = user["public_repos"], user["total_private_repos"]
            if not isinstance(public,int) or not isinstance(private,int) or min(public,private)<0:
                raise ValueError("Invalid repository totals")
            return {"total": public+private, "public": public, "private": private,
                    "visibility": "PUBLIC + PRIVATE", "source": "owner_api",
                    "verifiedAt": datetime.now(timezone.utc).isoformat(), "fresh": True}
        except Exception as exc:
            print(f"Owner repository count unavailable: {exc}", file=sys.stderr)
    previous = json.loads((GENERATED_DIR / "metrics.json").read_text(encoding="utf-8"))["repositories"]
    if previous.get("visibility") != "PUBLIC + PRIVATE" or "verifiedAt" not in previous:
        raise RuntimeError("No verified complete repository snapshot available")
    return {**previous, "fresh": False}


LANGUAGE_METHOD = "max_js_ts"


def summarize_language_bytes(lang_bytes):
    """Adjusted footprint: retain max(JS, TS), not their sum, under TypeScript.

    This is an explicit display heuristic, not exact generated-code detection.
    All other language byte counts are unchanged.
    """
    counts = dict(lang_bytes)
    js = counts.pop("JavaScript", 0)
    ts = counts.pop("TypeScript", 0)
    if max(js, ts):
        counts["TypeScript"] = max(js, ts)
    total = sum(counts.values())
    if not total:
        raise ValueError("No language bytes available")
    ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    top = ranked[:5]
    other = total - sum(b for _, b in top)
    if other:
        top.append(("Other", other))
    return {
        "totalBytes": total,
        "breakdown": [{"language": lang, "bytes": b, "percentage": round(100*b/total,1)} for lang,b in top],
        "method": LANGUAGE_METHOD,
        "rawJavaScriptBytes": js,
        "rawTypeScriptBytes": ts,
        "source": "public_repository_language_api",
    }


def fetch_live_languages() -> dict:
    """Read all public owned repositories, retaining the prior adjusted snapshot on API failure."""
    print("Fetching live repository languages...")
    try:
        repos = []
        page = 1
        while True:
            data = gh_api_request(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&type=owner")
            if not isinstance(data, list):
                raise RuntimeError("Repository enumeration failed")
            repos.extend(data)
            if len(data) < 100:
                break
            page += 1

        lang_bytes = {}
        for r in repos:
            if r.get("fork") or r.get("archived"):
                continue
            url = r.get("languages_url")
            if not url:
                raise RuntimeError("Missing languages endpoint")
            # Request directly so an empty repository can be distinguished from API failure.
            req = urllib.request.Request(url, headers={"User-Agent": f"{USERNAME}-telemetry-pipeline", "Accept": "application/vnd.github+json"})
            if TOKEN:
                req.add_header("Authorization", f"Bearer {TOKEN}")
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
            if not isinstance(data, dict) or any(type(b) is not int or b < 0 for b in data.values()):
                raise RuntimeError("Invalid language response")
            for lang,b in data.items():
                if lang not in SKIP_LANGS:
                    lang_bytes[lang] = lang_bytes.get(lang,0)+b
            time.sleep(0.04)
        return summarize_language_bytes(lang_bytes)
    except Exception as exc:
        print(f"Language refresh unavailable; retaining last adjusted snapshot: {exc}", file=sys.stderr)
        previous = json.loads((GENERATED_DIR / "metrics.json").read_text(encoding="utf-8"))["languages"]
        if previous.get("method") != LANGUAGE_METHOD:
            raise RuntimeError("No adjusted language snapshot available") from exc
        return previous

# ─── SVG GENERATORS ───────────────────────────────────────────────────────────

def build_pulse_svg(contrib_data: dict, repositories: dict, is_dark=True):
    p = palette(is_dark)
    weeks = contrib_data["weekly_52"]
    if len(weeks) != 52 or any(not isinstance(n, int) or n < 0 for n in weeks):
        raise ValueError("Expected 52 non-negative weekly contribution counts")
    peak = max(weeks)
    top_seven = set(sorted((i for i,n in enumerate(weeks) if n>0), key=lambda i: (-weeks[i],i))[:7])
    active_weeks = sum(n>0 for n in weeks)
    step = max(50, ((peak + 249) // 250) * 50)
    y_max = 5 * step
    parts = [card(438, "ENGINEERING ACTIVITY", "365-DAY SNAPSHOT", p)]
    for x, value, label in [(36, f'{repositories["total"]:,}', "Repositories (public + private)"), (310, f'{contrib_data["total"]:,}', "Contributions"), (580, contrib_data["active_days"], "Active days"), (850, active_weeks, "Active weeks / 52")]:
        parts.extend([text(x,132,value,36,600,p["fg"]), text(x,157,label,15,400,p["muted"])])
    parts.extend([line(292,94,292,170,p),line(562,94,562,170,p),line(832,94,832,170,p),line(36,184,1084,184,p)])
    for tick in range(0,y_max+1,step):
        y = 391 - 182*tick/y_max
        parts.extend([line(78,f"{y:.2f}",1084,f"{y:.2f}",p),text(64,f"{y+5:.2f}",tick,14,400,p["muted"],"end")])
    for i,n in enumerate(weeks):
        if not n:
            continue
        h = 182*n/y_max
        x = 78+(i+.5)*1006/52-7.2
        fill = p["accent"] if i in top_seven else p["bar"]
        parts.append(f'  <rect x="{x:.2f}" y="{391-h:.2f}" width="14.4" height="{h:.2f}" rx="{min(2.5,h/2):.2f}" fill="{fill}"><title>Week {i+1}: {n} contributions</title></rect>')
    parts.extend([text(78,414,"WEEK 01",14,500,p["muted"]),text(1084,414,"WEEK 52",14,500,p["muted"],"end"),"</svg>\n"])
    return "\n".join(parts)

def build_spectrum_svg(languages: list, is_dark=True):
    p = palette(is_dark)
    total = sum(l["bytes"] for l in languages)
    rows = (len(languages)+1)//2
    parts = [card(166+rows*76,"LANGUAGE FOOTPRINT","ADJUSTED CODE VOLUME · MAX(JS, TS)",p)]
    parts.append("<desc>JavaScript and TypeScript share a single TypeScript bucket equal to the larger raw byte total, not their sum. Other languages retain their original counts. This is a display heuristic.</desc>")
    x = 36
    usable = 1048-4*max(0,len(languages)-1)
    for i,l in enumerate(languages):
        w = usable*l["bytes"]/total if total else 0
        parts.append(rect(f"{x:.2f}",96,f"{w:.2f}",28,f"{min(4,w/2):.2f}",p["colors"][i%6]))
        x += w+4
    parts.append(line(36,144,1084,144,p))
    for i,l in enumerate(languages):
        j,col = i%rows,i//rows
        xx,y = 36+col*548,182+j*76
        c = p["colors"][i%6]
        pct = 100*l["bytes"]/total if total else 0
        parts.extend([f'  <circle cx="{xx+7}" cy="{y-6}" r="7" fill="{c}"/>',text(xx+24,y,l["language"],22,600,p["fg"]),text(xx+328,y,f"{pct:.1f}%",20,600,p["accent"],"end"),text(xx+348,y,"|",18,400,p["muted"],"middle"),text(xx+500,y,f'{l["bytes"]:,} B',17,400,p["muted"],"end"),rect(xx+24,y+14,476,9,4.5,p["track"]),rect(xx+24,y+14,f"{476*pct/100:.2f}",9,f"{min(4.5,476*pct/200):.2f}",c)])
        if j<rows-1:
            parts.append(line(xx,y+39,xx+500,y+39,p))
    parts.append("</svg>\n")
    return "\n".join(parts)


def main():
    print("=== Running Live GitHub Telemetry Ingestion Pipeline ===")
    
    # 1. Fetch live metrics
    contrib_data = fetch_live_contributions()
    language_snapshot = fetch_live_languages()
    languages = language_snapshot["breakdown"]

    repositories = fetch_repository_count()
    total_repos = repositories['total']
    total_contribs = contrib_data["total"]
    active_days = contrib_data["active_days"]
    peak_week = contrib_data["peak_week"]

    print(f"Metrics: Repos={total_repos}, Contribs={total_contribs}, ActiveDays={active_days}, PeakWeek={peak_week}")

    # 2. Generate Engineering Activity SVGs
    pulse_dark = build_pulse_svg(contrib_data, repositories, is_dark=True)
    pulse_light = build_pulse_svg(contrib_data, repositories, is_dark=False)

    (ASSETS_DIR / "pulse-52w-dark.svg").write_text(pulse_dark, encoding="utf-8")
    (ASSETS_DIR / "pulse-52w-light.svg").write_text(pulse_light, encoding="utf-8")
    print("Generated pulse-52w-dark.svg & pulse-52w-light.svg")

    # 3. Generate Language Footprint Spectrum SVGs
    spec_dark = build_spectrum_svg(languages, is_dark=True)
    spec_light = build_spectrum_svg(languages, is_dark=False)

    (ASSETS_DIR / "domain-spectrum-dark.svg").write_text(spec_dark, encoding="utf-8")
    (ASSETS_DIR / "domain-spectrum-light.svg").write_text(spec_light, encoding="utf-8")
    print("Generated domain-spectrum-dark.svg & domain-spectrum-light.svg")

    # 4. Output Machine-Readable Manifest
    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "user": USERNAME,
        "repositories": repositories,
        "contributions": {
            "total365": total_contribs,
            "activeDays": active_days,
            "peakWeek": peak_week,
            "currentWeek": contrib_data["current_week"],
            "weeklyPulse": contrib_data["weekly_52"],
            "activeWeeks": sum(n>0 for n in contrib_data["weekly_52"])
        },
        "languages": language_snapshot
    }
    (GENERATED_DIR / "metrics.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Saved generated/metrics.json manifest.")
    print("=== Telemetry pipeline finished successfully. ===")

if __name__ == "__main__":
    main()
