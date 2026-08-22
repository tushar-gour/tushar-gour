#!/usr/bin/env python3
"""
tools/build_all_skills_toolchain.py

Builds the 6-lane animated Engineering Stack SVGs (Dark + Light):
- 01: CLIENT & UI (Flutter, Dart, React, TypeScript, JavaScript, HTML5, CSS3, Tailwind CSS, Vite)
- 02: BACKEND & LANGUAGES (Node.js, Express, Socket.IO, Java, Python, C++, C, Kotlin, Lua, JWT)
- 03: DATA & PERSISTENCE (PostgreSQL, MongoDB, Redis, MySQL, SQLite, Prisma, Drizzle, Supabase, Firebase)
- 04: CLOUD & DELIVERY (AWS, GCP, Docker, Linux, Cloudflare, CI/CD, Vercel, Netlify, Render, Railway, Hostinger)
- 05: TOOLS & CREATIVE (Git, GitHub, Postman, npm, DNS, Windows, macOS, Figma, Blender, Unity, Roblox Studio)
- 06: AI (ChatGPT / Codex, Claude / Code, Gemini / AGY, DeepSeek, Perplexity, Manus, MiniMax, Blackbox AI)
"""

import urllib.request
import os
import re
import base64
import xml.etree.ElementTree as ET

CACHE_DIR = os.path.join(os.path.dirname(__file__), "skillicons_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# List of skill definitions: (lane_idx, col_idx, id, display_label, is_primary, icon_dark, icon_light)
SKILLS = [
    # ─── Lane 01: CLIENT & UI (Y=135) ───
    (1, 0, "Flutter", "Flutter", True, "Flutter-Dark.svg", "Flutter-Light.svg"),
    (1, 1, "Dart", "Dart", False, "Dart-Dark.svg", "Dart-Light.svg"),
    (1, 2, "React", "React", True, "React-Dark.svg", "React-Light.svg"),
    (1, 3, "TypeScript", "TypeScript", True, "TypeScript.svg", "TypeScript.svg"),
    (1, 4, "JavaScript", "JavaScript", False, "JavaScript.svg", "JavaScript.svg"),
    (1, 5, "HTML5", "HTML5", False, "HTML.svg", "HTML.svg"),
    (1, 6, "CSS3", "CSS3", False, "CSS.svg", "CSS.svg"),
    (1, 7, "Tailwind", "Tailwind CSS", False, "TailwindCSS-Dark.svg", "TailwindCSS-Light.svg"),
    (1, 8, "Vite", "Vite", False, "Vite-Dark.svg", "Vite-Light.svg"),

    # ─── Lane 02: BACKEND & LANGUAGES (Y=255) ───
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

    # ─── Lane 03: DATA & PERSISTENCE (Y=375) ───
    (3, 0, "PostgreSQL", "PostgreSQL", True, "PostgreSQL-Dark.svg", "PostgreSQL-Light.svg"),
    (3, 1, "MongoDB", "MongoDB", False, "MongoDB.svg", "MongoDB.svg"),
    (3, 2, "Redis", "Redis", True, "Redis-Dark.svg", "Redis-Light.svg"),
    (3, 3, "MySQL", "MySQL", False, "MySQL-Dark.svg", "MySQL-Light.svg"),
    (3, 4, "SQLite", "SQLite", False, "SQLite.svg", "SQLite.svg"),
    (3, 5, "Prisma", "Prisma", False, "Prisma.svg", "Prisma.svg"),
    (3, 6, "Drizzle", "Drizzle", False, "CUSTOM_DRIZZLE", "CUSTOM_DRIZZLE"),
    (3, 7, "Supabase", "Supabase", False, "Supabase-Dark.svg", "Supabase-Light.svg"),
    (3, 8, "Firebase", "Firebase", False, "Firebase-Dark.svg", "Firebase-Light.svg"),

    # ─── Lane 04: CLOUD & DELIVERY (Y=495) ───
    (4, 0, "AWS", "AWS", True, "AWS-Dark.svg", "AWS-Light.svg"),
    (4, 1, "GCP", "GCP", False, "GCP-Dark.svg", "GCP-Light.svg"),
    (4, 2, "Docker", "Docker", True, "Docker.svg", "Docker.svg"),
    (4, 3, "Linux", "Linux", False, "Linux-Dark.svg", "Linux-Light.svg"),
    (4, 4, "Cloudflare", "Cloudflare", False, "Cloudflare-Dark.svg", "Cloudflare-Light.svg"),
    (4, 5, "CICD", "CI/CD", False, "GithubActions-Dark.svg", "GithubActions-Light.svg"),
    (4, 6, "Vercel", "Vercel", False, "Vercel-Dark.svg", "Vercel-Light.svg"),
    (4, 7, "Netlify", "Netlify", False, "Netlify-Dark.svg", "Netlify-Light.svg"),
    (4, 8, "Render", "Render", False, "CUSTOM_RENDER", "CUSTOM_RENDER"),
    (4, 9, "Railway", "Railway", False, "CUSTOM_RAILWAY", "CUSTOM_RAILWAY"),
    (4, 10, "Hostinger", "Hostinger", False, "CUSTOM_HOSTINGER", "CUSTOM_HOSTINGER"),

    # ─── Lane 05: TOOLS & CREATIVE (Y=615) ───
    (5, 0, "Git", "Git", True, "Git.svg", "Git.svg"),
    (5, 1, "GitHub", "GitHub", False, "Github-Dark.svg", "Github-Light.svg"),
    (5, 2, "Postman", "Postman", False, "Postman.svg", "Postman.svg"),
    (5, 3, "NPM", "npm", False, "Npm-Dark.svg", "Npm-Light.svg"),
    (5, 4, "DNS", "DNS", False, "CUSTOM_DNS", "CUSTOM_DNS"),
    (5, 5, "Windows", "Windows", False, "Windows-Dark.svg", "Windows-Light.svg"),
    (5, 6, "macOS", "macOS", False, "CUSTOM_MACOS", "CUSTOM_MACOS"),
    (5, 7, "Figma", "Figma", False, "Figma-Dark.svg", "Figma-Light.svg"),
    (5, 8, "Blender", "Blender", False, "Blender-Dark.svg", "Blender-Light.svg"),
    (5, 9, "Unity", "Unity", True, "Unity-Dark.svg", "Unity-Light.svg"),
    (5, 10, "Roblox", "Roblox Studio", False, "RobloxStudio.svg", "RobloxStudio.svg"),

    # ─── Lane 06: AI (Y=735) ───
    (6, 0, "ChatGPT", "ChatGPT / Codex", True, "CUSTOM_OPENAI", "CUSTOM_OPENAI"),
    (6, 1, "Claude", "Claude / Code", True, "CUSTOM_CLAUDE", "CUSTOM_CLAUDE"),
    (6, 2, "Gemini", "Gemini / AGY", True, "CUSTOM_GEMINI", "CUSTOM_GEMINI"),
    (6, 3, "DeepSeek", "DeepSeek", True, "CUSTOM_DEEPSEEK", "CUSTOM_DEEPSEEK"),
    (6, 4, "Perplexity", "Perplexity", False, "CUSTOM_PERPLEXITY", "CUSTOM_PERPLEXITY"),
    (6, 5, "Manus", "Manus", False, "CUSTOM_MANUS", "CUSTOM_MANUS"),
    (6, 6, "MiniMax", "MiniMax", False, "CUSTOM_MINIMAX", "CUSTOM_MINIMAX"),
    (6, 7, "Blackbox", "Blackbox AI", False, "CUSTOM_BLACKBOX", "CUSTOM_BLACKBOX"),
]

# 11 columns with 115px pitch
COL_X = [225, 340, 455, 570, 685, 800, 915, 1030, 1145, 1260, 1375]
LANE_Y = {1: 135, 2: 255, 3: 375, 4: 495, 5: 615, 6: 735}

# Category labels
LANE_LABELS = {
    1: ("01", "CLIENT &amp; UI", ""),
    2: ("02", "BACKEND &amp;", "LANGUAGES"),
    3: ("03", "DATA &amp;", "PERSISTENCE"),
    4: ("04", "CLOUD &amp;", "DELIVERY"),
    5: ("05", "TOOLS &amp;", "CREATIVE"),
    6: ("06", "AI", ""),
}

def make_badge_from_path(path_d, fill_color, bg_color="#242938", scale=6.6667, translate=(48, 48)):
    return f'''<rect width="256" height="256" rx="60" fill="{bg_color}"/>
<g transform="translate({translate[0]}, {translate[1]}) scale({scale})">
  <path d="{path_d}" fill="{fill_color}"/>
</g>'''

def get_icon_svg(skill_id, filename, is_dark):
    bg = "#242938" if is_dark else "#FFFFFF"
    fg = "#FFFFFF" if is_dark else "#1F2328"

    # AI Tools
    if filename == "CUSTOM_OPENAI":
        openai_d = "M9.205 8.658v-2.26c0-.19.072-.333.238-.428l4.543-2.616c.619-.357 1.356-.523 2.117-.523 2.854 0 4.662 2.212 4.662 4.566 0 .167 0 .357-.024.547l-4.71-2.759a.797.797 0 00-.856 0l-5.97 3.473zm10.609 8.8V12.06c0-.333-.143-.57-.429-.737l-5.97-3.473 1.95-1.118a.433.433 0 01.476 0l4.543 2.617c1.309.76 2.189 2.378 2.189 3.948 0 1.808-1.07 3.473-2.76 4.163zM7.802 12.703l-1.95-1.142c-.167-.095-.239-.238-.239-.428V5.899c0-2.545 1.95-4.472 4.591-4.472 1 0 1.927.333 2.712.928L8.23 5.067c-.285.166-.428.404-.428.737v6.898zM12 15.128l-2.795-1.57v-3.33L12 8.658l2.795 1.57v3.33L12 15.128zm1.796 7.23c-1 0-1.927-.332-2.712-.927l4.686-2.712c.285-.166.428-.404.428-.737v-6.898l1.974 1.142c.167.095.238.238.238.428v5.233c0 2.545-1.974 4.472-4.614 4.472zm-5.637-5.303l-4.544-2.617c-1.308-.761-2.188-2.378-2.188-3.948A4.482 4.482 0 014.21 6.327v5.423c0 .333.143.571.428.738l5.947 3.449-1.95 1.118a.432.432 0 01-.476 0zm-.262 3.9c-2.688 0-4.662-2.021-4.662-4.519 0-.19.024-.38.047-.57l4.686 2.71c.286.167.571.167.856 0l5.97-3.448v2.26c0 .19-.07.333-.237.428l-4.543 2.616c-.619.357-1.356.523-2.117.523zm5.899 2.83a5.947 5.947 0 005.827-4.756C22.287 18.339 24 15.84 24 13.296c0-1.665-.713-3.282-1.998-4.448.119-.5.19-.999.19-1.498 0-3.401-2.759-5.947-5.946-5.947-.642 0-1.26.095-1.88.31A5.962 5.962 0 0010.205 0a5.947 5.947 0 00-5.827 4.757C1.713 5.447 0 7.945 0 10.49c0 1.666.713 3.283 1.998 4.448-.119.5-.19 1-.19 1.499 0 3.401 2.759 5.946 5.946 5.946.642 0 1.26-.095 1.88-.309a5.96 5.96 0 004.162 1.713z"
        return make_badge_from_path(openai_d, "#10A37F" if is_dark else "#10A37F", bg)

    if filename == "CUSTOM_CLAUDE":
        claude_path = os.path.join(CACHE_DIR, "claude.svg")
        with open(claude_path, "r", encoding="utf-8") as f:
            claude_txt = f.read()
        claude_d = re.search(r'd="([^"]+)"', claude_txt).group(1)
        return make_badge_from_path(claude_d, "#D97706" if is_dark else "#D97706", bg)

    if filename == "CUSTOM_GEMINI":
        gemini_d = "M11.04 19.32Q12 21.51 12 24q0-2.49.93-4.68.96-2.19 2.58-3.81t3.81-2.55Q21.51 12 24 12q-2.49 0-4.68-.93a12.3 12.3 0 0 1-3.81-2.58 12.3 12.3 0 0 1-2.58-3.81Q12 2.49 12 0q0 2.49-.96 4.68-.93 2.19-2.55 3.81a12.3 12.3 0 0 1-3.81 2.58Q2.49 12 0 12q2.49 0 4.68.96 2.19.93 3.81 2.55t2.55 3.81"
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<defs>
  <linearGradient id="{skill_id}_geminiGrad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#4E75F8"/>
    <stop offset="50%" stop-color="#9B72CB"/>
    <stop offset="100%" stop-color="#F37380"/>
  </linearGradient>
</defs>
<g transform="translate(48, 48) scale(6.6667)">
  <path d="{gemini_d}" fill="url(#{skill_id}_geminiGrad)"/>
</g>'''

    if filename == "CUSTOM_DEEPSEEK":
        deepseek_path = os.path.join(CACHE_DIR, "deepseek.svg")
        with open(deepseek_path, "r", encoding="utf-8") as f:
            deepseek_txt = f.read()
        deepseek_d = re.search(r'd="([^"]+)"', deepseek_txt).group(1)
        return make_badge_from_path(deepseek_d, "#0066FF" if is_dark else "#0066FF", bg)

    if filename == "CUSTOM_PERPLEXITY":
        perpl_path = os.path.join(CACHE_DIR, "perplexity.svg")
        with open(perpl_path, "r", encoding="utf-8") as f:
            perpl_txt = f.read()
        perpl_d = re.search(r'd="([^"]+)"', perpl_txt).group(1)
        return make_badge_from_path(perpl_d, "#20B2AA" if is_dark else "#008080", bg)

    if filename == "CUSTOM_MINIMAX":
        minimax_path = os.path.join(CACHE_DIR, "minimax.svg")
        with open(minimax_path, "r", encoding="utf-8") as f:
            minimax_txt = f.read()
        minimax_d = re.search(r'd="([^"]+)"', minimax_txt).group(1)
        return make_badge_from_path(minimax_d, "#E03131" if is_dark else "#E03131", bg)

    if filename == "CUSTOM_MANUS":
        manus_path = os.path.join(CACHE_DIR, "manus.svg")
        with open(manus_path, "r", encoding="utf-8") as f:
            manus_txt = f.read()
        match = re.search(r'<svg[^>]*>(.*)</svg>', manus_txt, re.DOTALL)
        inner = match.group(1).strip() if match else manus_txt
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<g transform="translate(48, 48) scale(0.625)">
  {inner}
</g>'''

    if filename == "CUSTOM_BLACKBOX":
        blackbox_d1 = "M75.5572 34.3324C88.7347 42.2162 102.993 50.3876 115.919 58.5073C94.6995 70.7628 61.0157 88.8504 41.4509 101.802C41.4503 150.926 42.9122 209.169 41.3355 257.576C32.3066 252.354 8.25927 237.57 0 233.852V77.9571C20.5984 65.811 55.1389 44.4756 75.5572 34.3324Z"
        blackbox_d2 = "M134.304 0H135.204C145.166 7.08673 167.646 19.5747 178.714 26.1553C210.351 44.8007 241.884 63.6219 273.312 82.6181C274.071 107.793 273.415 136.913 273.431 162.379C260.716 170.359 244.62 179.1 231.408 186.761L231.369 104.969L94.2639 23.2964C107.679 15.6494 121.027 7.88363 134.304 0Z"
        blackbox_d3 = "M272.205 185.262C274.309 187.586 273.457 225.275 273.439 231.532C259.764 238.431 240.572 250.373 226.585 258.464L134.56 311.71C110.707 297.246 84.9748 282.861 60.7132 268.858C59.535 264.734 60.1441 227.775 60.2148 221.383L134.926 264.627C149.348 255.575 167.098 245.87 182.016 237.244L272.205 185.262Z"
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<g transform="translate(48, 48) scale(0.512)">
  <path d="{blackbox_d1}" fill="#00FF9D"/>
  <path d="{blackbox_d2}" fill="{fg}"/>
  <path d="{blackbox_d3}" fill="#00C476"/>
</g>'''

    # Other tools
    if filename == "CUSTOM_RENDER":
        render_d = "M18.263.007c-3.121-.147-5.744 2.109-6.192 5.082-.018.138-.045.272-.067.405-.696 3.703-3.936 6.507-7.827 6.507-1.388 0-2.691-.356-3.825-.979a.2024.2024 0 0 0-.302.178V24H12v-8.999c0-1.656 1.338-3 2.987-3h2.988c3.382 0 6.103-2.817 5.97-6.244-.12-3.084-2.61-5.603-5.682-5.75"
        return make_badge_from_path(render_d, "#46E3B7" if is_dark else "#14B8A6", bg)

    if filename == "CUSTOM_RAILWAY":
        railway_d = "M.113 10.27A13.026 13.026 0 000 11.48h18.23c-.064-.125-.15-.237-.235-.347-3.117-4.027-4.793-3.677-7.19-3.78-.8-.034-1.34-.048-4.524-.048-1.704 0-3.555.005-5.358.01-.234.63-.459 1.24-.567 1.737h9.342v1.216H.113v.002zm18.26 2.426H.009c.02.326.05.645.094.961h16.955c.754 0 1.179-.429 1.315-.96zm-17.318 4.28s2.81 6.902 10.93 7.024c4.855 0 9.027-2.883 10.92-7.024H1.056zM11.988 0C7.5 0 3.593 2.466 1.531 6.108l4.75-.005v-.002c3.71 0 3.849.016 4.573.047l.448.016c1.563.052 3.485.22 4.996 1.364.82.621 2.007 1.99 2.712 2.965.654.902.842 1.94.396 2.934-.408.914-1.289 1.458-2.353 1.458H.391s.099.42.249.886h22.748A12.026 12.026 0 0024 12.005C24 5.377 18.621 0 11.988 0z"
        return make_badge_from_path(railway_d, fg, bg)

    if filename == "CUSTOM_HOSTINGER":
        hostinger_d = "M16.415 0v7.16l5.785 3.384V2.949L16.415 0ZM1.8 0v11.237h18.815L14.89 8.09l-7.457-.003V3.024L1.8 0Zm14.615 20.894v-5.019l-7.514-.005c.007.033-5.82-3.197-5.82-3.197l19.119.091V24l-5.785-3.106ZM1.8 13.551v7.343l5.633 2.949v-6.988L1.8 13.551Z"
        return make_badge_from_path(hostinger_d, "#673DE6", bg)

    if filename == "CUSTOM_SOCKETIO":
        socket_d = "M11.9362.0137a12.1694 12.1694 0 00-2.9748.378C4.2816 1.5547.5678 5.7944.0918 10.6012c-.59 4.5488 1.7079 9.2856 5.6437 11.6345 3.8608 2.4179 9.0926 2.3199 12.8734-.223 3.3969-2.206 5.5118-6.2277 5.3858-10.2845-.058-4.0159-2.31-7.9167-5.7588-9.9796C16.354.5876 14.1431.0047 11.9362.0137zm-.063 1.696c4.9448-.007 9.7886 3.8137 10.2815 8.9245.945 5.6597-3.7528 11.4125-9.4875 11.5795-5.4538.544-10.7245-4.0798-10.8795-9.5566-.407-4.4338 2.5159-8.8346 6.6977-10.2995a9.1126 9.1126 0 013.3878-.647zm5.0908 3.2248c-2.6869 2.0849-5.2598 4.3078-7.8886 6.4567 1.2029.017 2.4118.016 3.6208.01 1.41-2.165 2.8589-4.3008 4.2678-6.4667zm-5.6647 7.6536c-1.41 2.166-2.86 4.3088-4.2699 6.4737 2.693-2.0799 5.2548-4.3198 7.9017-6.4557a255.4132 255.4132 0 00-3.6318-.018z"
        return make_badge_from_path(socket_d, fg, bg)

    if filename == "CUSTOM_DRIZZLE":
        drizzle_d = "M5.353 11.823a1.036 1.036 0 0 0-.395-1.422 1.063 1.063 0 0 0-1.437.399L.138 16.702a1.035 1.035 0 0 0 .395 1.422 1.063 1.063 0 0 0 1.437-.398l3.383-5.903Zm11.216 0a1.036 1.036 0 0 0-.394-1.422 1.064 1.064 0 0 0-1.438.399l-3.382 5.902a1.036 1.036 0 0 0 .394 1.422c.506.283 1.15.104 1.438-.398l3.382-5.903Zm7.293-4.525a1.036 1.036 0 0 0-.395-1.422 1.062 1.062 0 0 0-1.437.399l-3.383 5.902a1.036 1.036 0 0 0 .395 1.422 1.063 1.063 0 0 0 1.437-.399l3.383-5.902Zm-11.219 0a1.035 1.035 0 0 0-.394-1.422 1.064 1.064 0 0 0-1.438.398l-3.382 5.903a1.036 1.036 0 0 0 .394 1.422c.506.282 1.15.104 1.438-.399l3.382-5.902Z"
        return make_badge_from_path(drizzle_d, "#C5F74F", bg)

    if filename == "CUSTOM_JWT":
        jwt_d = "M10.2 0v6.456L12 8.928l1.8-2.472V0zm3.6 6.456v3.072l2.904-.96L20.52 3.36l-2.928-2.136zm2.904 2.112l-1.8 2.496 2.928.936 6.144-1.992-1.128-3.432zM17.832 12l-2.928.936 1.8 2.496 6.144 1.992 1.128-3.432zm-1.128 3.432l-2.904-.96v3.072l3.792 5.232 2.928-2.136zM13.8 17.544L12 15.072l-1.8 2.472V24h3.6zm-3.6 0v-3.072l-2.904.96L3.48 20.64l2.928 2.136zm-2.904-2.112l1.8-2.496L6.168 12 .024 13.992l1.128 3.432zM6.168 12l2.928-.936-1.8-2.496-6.144-1.992-1.128 3.432zm1.128-3.432l2.904.96V6.456L6.408 1.224 3.48 3.36Z"
        return make_badge_from_path(jwt_d, "#D63AFF", bg)

    if filename == "CUSTOM_DNS":
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<circle cx="128" cy="128" r="68" fill="none" stroke="{fg}" stroke-width="8"/>
<ellipse cx="128" cy="128" rx="34" ry="68" fill="none" stroke="{fg}" stroke-width="8"/>
<line x1="60" y1="128" x2="196" y2="128" stroke="{fg}" stroke-width="8"/>
<line x1="72" y1="94" x2="184" y2="94" stroke="{fg}" stroke-width="7"/>
<line x1="72" y1="162" x2="184" y2="162" stroke="{fg}" stroke-width="7"/>
<line x1="128" y1="60" x2="128" y2="196" stroke="{fg}" stroke-width="8"/>'''

    if filename == "CUSTOM_MACOS":
        return f'''<rect width="256" height="256" rx="60" fill="{bg}"/>
<g transform="translate(48, 48)">
  <rect width="160" height="160" rx="36" fill="#D0D7DE"/>
  <path d="M 80 0 A 80 80 0 0 1 160 80 L 160 124 A 36 36 0 0 1 124 160 L 80 160 Z" fill="#90A4AE"/>
  <rect x="36" y="52" width="16" height="28" rx="8" fill="#1E293B"/>
  <rect x="108" y="52" width="16" height="28" rx="8" fill="#1E293B"/>
  <path d="M 80 40 L 80 96 L 96 96" fill="none" stroke="#1E293B" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M 44 116 Q 80 148 116 116" fill="none" stroke="#1E293B" stroke-width="8" stroke-linecap="round"/>
</g>'''

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

    match = re.search(r'<svg[^>]*>(.*)</svg>', content, re.DOTALL)
    inner = match.group(1).strip() if match else content

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
    hdr_title_color = "#FFFFFF" if is_dark else "#0D1117"

    rocket_path = os.path.join(os.path.dirname(__file__), "..", "assets", "skills", "rocket.png")
    with open(rocket_path, "rb") as f:
        rocket_b64 = base64.b64encode(f.read()).decode("utf-8")

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1520 835" width="100%" height="100%">
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
      <stop offset="100%" stop-color="{accent}" stop-opacity="0.0"/>
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
      .b6{theme_suffix} {{ animation: bulletAnim{theme_suffix} 7.8s cubic-bezier(.25,0,.25,1) infinite; animation-delay: 4.2s; }}

      @keyframes cardPulse{theme_suffix} {{
        0%,100% {{ stroke-opacity:0.85; }}
        50% {{ stroke-opacity:1; }}
      }}
      .pri{theme_suffix} {{ animation: cardPulse{theme_suffix} 3.5s ease-in-out infinite; }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="1520" height="835" rx="14" fill="url(#bgVignette{theme_suffix})"/>
  <rect width="1520" height="835" rx="14" fill="none" stroke="{border_col}" stroke-width="1.2"/>''')

    if is_dark:
        svg_parts.append('''  <!-- Star field -->
  <g fill="#FFFFFF" opacity="0.35">
    <circle cx="82" cy="44" r="0.8"/><circle cx="220" cy="28" r="1"/><circle cx="410" cy="52" r="0.7"/>
    <circle cx="660" cy="30" r="0.9"/><circle cx="870" cy="45" r="0.7"/><circle cx="1180" cy="25" r="1"/><circle cx="1420" cy="40" r="0.8"/>
    <circle cx="135" cy="790" r="0.8"/><circle cx="490" cy="805" r="0.7"/><circle cx="940" cy="795" r="1"/>
    <circle cx="1340" cy="780" r="0.8"/><circle cx="40" cy="430" r="0.7"/><circle cx="1485" cy="440" r="0.9"/>
  </g>''')

    svg_parts.append(f'''  <!-- Left orbital arc trajectory -->
  <path d="M 170 790 C -40 600 -40 180 170 40" fill="none" stroke="{accent}" stroke-width="1.4" opacity="0.2"/>
  <g transform="translate(90, 435)">
    <circle cx="0" cy="0" r="5" fill="url(#flareGrad{theme_suffix})" opacity="0.9"/>
    <circle cx="0" cy="0" r="3" fill="{accent}"/>
    <line x1="-14" y1="0" x2="14" y2="0" stroke="{accent}" stroke-width="1.2" opacity="0.6"/>
    <line x1="0" y1="-14" x2="0" y2="14" stroke="{accent}" stroke-width="1.2" opacity="0.6"/>
  </g>

  <!-- Header -->
  <g transform="translate(42, 42)">
    <text class="mono{theme_suffix}" x="0" y="2" font-size="22" font-weight="900" fill="{hdr_title_color}" letter-spacing="2">ENGINEERING STACK</text>
    <text class="mono{theme_suffix}" x="300" y="0" font-size="13" font-weight="600" fill="{hdr_sub}" letter-spacing="1.5">/ TOOLS ACROSS THE SOFTWARE DELIVERY PATH</text>
    <text class="mono{theme_suffix}" x="1392" y="0" font-size="12" font-weight="600" fill="{hdr_sub}" letter-spacing="1.5" text-anchor="end">SIGNAL TRANSMISSION</text>
    <circle cx="1400" cy="-4" r="4.5" fill="{accent}" opacity="0.9"/>
    <circle cx="1400" cy="-4" r="8" fill="{accent}" opacity="0.25"/>
  </g>
  <line x1="42" y1="58" x2="1478" y2="58" stroke="{track_col}" stroke-width="1.2"/>''')

    # Build lanes 1 to 6
    for lane_idx in range(1, 7):
        lane_y = LANE_Y[lane_idx]
        num_str, line1, line2 = LANE_LABELS[lane_idx]
        lane_skills = [s for s in SKILLS if s[0] == lane_idx]

        if line2:
            label_markup = f'''<text class="mono{theme_suffix}" x="0" y="-18" font-size="22" font-weight="900" fill="{accent}" letter-spacing="0.5">{num_str}</text>
      <text class="mono{theme_suffix}" x="0" y="2" font-size="12" font-weight="700" fill="{lane_txt}" letter-spacing="1.5">{line1}</text>
      <text class="mono{theme_suffix}" x="0" y="17" font-size="12" font-weight="700" fill="{lane_txt}" letter-spacing="1.5">{line2}</text>
      <g transform="translate(0, 26)" fill="{track_term}">
        <rect x="0" y="0" width="3.5" height="3.5" rx="0.5"/><rect x="7" y="0" width="3.5" height="3.5" rx="0.5"/>
        <rect x="14" y="0" width="3.5" height="3.5" rx="0.5"/><rect x="21" y="0" width="3.5" height="3.5" rx="0.5"/>
        <rect x="28" y="0" width="3.5" height="3.5" rx="0.5"/>
      </g>'''
        else:
            label_markup = f'''<text class="mono{theme_suffix}" x="0" y="-18" font-size="22" font-weight="900" fill="{accent}" letter-spacing="0.5">{num_str}</text>
      <text class="mono{theme_suffix}" x="0" y="6" font-size="12.5" font-weight="700" fill="{lane_txt}" letter-spacing="1.5">{line1}</text>
      <g transform="translate(0, 18)" fill="{track_term}">
        <rect x="0" y="0" width="3.5" height="3.5" rx="0.5"/><rect x="7" y="0" width="3.5" height="3.5" rx="0.5"/>
        <rect x="14" y="0" width="3.5" height="3.5" rx="0.5"/><rect x="21" y="0" width="3.5" height="3.5" rx="0.5"/>
        <rect x="28" y="0" width="3.5" height="3.5" rx="0.5"/>
      </g>'''

        svg_parts.append(f'''
  <!-- ════════════════════════════════════════
       LANE {num_str} — {line1} {line2}  (Y={lane_y})
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
      {label_markup}
    </g>''')

        # Skills in this lane
        for skill in lane_skills:
            _, col_idx, skill_id, label, is_pri, icon_dark, icon_light = skill
            icon_file = icon_dark if is_dark else icon_light
            inner_svg = get_icon_svg(skill_id, icon_file, is_dark)
            cx = COL_X[col_idx]

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

        # Rocket placement in Lane 01 (at x=1320)
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
