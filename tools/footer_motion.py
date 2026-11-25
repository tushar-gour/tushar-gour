"""Build one full-width animated ribbon beneath static clickable contact tiles."""
import math
import re
from pathlib import Path
from xml.etree import ElementTree

TAU = 2 * math.pi
FRAMES = 48
DURATION = 16
STEP = 144.8


def y_at(x, u, t, extra=0):
    # Standing modes change amplitude and polarity; the soft travelling component
    # adds flow without shifting the whole ribbon. Strands swap vertical order.
    p = TAU * t
    q = TAU * x / 1800
    center = (579 + 32*math.sin(q+.35)*math.cos(p)
              + 19*math.cos(TAU*x/2350-.6)*math.sin(p)
              + 8*math.sin(TAU*x/1220-p+.4))
    spread = (38*math.sin(q+.75)*math.cos(p+.55)
              + 23*math.cos(TAU*x/1480-.45)*math.sin(p+.2))
    curl = 13*math.sin(math.pi*u)*math.sin(TAU*x/1350+2.2*u-.8)*math.sin(p+1.7*u)
    return center + (2*u-1)*spread + curl + extra


def ribbon_path(x, u, t, extra=0):
    """Fixed horizontal nodes with animated heights and continuous slopes."""
    nodes = [x+i*STEP for i in range(-1,17)]
    y = [y_at(v,u,t,extra) for v in nodes]
    slope = [(y_at(v+.1,u,t,extra)-y_at(v-.1,u,t,extra))/.2 for v in nodes]
    parts = [f"M {nodes[0]:.1f} {y[0]:.1f}"]
    for i in range(len(nodes)-1):
        a,b = nodes[i:i+2]
        h = (b-a)/3
        parts.append(f"C {a+h:.1f} {y[i]+h*slope[i]:.1f} {b-h:.1f} {y[i+1]-h*slope[i+1]:.1f} {b:.1f} {y[i+1]:.1f}")
    return " ".join(parts)


def animated(x,u,attrs):
    frames = [ribbon_path(x,u,k/FRAMES) for k in range(FRAMES)]
    frames.append(frames[0])
    values = ";".join(frames)
    return f'<path {attrs} d="{frames[0]}"><animate attributeName="d" values="{values}" dur="{DURATION}s" repeatCount="indefinite" calcMode="linear"/></path>'


def theme_colors(theme):
    return ("#0b0a0c", "#09090b", "#55483B") if theme == "dark" else ("#f9f6f0", "#faf7f2", "#C8B7A3")


def static_top(svg, x, theme):
    """Keep every source image byte and clip at the horizontal split."""
    paper, _, stroke = theme_colors(theme)
    root = re.search(r'<svg [^>]+>', svg)[0]
    root = re.sub(r'viewBox="[^"]+"', f'viewBox="{x} 0 543 444"', root)
    root = re.sub(r'height="724"', 'height="444"', root)
    image = re.search(r'<image\b[^>]+/>', svg)[0]
    if 'id="artwork"' not in image:
        image = image.replace("<image ", '<image id="artwork" ', 1)
    return f'''{root}
<defs><clipPath id="frame" clipPathUnits="userSpaceOnUse"><rect width="2172" height="724" rx="28.314"/></clipPath>{image}
<linearGradient id="join" gradientUnits="userSpaceOnUse" x1="0" y1="420" x2="0" y2="444"><stop stop-color="{paper}" stop-opacity="0"/><stop offset="1" stop-color="{paper}"/></linearGradient></defs>
<g clip-path="url(#frame)"><use xlink:href="#artwork"/><rect x="{x}" y="420" width="543" height="24" fill="url(#join)"/></g>
<rect x="1.164" y="1.164" width="2169.672" height="721.672" rx="27.15" fill="none" stroke="{stroke}" stroke-width="2.328"/>
</svg>
'''


def render_wave(theme):
    """One SVG and one animation clock across the entire footer width."""
    dark = theme == "dark"
    paper, bottom, stroke = theme_colors(theme)
    colors = ["#a45a18","#ffd28a","#f3a437","#fff0c6","#c77b25","#ffe0a0","#a45a18"] if dark else ["#ad8051","#986024","#bd8745","#854711","#b88a55","#986024","#bd9465"]
    grad = "".join(f'<stop offset="{p}" stop-color="{c}"/>' for p,c in zip([0,.16,.34,.5,.67,.84,1],colors))
    specs = []
    for i in range(26):
        u = i/25
        if i in (0,25):
            attrs = f'stroke-width="{2.7 if dark else 2.2}" filter="url(#glow)" opacity=".93"'
        else:
            attrs = f'stroke-width="{1.12 if i%5==0 else .8}" opacity="{.21+.11*math.cos(math.pi*u)**2:.3f}"'
        specs.append((u,attrs))
    motion = "\n".join(animated(0,u,attrs) for u,attrs in specs)
    still = "\n".join(f'<path {attrs} d="{ribbon_path(0,u,0)}"/>' for u,attrs in specs)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 444 2172 280" width="2172" height="280" overflow="hidden" role="img" aria-label="Soft flowing golden ribbon">
<defs><clipPath id="frame"><rect width="2172" height="724" rx="28.314"/></clipPath><linearGradient id="base" gradientUnits="userSpaceOnUse" x1="0" y1="444" x2="0" y2="724"><stop stop-color="{paper}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>
<linearGradient id="gold" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="2172" y2="0">{grad}</linearGradient>
<filter id="glow" filterUnits="userSpaceOnUse" x="-120" y="420" width="2412" height="304" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="{7 if dark else 3}" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<style>.still{{display:none}}@media(prefers-reduced-motion:reduce){{.motion{{display:none}}.still{{display:inline}}}}</style>
<g clip-path="url(#frame)"><rect y="444" width="2172" height="280" fill="url(#base)"/><g fill="none" stroke="url(#gold)" stroke-linejoin="round"><g class="motion">{motion}</g><g class="still">{still}</g></g></g>
<rect x="1.164" y="1.164" width="2169.672" height="721.672" rx="27.15" fill="none" stroke="{stroke}" stroke-width="2.328"/>
</svg>
'''


def refresh_existing():
    root = Path(__file__).resolve().parents[1] / "assets" / "footer"
    updates = []
    # Every sampled location must exhibit a reversal of the ribbon edges.
    for i in range(16):
        x = i * STEP
        delta = [y_at(x,1,k/FRAMES)-y_at(x,0,k/FRAMES) for k in range(FRAMES)]
        assert min(delta) < 0 < max(delta)
    for theme in ("dark","light"):
        for i,key in enumerate(("github","linkedin","email","resume")):
            path = root / f"connect-{key}-{theme}.svg"
            old = path.read_text(encoding="utf-8")
            new = static_top(old, i*543, theme)
            payload = r'data:image/png;base64,([^"]+)'
            assert re.search(payload,new)[1] == re.search(payload,old)[1]
            assert "<animate" not in new
            ElementTree.fromstring(new)
            updates.append((path,new))
        wave = render_wave(theme)
        tree = ElementTree.fromstring(wave)
        anims = tree.findall(".//{http://www.w3.org/2000/svg}animate")
        assert len(anims) == 26
        for anim in anims:
            values = anim.attrib["values"].split(";")
            assert len(values) == FRAMES+1 and values[0] == values[-1]
        updates.append((root / f"footer-wave-{theme}.svg",wave))
    for path,new in updates:
        path.write_text(new,encoding="utf-8")
    print("Verified static contact tiles and one continuous wave per theme.")


if __name__ == "__main__":
    refresh_existing()
