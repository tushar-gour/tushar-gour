#!/usr/bin/env python3
import urllib.request
import os
import re
import base64
import xml.etree.ElementTree as ET

CACHE_DIR = os.path.join(os.path.dirname(__file__), "skillicons_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# List of skill definitions: (lane_idx, col_idx, id, display_label, is_primary, icon_dark, icon_light)
SKILLS = [
    # Lane 01: PRODUCT & CLIENT (Y=135)
    (1, 0, "Flutter", "Flutter", True, "Flutter-Dark.svg", "Flutter-Light.svg"),
    (1, 1, "Dart", "Dart", False, "Dart-Dark.svg", "Dart-Light.svg"),
    (1, 2, "React", "React", True, "React-Dark.svg", "React-Light.svg"),
    (1, 3, "TypeScript", "TypeScript", True, "TypeScript.svg", "TypeScript.svg"),
    (1, 4, "JavaScript", "JavaScript", False, "JavaScript.svg", "JavaScript.svg"),
    (1, 5, "HTML5", "HTML5", False, "HTML.svg", "HTML.svg"),
    (1, 6, "CSS3", "CSS3", False, "CSS.svg", "CSS.svg"),
    (1, 7, "Tailwind", "Tailwind", False, "TailwindCSS-Dark.svg", "TailwindCSS-Light.svg"),
    (1, 8, "Vite", "Vite", False, "Vite-Dark.svg", "Vite-Light.svg"),

    # Lane 02: SERVICES & LANGUAGES (Y=255)
    (2, 0, "NodeJS", "Node.js", True, "NodeJS-Dark.svg", "NodeJS-Light.svg"),
    (2, 1, "Express", "Express", False, "ExpressJS-Dark.svg", "ExpressJS-Light.svg"),
    (2, 2, "SocketIO", "Socket.IO", False, "CUSTOM_SOCKETIO", "CUSTOM_SOCKETIO"),
    (2, 3, "Java", "Java", True, "Java-Dark.svg", "Java-Light.svg"),
    (2, 4, "Python", "Python", True, "Python-Dark.svg", "Python-Light.svg"),
    (2, 5, "CPP", "C++", True, "CPP.svg", "CPP.svg"),
    (2, 6, "C", "C", False, "C.svg", "C.svg"),
    (2, 7, "Kotlin", "Kotlin", False, "Kotlin-Dark.svg", "Kotlin-Light.svg"),
    (2, 8, "Lua", "Lua", False, "Lua-Dark.svg", "Lua-Light.svg"),
    (2, 9, "JWT", "JWT", False, "CUSTOM_JWT", "CUSTOM_JWT"),

    # Lane 03: DATA & STORAGE (Y=375)
    (3, 0, "PostgreSQL", "PostgreSQL", True, "PostgreSQL-Dark.svg", "PostgreSQL-Light.svg"),
    (3, 1, "MongoDB", "MongoDB", False, "MongoDB.svg", "MongoDB.svg"),
    (3, 2, "Redis", "Redis", True, "Redis-Dark.svg", "Redis-Light.svg"),
    (3, 3, "MySQL", "MySQL", False, "MySQL-Dark.svg", "MySQL-Light.svg"),
    (3, 4, "Supabase", "Supabase", False, "Supabase-Dark.svg", "Supabase-Light.svg"),
    (3, 5, "Firebase", "Firebase", False, "Firebase-Dark.svg", "Firebase-Light.svg"),
    (3, 6, "Prisma", "Prisma", False, "Prisma.svg", "Prisma.svg"),
    (3, 7, "Drizzle", "Drizzle", False, "CUSTOM_DRIZZLE", "CUSTOM_DRIZZLE"),
    (3, 8, "SQLite", "SQLite", False, "SQLite.svg", "SQLite.svg"),

    # Lane 04: CLOUD & DELIVERY (Y=495)
    (4, 0, "AWS", "AWS", True, "AWS-Dark.svg", "AWS-Light.svg"),
    (4, 1, "GCP", "GCP", False, "GCP-Dark.svg", "GCP-Light.svg"),
    (4, 2, "Docker", "Docker", True, "Docker.svg", "Docker.svg"),
    (4, 3, "Linux", "Linux", False, "Linux-Dark.svg", "Linux-Light.svg"),
    (4, 4, "CICD", "CI/CD", False, "GithubActions-Dark.svg", "GithubActions-Light.svg"),
    (4, 5, "Cloudflare", "Cloudflare", False, "Cloudflare-Dark.svg", "Cloudflare-Light.svg"),
    (4, 6, "Vercel", "Vercel", False, "Vercel-Dark.svg", "Vercel-Light.svg"),
    (4, 7, "Netlify", "Netlify", False, "Netlify-Dark.svg", "Netlify-Light.svg"),
    (4, 8, "Render", "Render", False, "CUSTOM_RENDER", "CUSTOM_RENDER"),
    (4, 9, "Railway", "Railway", False, "CUSTOM_RAILWAY", "CUSTOM_RAILWAY"),
    (4, 10, "Hostinger", "Hostinger", False, "CUSTOM_HOSTINGER", "CUSTOM_HOSTINGER"),

    # Lane 05: PLATFORMS & ENGINES (Y=615)
    (5, 0, "Git", "Git", True, "Git.svg", "Git.svg"),
    (5, 1, "GitHub", "GitHub", False, "Github-Dark.svg", "Github-Light.svg"),
    (5, 2, "Postman", "Postman", False, "Postman.svg", "Postman.svg"),
    (5, 3, "NPM", "NPM", False, "Npm-Dark.svg", "Npm-Light.svg"),
    (5, 4, "DNS", "DNS", False, "CUSTOM_DNS", "CUSTOM_DNS"),
    (5, 5, "Windows", "Windows", False, "Windows-Dark.svg", "Windows-Light.svg"),
    (5, 6, "macOS", "macOS", False, "Apple-Dark.svg", "Apple-Light.svg"),
    (5, 7, "Figma", "Figma", False, "Figma-Dark.svg", "Figma-Light.svg"),
    (5, 8, "Blender", "Blender", False, "Blender-Dark.svg", "Blender-Light.svg"),
    (5, 9, "Unity", "Unity", True, "Unity-Dark.svg", "Unity-Light.svg"),
    (5, 10, "Roblox", "Roblox Studio", False, "RobloxStudio.svg", "RobloxStudio.svg"),
]

# 11 columns with 115px pitch
COL_X = [225, 340, 455, 570, 685, 800, 915, 1030, 1145, 1260, 1375]
LANE_Y = {1: 135, 2: 255, 3: 375, 4: 495, 5: 615}
LANE_LABELS = {
    1: ("01", "PRODUCT"),
    2: ("02", "SERVICES"),
    3: ("03", "DATA"),
    4: ("04", "DELIVERY"),
    5: ("05", "PLATFORMS &amp; ENGINES"),
}

def get_icon_svg(skill_id, filename, is_dark):
    bg = "#242938" if is_dark else "#FFFFFF"
    fg = "#FFFFFF" if is_dark else "#1F2328"

    if filename == "CUSTOM_SOCKETIO":
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<circle cx="128" cy="128" r="75" fill="none" stroke="{fg}" stroke-width="12"/>
<polygon points="148,72 120,120 142,120 108,184 136,136 114,136" fill="{fg}"/>'''

    if filename == "CUSTOM_DRIZZLE":
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<line x1="76" y1="164" x2="160" y2="72" stroke="#C5F74F" stroke-width="16" stroke-linecap="round"/>
<line x1="110" y1="184" x2="184" y2="102" stroke="#C5F74F" stroke-width="16" stroke-linecap="round"/>'''

    if filename == "CUSTOM_JWT":
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<polygon points="128,45 205,89 205,177 128,221 51,177 51,89" fill="none" stroke="#D63AFF" stroke-width="14" stroke-linejoin="round"/>
<circle cx="128" cy="133" r="28" fill="#00B9F1"/>
<polygon points="128,75 170,100 170,148 128,172 86,148 86,100" fill="none" stroke="#FFFFFF" stroke-width="6" opacity="0.6"/>'''

    if filename == "CUSTOM_RENDER":
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<path d="M70 180V76h64c30 0 52 18 52 45 0 22-14 38-34 43l38 56h-28l-34-52H96v52H70zm26-72h36c16 0 28-8 28-23 0-14-12-22-28-22H96v45z" fill="#46E3B7"/>'''

    if filename == "CUSTOM_RAILWAY":
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<rect x="58" y="70" width="140" height="116" rx="20" fill="none" stroke="{fg}" stroke-width="14"/>
<line x1="90" y1="70" x2="90" y2="186" stroke="{fg}" stroke-width="10"/>
<line x1="166" y1="70" x2="166" y2="186" stroke="{fg}" stroke-width="10"/>
<circle cx="95" cy="155" r="10" fill="#FF5EBB"/>
<circle cx="161" cy="155" r="10" fill="#FF5EBB"/>'''

    if filename == "CUSTOM_HOSTINGER":
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<path d="M78 68h28v48h44V68h28v120h-28v-48h-44v48H78V68z" fill="#673DE6"/>
<circle cx="128" cy="128" r="14" fill="#FF6B35"/>'''

    if filename == "CUSTOM_DNS":
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<rect x="68" y="60" width="120" height="38" rx="8" fill="none" stroke="{fg}" stroke-width="10"/>
<rect x="68" y="110" width="120" height="38" rx="8" fill="none" stroke="{fg}" stroke-width="10"/>
<rect x="68" y="160" width="120" height="38" rx="8" fill="none" stroke="{fg}" stroke-width="10"/>
<circle cx="92" cy="79" r="6" fill="#00D8FF"/>
<circle cx="92" cy="129" r="6" fill="#00D8FF"/>
<circle cx="92" cy="179" r="6" fill="#00D8FF"/>'''

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
    inner = match.group(1).strip() if match else content

    # Scope all IDs with skill_id to prevent collision
    ids = re.findall(r'id=["\']([^"\']+)["\']', inner)
    for id_val in set(ids):
        new_id = f"{skill_id}_{id_val}"
        inner = inner.replace(f'id="{id_val}"', f'id="{new_id}"')
        inner = inner.replace(f'id=\'{id_val}\'', f'id=\'{new_id}\'')
        inner = inner.replace(f'url(#{id_val})', f'url(#{new_id})')
        inner = inner.replace(f'url(\'#{id_val}\')', f'url(\'#{new_id}\')')
        inner = inner.replace(f'url("#{id_val}")', f'url("#{new_id}")')
        inner = inner.replace(f'href="#{id_val}"', f'href="#{new_id}"')

    return inner

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
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1520 720" width="100%" height="100%">
  <defs>
    <radialGradient id="bgVignette{theme_suffix}" cx="50%" cy="50%" r="75%">
      <stop offset="0%" stop-color="{bg_vignette}"/>
      <stop offset="100%" stop-color="{bg_vignette_outer}"/>
    </radialGradient>

    <!-- Laser bullet gradient tail -->
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
        0%   {{ transform: translateX(120px); opacity: 0; }}
        3%   {{ transform: translateX(180px); opacity: 1; }}
        56%  {{ transform: translateX(1420px); opacity: 1; }}
        62%  {{ transform: translateX(1485px); opacity: 0; }}
        100% {{ transform: translateX(1485px); opacity: 0; }}
      }}

      .b1{theme_suffix} {{ animation: bulletAnim{theme_suffix} 7.0s cubic-bezier(.25,0,.25,1) infinite; }}
      .b2{theme_suffix} {{ animation: bulletAnim{theme_suffix} 8.5s cubic-bezier(.25,0,.25,1) infinite; animation-delay: 1.8s; }}
      .b3{theme_suffix} {{ animation: bulletAnim{theme_suffix} 7.6s cubic-bezier(.25,0,.25,1) infinite; animation-delay: 3.5s; }}
      .b4{theme_suffix} {{ animation: bulletAnim{theme_suffix} 8.8s cubic-bezier(.25,0,.25,1) infinite; animation-delay: 0.8s; }}
      .b5{theme_suffix} {{ animation: bulletAnim{theme_suffix} 8.0s cubic-bezier(.25,0,.25,1) infinite; animation-delay: 2.6s; }}

      @keyframes cardPulse{theme_suffix} {{
        0%,100% {{ stroke-opacity:0.85; }}
        50% {{ stroke-opacity:1; }}
      }}
      .pri{theme_suffix} {{ animation: cardPulse{theme_suffix} 3.5s ease-in-out infinite; }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="1520" height="720" rx="14" fill="url(#bgVignette{theme_suffix})"/>
  <rect width="1520" height="720" rx="14" fill="none" stroke="{border_col}" stroke-width="1.2"/>''')

    if is_dark:
        svg_parts.append('''  <!-- Star field -->
  <g fill="#FFFFFF" opacity="0.35">
    <circle cx="82" cy="44" r="0.8"/><circle cx="220" cy="28" r="1"/><circle cx="410" cy="52" r="0.7"/>
    <circle cx="660" cy="30" r="0.9"/><circle cx="870" cy="45" r="0.7"/><circle cx="1180" cy="25" r="1"/><circle cx="1420" cy="40" r="0.8"/>
    <circle cx="135" cy="680" r="0.8"/><circle cx="490" cy="695" r="0.7"/><circle cx="940" cy="685" r="1"/>
    <circle cx="1340" cy="670" r="0.8"/><circle cx="40" cy="330" r="0.7"/><circle cx="1485" cy="340" r="0.9"/>
  </g>''')

    svg_parts.append(f'''  <!-- Left orbital arc trajectory -->
  <path d="M 170 680 C -40 520 -40 180 170 40" fill="none" stroke="{accent}" stroke-width="1.4" opacity="0.2"/>
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
    <text class="mono{theme_suffix}" x="1392" font-size="12" font-weight="600" fill="{hdr_sub}" letter-spacing="1.5" text-anchor="end">SIGNAL TRANSMISSION</text>
    <circle cx="1400" cy="-4" r="4.5" fill="{accent}" opacity="0.9"/>
    <circle cx="1400" cy="-4" r="8" fill="{accent}" opacity="0.25"/>
  </g>
  <line x1="42" y1="58" x2="1478" y2="58" stroke="{track_col}" stroke-width="1.2"/>''')

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
    <line x1="175" y1="0" x2="1440" y2="0" stroke="{track_col}" stroke-width="2.5"/>
    <line x1="1440" y1="0" x2="1470" y2="0" stroke="{track_col}" stroke-width="2" stroke-dasharray="3,4"/>
    <circle cx="1478" cy="0" r="5.5" fill="none" stroke="{track_term}" stroke-width="2"/>
    <circle cx="1478" cy="0" r="2" fill="{track_term}"/>

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
            inner_svg = get_icon_svg(skill_id, icon_file, is_dark)
            cx = COL_X[col_idx]

            # Card size: 68x68 for compact crisp grid
            w, h = 68, 68
            x_off, y_off = -w // 2, -h // 2
            border_radius = 16

            if is_pri:
                border_elem = f'<rect class="pri{theme_suffix}" x="{x_off}" y="{y_off}" width="{w}" height="{h}" rx="{border_radius}" fill="none" stroke="{accent}" stroke-width="2.2" filter="url(#cardGlow{theme_suffix})"/>'
            else:
                card_border = "#252E3A" if is_dark else "#D0D7DE"
                border_elem = f'<rect x="{x_off}" y="{y_off}" width="{w}" height="{h}" rx="{border_radius}" fill="none" stroke="{card_border}" stroke-width="1.2"/>'

            svg_parts.append(f'''
    <!-- {label} (Col {col_idx+1}: {cx}) -->
    <g transform="translate({cx}, 0)">
      <svg x="{x_off}" y="{y_off}" width="{w}" height="{h}" viewBox="0 0 256 256">
        {inner_svg}
      </svg>
      {border_elem}
      <text class="label{theme_suffix}" x="0" y="54" font-size="13" fill="{label_txt}" text-anchor="middle">{label}</text>
    </g>''')

        # Add rocket in Lane 01 where there are 9 items (at x=1320)
        if lane_idx == 1:
            svg_parts.append(f'''
    <!-- Spacecraft (rocket) -->
    <g transform="translate(1320, 0)">
      <image href="data:image/png;base64,{rocket_b64}" x="-50" y="-21" width="100" height="42"/>
    </g>''')

        svg_parts.append('  </g>')

    svg_parts.append('</svg>\n')
    return "\n".join(svg_parts)

if __name__ == "__main__":
    dark_svg = build_toolchain(is_dark=True)
    light_svg = build_toolchain(is_dark=False)

    # Validate XML with ElementTree
    try:
        ET.fromstring(dark_svg)
        print("dark_svg is VALID XML!")
    except Exception as e:
        print("dark_svg XML ERROR:", e)
        exit(1)

    try:
        ET.fromstring(light_svg)
        print("light_svg is VALID XML!")
    except Exception as e:
        print("light_svg XML ERROR:", e)
        exit(1)

    out_dark = os.path.join(os.path.dirname(__file__), "..", "assets", "skills", "toolchain-dark.svg")
    out_light = os.path.join(os.path.dirname(__file__), "..", "assets", "skills", "toolchain-light.svg")

    with open(out_dark, "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print(f"Generated {out_dark} ({len(dark_svg)} bytes)")

    with open(out_light, "w", encoding="utf-8") as f:
        f.write(light_svg)
    print(f"Generated {out_light} ({len(light_svg)} bytes)")
