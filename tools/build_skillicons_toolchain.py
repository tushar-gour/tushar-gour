#!/usr/bin/env python3
import urllib.request
import os
import re
import base64

CACHE_DIR = os.path.join(os.path.dirname(__file__), "skillicons_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# List of skill definitions: (lane_idx, col_idx, id, display_label, is_primary, icon_dark, icon_light)
SKILLS = [
    # Lane 01: PRODUCT (Y=135)
    (1, 0, "Flutter", "Flutter", True, "Flutter-Dark.svg", "Flutter-Light.svg"),
    (1, 1, "Dart", "Dart", False, "Dart-Dark.svg", "Dart-Light.svg"),
    (1, 2, "React", "React", True, "React-Dark.svg", "React-Light.svg"),
    (1, 3, "TypeScript", "TypeScript", True, "TypeScript.svg", "TypeScript.svg"),
    (1, 4, "Tailwind", "Tailwind", False, "TailwindCSS-Dark.svg", "TailwindCSS-Light.svg"),
    (1, 5, "Vite", "Vite", False, "Vite-Dark.svg", "Vite-Light.svg"),

    # Lane 02: SERVICES (Y=255)
    (2, 0, "NodeJS", "Node.js", True, "NodeJS-Dark.svg", "NodeJS-Light.svg"),
    (2, 1, "Express", "Express", False, "ExpressJS-Dark.svg", "ExpressJS-Light.svg"),
    (2, 2, "SocketIO", "Socket.IO", False, "CUSTOM_SOCKETIO", "CUSTOM_SOCKETIO"),
    (2, 3, "Java", "Java", True, "Java-Dark.svg", "Java-Light.svg"),

    # Lane 03: DATA (Y=375)
    (3, 0, "PostgreSQL", "PostgreSQL", True, "PostgreSQL-Dark.svg", "PostgreSQL-Light.svg"),
    (3, 1, "MongoDB", "MongoDB", False, "MongoDB.svg", "MongoDB.svg"),
    (3, 2, "Redis", "Redis", True, "Redis-Dark.svg", "Redis-Light.svg"),
    (3, 3, "MySQL", "MySQL", False, "MySQL-Dark.svg", "MySQL-Light.svg"),
    (3, 4, "Prisma", "Prisma", False, "Prisma.svg", "Prisma.svg"),
    (3, 5, "Drizzle", "Drizzle", False, "CUSTOM_DRIZZLE", "CUSTOM_DRIZZLE"),
    (3, 6, "SQLite", "SQLite", False, "SQLite.svg", "SQLite.svg"),
    (3, 7, "Supabase", "Supabase", False, "Supabase-Dark.svg", "Supabase-Light.svg"),

    # Lane 04: DELIVERY (Y=495)
    (4, 0, "AWS", "AWS", True, "AWS-Dark.svg", "AWS-Light.svg"),
    (4, 1, "GCP", "GCP", False, "GCP-Dark.svg", "GCP-Light.svg"),
    (4, 2, "Docker", "Docker", True, "Docker.svg", "Docker.svg"),
    (4, 3, "Linux", "Linux", False, "Linux-Dark.svg", "Linux-Light.svg"),
    (4, 4, "CI/CD", "CI/CD", False, "GithubActions-Dark.svg", "GithubActions-Light.svg"),
    (4, 5, "Vercel", "Vercel", False, "Vercel-Dark.svg", "Vercel-Light.svg"),

    # Lane 05: AI & TOOLS (Y=615)
    (5, 0, "Python", "Python", True, "Python-Dark.svg", "Python-Light.svg"),
    (5, 1, "PyTorch", "PyTorch", False, "PyTorch-Dark.svg", "PyTorch-Light.svg"),
    (5, 2, "Git", "Git", False, "Git.svg", "Git.svg"),
    (5, 3, "Postman", "Postman", False, "Postman.svg", "Postman.svg"),
    (5, 4, "Figma", "Figma", False, "Figma-Dark.svg", "Figma-Light.svg"),
    (5, 5, "Blender", "Blender", False, "Blender-Dark.svg", "Blender-Light.svg"),
    (5, 6, "Unity", "Unity", False, "Unity-Dark.svg", "Unity-Light.svg"),
]

COL_X = [230, 350, 470, 590, 710, 830, 950, 1070]
LANE_Y = {1: 135, 2: 255, 3: 375, 4: 495, 5: 615}
LANE_LABELS = {
    1: ("01", "PRODUCT"),
    2: ("02", "SERVICES"),
    3: ("03", "DATA"),
    4: ("04", "DELIVERY"),
    5: ("05", "AI &amp; TOOLS"),
}

def get_icon_svg(filename, is_dark):
    if filename == "CUSTOM_SOCKETIO":
        bg = "#242938" if is_dark else "#FFFFFF"
        fg = "#FFFFFF" if is_dark else "#1F2328"
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<circle cx="128" cy="128" r="75" fill="none" stroke="{fg}" stroke-width="12"/>
<polygon points="148,72 120,120 142,120 108,184 136,136 114,136" fill="{fg}"/>'''

    if filename == "CUSTOM_DRIZZLE":
        bg = "#242938" if is_dark else "#FFFFFF"
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<line x1="76" y1="164" x2="160" y2="72" stroke="#C5F74F" stroke-width="16" stroke-linecap="round"/>
<line x1="110" y1="184" x2="184" y2="102" stroke="#C5F74F" stroke-width="16" stroke-linecap="round"/>'''

    cache_path = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(cache_path):
        url = f"https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/{filename}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
        with open(cache_path, "wb") as f:
            f.write(data)

    with open(cache_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract inside of <svg ...> ... </svg>
    match = re.search(r'<svg[^>]*>(.*)</svg>', content, re.DOTALL)
    if match:
        inner = match.group(1).strip()
        return inner
    return content

def build_toolchain(is_dark=True):
    theme_suffix = "" if is_dark else "L"
    bg_vignette = "#0F1923" if is_dark else "#F8FAFC"
    bg_vignette_outer = "#080C11" if is_dark else "#EDF2F7"
    border_col = "#1C2632" if is_dark else "#D0D7DE"
    track_col = "#1E2830" if is_dark else "#D8DDE3"
    track_term = "#374448" if is_dark else "#A0AAB2"
    hdr_sub = "#586068" if is_dark else "#8A9299"
    lane_txt = "#C8D0D8" if is_dark else "#3A4450"
    label_txt = "#C8D0D8" if is_dark else "#3A4450"
    accent = "#FF6B35" if is_dark else "#C96A4B"

    # Rocket base64
    rocket_path = os.path.join(os.path.dirname(__file__), "..", "assets", "skills", "rocket.png")
    with open(rocket_path, "rb") as f:
        rocket_b64 = base64.b64encode(f.read()).decode("utf-8")

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 710" width="100%" height="100%">
  <defs>
    <radialGradient id="bgVignette{theme_suffix}" cx="50%" cy="50%" r="75%">
      <stop offset="0%" stop-color="{bg_vignette}"/>
      <stop offset="100%" stop-color="{bg_vignette_outer}"/>
    </radialGradient>

    <!-- Laser bullet gradient tail: 0% opacity at pointed left tip (x=-100) ramping smoothly to head (x=0) -->
    <linearGradient id="laserTail{theme_suffix}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0"/>
      <stop offset="20%" stop-color="{accent}" stop-opacity="0.12"/>
      <stop offset="50%" stop-color="{accent}" stop-opacity="0.45"/>
      <stop offset="80%" stop-color="#FFA880" stop-opacity="0.8"/>
      <stop offset="95%" stop-color="#FFFFFF" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="1"/>
    </linearGradient>

    <radialGradient id="flareGrad{theme_suffix}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="1"/>
      <stop offset="40%" stop-color="{accent}" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>

    <filter id="laserGlow{theme_suffix}" x="-200%" y="-400%" width="500%" height="900%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="b1"/>
      <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="b2"/>
      <feMerge><feMergeNode in="b2"/><feMergeNode in="b1"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>

    <filter id="cardGlow{theme_suffix}" x="-25%" y="-25%" width="150%" height="150%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="4" result="blur"/>
      <feFlood flood-color="{accent}" flood-opacity="0.4" result="c"/>
      <feComposite in="c" in2="blur" operator="in" result="glow"/>
      <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>

    <style>
      .mono{theme_suffix} {{ font-family: 'SF Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
      .label{theme_suffix} {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-weight: 700; }}

      @keyframes bulletAnim{theme_suffix} {{
        0%   {{ transform: translateX(100px); opacity: 0; }}
        3%   {{ transform: translateX(160px); opacity: 1; }}
        56%  {{ transform: translateX(1100px); opacity: 1; }}
        62%  {{ transform: translateX(1162px); opacity: 0; }}
        100% {{ transform: translateX(1162px); opacity: 0; }}
      }}

      .b1{theme_suffix} {{ animation: bulletAnim{theme_suffix} 6.5s cubic-bezier(.25,0,.25,1) infinite; }}
      .b2{theme_suffix} {{ animation: bulletAnim{theme_suffix} 8.0s cubic-bezier(.25,0,.25,1) infinite; animation-delay: 1.8s; }}
      .b3{theme_suffix} {{ animation: bulletAnim{theme_suffix} 7.2s cubic-bezier(.25,0,.25,1) infinite; animation-delay: 3.5s; }}
      .b4{theme_suffix} {{ animation: bulletAnim{theme_suffix} 8.5s cubic-bezier(.25,0,.25,1) infinite; animation-delay: 0.8s; }}
      .b5{theme_suffix} {{ animation: bulletAnim{theme_suffix} 7.6s cubic-bezier(.25,0,.25,1) infinite; animation-delay: 2.6s; }}

      @keyframes cardPulse{theme_suffix} {{
        0%,100% {{ stroke-opacity:0.85; }}
        50% {{ stroke-opacity:1; }}
      }}
      .pri{theme_suffix} {{ animation: cardPulse{theme_suffix} 3.5s ease-in-out infinite; }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="1200" height="710" rx="14" fill="url(#bgVignette{theme_suffix})"/>
  <rect width="1200" height="710" rx="14" fill="none" stroke="{border_col}" stroke-width="1.2"/>''')

    if is_dark:
        svg_parts.append('''  <!-- Star field -->
  <g fill="#FFFFFF" opacity="0.35">
    <circle cx="82" cy="44" r="0.8"/><circle cx="220" cy="28" r="1"/><circle cx="410" cy="52" r="0.7"/>
    <circle cx="660" cy="30" r="0.9"/><circle cx="870" cy="45" r="0.7"/><circle cx="1080" cy="25" r="1"/>
    <circle cx="135" cy="670" r="0.8"/><circle cx="490" cy="685" r="0.7"/><circle cx="940" cy="675" r="1"/>
    <circle cx="1140" cy="660" r="0.8"/><circle cx="40" cy="330" r="0.7"/><circle cx="1165" cy="340" r="0.9"/>
  </g>''')

    svg_parts.append(f'''  <!-- Left orbital arc trajectory -->
  <path d="M 170 670 C -40 510 -40 180 170 40" fill="none" stroke="{accent}" stroke-width="1.4" opacity="0.2"/>
  <g transform="translate(90, 375)">
    <circle cx="0" cy="0" r="5" fill="url(#flareGrad{theme_suffix})" opacity="0.9"/>
    <circle cx="0" cy="0" r="3" fill="{accent}"/>
    <line x1="-14" y1="0" x2="14" y2="0" stroke="{accent}" stroke-width="1.2" opacity="0.6"/>
    <line x1="0" y1="-14" x2="0" y2="14" stroke="{accent}" stroke-width="1.2" opacity="0.6"/>
  </g>

  <!-- Header -->
  <g transform="translate(42, 42)">
    <text class="mono{theme_suffix}" font-size="16" font-weight="800" fill="{accent}" letter-spacing="1.5">ENGINEERING STACK</text>
    <text class="mono{theme_suffix}" x="220" font-size="13" font-weight="600" fill="{hdr_sub}" letter-spacing="1.5">/ TOOLS ACROSS THE SOFTWARE DELIVERY PATH</text>
    <text class="mono{theme_suffix}" x="1072" font-size="12" font-weight="600" fill="{hdr_sub}" letter-spacing="1.5" text-anchor="end">SIGNAL TRANSMISSION</text>
    <circle cx="1080" cy="-4" r="4.5" fill="{accent}" opacity="0.9"/>
    <circle cx="1080" cy="-4" r="8" fill="{accent}" opacity="0.25"/>
  </g>
  <line x1="42" y1="58" x2="1158" y2="58" stroke="{track_col}" stroke-width="1.2"/>''')

    # Build lanes 1 to 5
    for lane_idx in range(1, 6):
        lane_y = LANE_Y[lane_idx]
        num_str, name_str = LANE_LABELS[lane_idx]
        lane_skills = [s for s in SKILLS if s[0] == lane_idx]

        svg_parts.append(f'''
  <!-- ════════════════════════════════════════
       LANE {num_str} — {name_str}  (Y={lane_y})
       ════════════════════════════════════════ -->
  <g transform="translate(0, {lane_y})">
    <line x1="175" y1="0" x2="1120" y2="0" stroke="{track_col}" stroke-width="2.5"/>
    <line x1="1120" y1="0" x2="1150" y2="0" stroke="{track_col}" stroke-width="2" stroke-dasharray="3,4"/>
    <circle cx="1158" cy="0" r="5.5" fill="none" stroke="{track_term}" stroke-width="2"/>
    <circle cx="1158" cy="0" r="2" fill="{track_term}"/>

    <!-- Laser bullet with tapered tail -->
    <g class="b{lane_idx}{theme_suffix}">
      <path d="M -100 0 C -60 -1.2, -20 -3.5, 0 -3.5 L 0 3.5 C -20 3.5, -60 1.2, -100 0 Z" fill="url(#laserTail{theme_suffix})"/>
      <ellipse cx="-3" cy="0" rx="10" ry="4" fill="url(#flareGrad{theme_suffix})" opacity="0.65"/>
      <circle cx="0" cy="0" r="4.5" fill="#FFFFFF" filter="url(#laserGlow{theme_suffix})"/>
      <circle cx="0" cy="0" r="2.5" fill="#FFFFFF"/>
    </g>

    <!-- Lane label -->
    <g transform="translate(42, 0)">
      <text class="mono{theme_suffix}" x="0" y="-16" font-size="22" font-weight="900" fill="{accent}" letter-spacing="0.5">{num_str}</text>
      <text class="mono{theme_suffix}" x="0" y="8" font-size="13" font-weight="700" fill="{lane_txt}" letter-spacing="1.5">{name_str}</text>
      <g transform="translate(0, 20)" fill="{track_term}">
        <rect x="0" y="0" width="3.5" height="3.5" rx="0.5"/><rect x="7" y="0" width="3.5" height="3.5" rx="0.5"/>
        <rect x="14" y="0" width="3.5" height="3.5" rx="0.5"/><rect x="21" y="0" width="3.5" height="3.5" rx="0.5"/>
        <rect x="28" y="0" width="3.5" height="3.5" rx="0.5"/>
      </g>
    </g>''')

        # Skills in this lane
        for skill in lane_skills:
            _, col_idx, skill_id, label, is_pri, icon_dark, icon_light = skill
            icon_file = icon_dark if is_dark else icon_light
            inner_svg = get_icon_svg(icon_file, is_dark)
            cx = COL_X[col_idx]

            # Card size: 76x76 for all skillicons (they have rx="60" inside 256x256)
            # For primary cards: add glowing orange border ring
            w, h = 76, 76
            x_off, y_off = -w // 2, -h // 2
            border_radius = 18

            if is_pri:
                border_elem = f'<rect class="pri{theme_suffix}" x="{x_off}" y="{y_off}" width="{w}" height="{h}" rx="{border_radius}" fill="none" stroke="{accent}" stroke-width="2.5" filter="url(#cardGlow{theme_suffix})"/>'
            else:
                card_border = "#252E3A" if is_dark else "#D0D7DE"
                border_elem = f'<rect x="{x_off}" y="{y_off}" width="{w}" height="{h}" rx="{border_radius}" fill="none" stroke="{card_border}" stroke-width="1.5"/>'

            svg_parts.append(f'''
    <!-- {label} (Col {col_idx+1}: {cx}) -->
    <g transform="translate({cx}, 0)">
      <svg x="{x_off}" y="{y_off}" width="{w}" height="{h}" viewBox="0 0 256 256">
        {inner_svg}
      </svg>
      {border_elem}
      <text class="label{theme_suffix}" x="0" y="58" font-size="16" fill="{label_txt}" text-anchor="middle">{label}</text>
    </g>''')

        # Add rocket in Lane 02
        if lane_idx == 2:
            svg_parts.append(f'''
    <!-- Spacecraft (rocket) -->
    <g transform="translate(820, 0)">
      <image href="data:image/png;base64,{rocket_b64}" x="-60" y="-25" width="120" height="50"/>
    </g>''')

        svg_parts.append('  </g>')

    svg_parts.append('</svg>\n')
    return "\n".join(svg_parts)

if __name__ == "__main__":
    dark_svg = build_toolchain(is_dark=True)
    light_svg = build_toolchain(is_dark=False)

    out_dark = os.path.join(os.path.dirname(__file__), "..", "assets", "skills", "toolchain-dark.svg")
    out_light = os.path.join(os.path.dirname(__file__), "..", "assets", "skills", "toolchain-light.svg")

    with open(out_dark, "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print(f"Generated {out_dark} ({len(dark_svg)} bytes)")

    with open(out_light, "w", encoding="utf-8") as f:
        f.write(light_svg)
    print(f"Generated {out_light} ({len(light_svg)} bytes)")
