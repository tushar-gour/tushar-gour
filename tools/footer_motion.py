"""Morph independent golden SVG paths; never transform the contact artwork."""
import math
import re
from pathlib import Path
from xml.etree import ElementTree

TAU = 2 * math.pi
FRAMES = 48
DURATION = 7
STEP = 108.6


def y_at(x, u, t, extra=0):
    phase = TAU * t
    center = (566 + (42 + 7 * math.sin(phase + .6)) * math.sin(TAU*x/1450 - phase + .3)
              + 17 * math.sin(TAU*x/950 - 2*phase + .5)
              + 8 * math.sin(TAU*x/2100 - 3*phase - .4))
    spread = 38 * math.cos(TAU*x/1350 - phase + .9) + 12 * math.sin(TAU*x/1000 - 2*phase + .3)
    return center + (2*u-1)*spread + 9*math.sin(math.pi*u)*math.sin(TAU*x/1100 - 2*phase + u) + extra


def ribbon_path(x, u, t, extra=0):
    """Fixed horizontal nodes with animated heights and continuous slopes."""
    nodes = [x+i*STEP for i in range(-1,7)]
    y = [y_at(v,u,t,extra) for v in nodes]
    slope = [(y_at(v+.1,u,t,extra)-y_at(v-.1,u,t,extra))/.2 for v in nodes]
    parts = [f"M {nodes[0]:.1f} {y[0]:.1f}"]
    for i in range(7):
        a,b = nodes[i:i+2]
        h = (b-a)/3
        parts.append(f"C {a+h:.1f} {y[i]+h*slope[i]:.1f} {b-h:.1f} {y[i+1]-h*slope[i+1]:.1f} {b:.1f} {y[i+1]:.1f}")
    return " ".join(parts)


def animated(x,u,attrs):
    frames = [ribbon_path(x,u,k/FRAMES) for k in range(FRAMES)]
    frames.append(frames[0])
    values = ";".join(frames)
    return f'<path {attrs} d="{frames[0]}"><animate attributeName="d" values="{values}" dur="{DURATION}s" repeatCount="indefinite" calcMode="linear"/></path>'


def wave_motion(x, theme):
    dark = theme == "dark"
    paper, bottom = ("#0b0a0c","#09090b") if dark else ("#f9f6f0","#faf7f2")
    colors = ["#8e420e","#fff2bd","#f28c20","#fff2bd","#a3551c","#fff2bd","#8e420e"] if dark else ["#b98b59","#824313","#b6742c","#743b13","#b88a55","#824313","#c19b74"]
    grad = "".join(f'<stop offset="{p}" stop-color="{c}"/>' for p,c in zip([0,.19,.32,.46,.61,.76,1],colors))
    defs = f'''<linearGradient id="base" gradientUnits="userSpaceOnUse" x1="0" y1="430" x2="0" y2="724"><stop stop-color="{paper}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>
<linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="0" y1="426" x2="0" y2="466"><stop stop-color="white" stop-opacity="0"/><stop offset="1" stop-color="white"/></linearGradient>
<mask id="replace-wave" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="{x}" y="420" width="543" height="304"><rect x="{x}" y="420" width="543" height="304" fill="url(#fade)"/></mask>
<clipPath id="wave-region" clipPathUnits="userSpaceOnUse"><rect x="{x}" y="444" width="543" height="280"/></clipPath>
<linearGradient id="gold" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="2172" y2="0">{grad}</linearGradient>
<filter id="glow" filterUnits="userSpaceOnUse" x="{x-120}" y="420" width="783" height="304" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="{9 if dark else 5}" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'''
    lines = []
    for i in range(24):
        u = (i+1)/25
        lines.append(animated(x,u,f'stroke-width="{1.15 if i%5==0 else .8}" opacity="{.23+(1-u)*.12}"'))
    lines.append(animated(x,0,f'stroke-width="{3.3 if dark else 2.5}" filter="url(#glow)"'))
    lines.append(animated(x,1,'stroke-width="1.6" opacity=".85"'))
    threads = "\n".join(lines)
    overlay = f'<g class="wave-motion"><rect x="{x}" y="420" width="543" height="304" fill="url(#base)" mask="url(#replace-wave)"/><g clip-path="url(#wave-region)"><g fill="none" stroke="url(#gold)" stroke-linejoin="round">{threads}</g></g></g>'
    return defs, overlay


def animate_footer(svg, x, theme=None):
    """Install an independent vector layer over the original static artwork."""
    if theme is None:
        theme = "light" if 'stroke="#C8B7A3"' in svg else "dark"
    defs, overlay = wave_motion(x, theme)
    match = re.search(r'<g clip-path="url\(#frame\)">(<image [^>]+/>)</g>', svg)
    if match:
        image = match[1].replace("<image ", '<image id="artwork" ', 1)
        svg = svg.replace("</defs>", image+"\n"+defs+"</defs>", 1)
        return svg.replace(match[0], '<style>@media (prefers-reduced-motion: reduce) {.wave-motion {display:none}}</style>\n<g clip-path="url(#frame)"><use xlink:href="#artwork"/>\n'+overlay+"\n</g>",1)
    start = svg.index('<linearGradient id="base"') if '<linearGradient id="base"' in svg else svg.index('<linearGradient id="waveMask"')
    defs_end = svg.index("</defs>", start)
    overlay_start = svg.index('<g class="wave-motion"')
    overlay_end = svg.rindex("\n</g>\n<rect")  # start of outer clipped group close
    return svg[:start]+defs+svg[defs_end:overlay_start]+overlay+svg[overlay_end:]


def refresh_existing():
    root = Path(__file__).resolve().parents[1]
    updates = []
    for theme in ("dark","light"):
        for i,key in enumerate(("github","linkedin","email","resume")):
            path = root/"assets"/"footer"/f"connect-{key}-{theme}.svg"
            old = path.read_text(encoding="utf-8")
            new = animate_footer(old, i*543, theme)
            payload = r'data:image/png;base64,([^"]+)'
            assert re.search(payload,new)[1] == re.search(payload,old)[1]
            assert new.count('<animate attributeName="d"') == 26 and "<animateTransform" not in new
            ElementTree.fromstring(new)
            updates.append((path,new))
    for path,new in updates:
        path.write_text(new,encoding="utf-8")
    print("Verified 8 independently morphing vector ribbons and unchanged original artwork.")


if __name__ == "__main__":
    refresh_existing()
