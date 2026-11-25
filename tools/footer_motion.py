"""Build one full-width animated ribbon beneath static clickable contact tiles."""
import math
import re
from pathlib import Path
from xml.etree import ElementTree

TAU = 2 * math.pi
FRAMES = 30          # key shapes per loop; linear blending between them is imperceptible
DURATION = 36        # seconds per seamless loop: slow and soothing
STRANDS = 44         # fine strands in the bundle
STEP = 2172 / 15     # fixed horizontal node spacing (equal steps allow smooth "S" joins)
Y0 = 584             # resting centre line of the ribbon (viewBox y runs 444..724)

# Centre-line wave components: (amplitude, wavelength, direction, phase, strand lag).
# Each runs at its own speed and direction (longer waves faster, shorter slower,
# two of them against the flow), so crests overtake and cancel one another and the
# ribbon keeps changing shape instead of one rigid pattern sliding sideways.
# Every component completes a whole number of cycles per loop, so the loop is seamless.
WAVES = (
    (28, 2300, +1, .4, .30),
    (17, 1450, -1, 1.9, .40),
    (9, 930, +1, 3.1, .55),
    (5, 610, -1, .7, .60),
)


def taper(x):
    """The bundle closes to a single thread just inside both card edges."""
    a = max(0.0, min(1.0, (min(x, 2172 - x) - 90) / 320))
    return a * a * (3 - 2 * a)


def y_at(x, u, t):
    """Height of strand u (0..1) at horizontal position x and loop time t (0..1)."""
    th = TAU * t
    s = 2 * u - 1
    swell = 1 + .16 * math.sin(th + .8)  # the whole ribbon slowly breathes
    y = Y0
    for amp, lam, direction, phase, lag in WAVES:
        # The per-strand lag shifts each strand's phase a little, which gives the
        # ribbon depth: strands drift past one another like silk instead of moving as one.
        y += amp * swell * math.sin(TAU * x / lam - direction * th + phase + lag * s)
    # Signed ribbon width: it narrows to a pinch, turns over and opens again as it travels.
    width = 38 * math.sin(TAU * x / 1700 - th + 2.2) + 13 * math.sin(TAU * x / 1050 + th + .5)
    return y + s * width * taper(x)


def ribbon_path(u, t):
    """Fixed horizontal nodes with animated heights and continuous slopes."""
    nodes = [i * STEP for i in range(-1, 17)]
    y = [y_at(v, u, t) for v in nodes]
    slope = [(y_at(v + .1, u, t) - y_at(v - .1, u, t)) / .2 for v in nodes]
    h = STEP / 3
    parts = [f"M{nodes[0]:.1f} {y[0]:.1f}C{nodes[0]+h:.1f} {y[0]+h*slope[0]:.1f} {nodes[1]-h:.1f} {y[1]-h*slope[1]:.1f} {nodes[1]:.1f} {y[1]:.1f}"]
    for i in range(2, len(nodes)):
        # "S" mirrors the previous control point, which matches the slope-based
        # construction exactly because every step has the same width.
        parts.append(f"S{nodes[i]-h:.1f} {y[i]-h*slope[i]:.1f} {nodes[i]:.1f} {y[i]:.1f}")
    return "".join(parts)


def animated(u, attrs):
    frames = [ribbon_path(u, k / FRAMES) for k in range(FRAMES)]
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
    """One SVG and one animation clock across the entire footer width.

    The animation always plays. It is deliberately slow and gentle, and a
    reduced-motion fallback would leave the ribbon frozen for everyone whose
    system has animations switched off, which is why none is included.
    """
    dark = theme == "dark"
    paper, bottom, stroke = theme_colors(theme)
    colors = ["#b8611a","#f59a2e","#ffa63a","#ffe2b0","#f08a22","#ffb85a","#b8611a"] if dark else ["#ad8051","#986024","#bd8745","#854711","#b88a55","#986024","#bd9465"]
    # Stops at the ends fade the bundle to nothing so it tapers inside the card.
    stops = [(0,colors[0],0),(.035,colors[0],0),(.09,colors[0],1)]
    stops += [(p,c,1) for p,c in zip([.16,.34,.5,.67,.84],colors[1:6])]
    stops += [(.91,colors[6],1),(.965,colors[6],0),(1,colors[6],0)]
    grad = "".join(f'<stop offset="{p}" stop-color="{c}" stop-opacity="{o}"/>' for p,c,o in stops)
    specs = []
    for i in range(STRANDS):
        u = i/(STRANDS-1)
        if i in (0,STRANDS-1):
            attrs = f'stroke-width="{2.4 if dark else 2}" opacity=".95"'
        else:
            attrs = f'stroke-width="{1.05 if i%6==0 else .75}" opacity="{(.17 if dark else .26)+.06*math.cos(math.pi*u)**2:.3f}"'
        specs.append((u,attrs))
    motion = "\n".join(animated(u,attrs) for u,attrs in specs)
    # One bloom over the whole bundle: the glow is strongest where many strands
    # overlap, so the ribbon flares at its pinch points as it moves.
    if dark:
        bloom = ('<feGaussianBlur in="SourceGraphic" stdDeviation="5" result="n"/><feGaussianBlur in="SourceGraphic" stdDeviation="14" result="w"/>'
                 '<feColorMatrix in="n" type="matrix" values="1 0 0 0 0 0 .95 0 0 0 0 0 .8 0 0 0 0 0 0.9 0" result="n2"/>'
                 '<feColorMatrix in="w" type="matrix" values="1 0 0 0 0 0 .8 0 0 0 0 0 .5 0 0 0 0 0 1.5 0" result="w2"/>'
                 '<feMerge><feMergeNode in="w2"/><feMergeNode in="n2"/><feMergeNode in="SourceGraphic"/></feMerge>')
    else:
        bloom = ('<feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="n"/><feGaussianBlur in="SourceGraphic" stdDeviation="9" result="w"/>'
                 '<feColorMatrix in="w" type="matrix" values="1 0 0 0 .15 0 .8 0 0 .08 0 0 .4 0 0 0 0 0 1.6 0" result="w2"/>'
                 '<feMerge><feMergeNode in="w2"/><feMergeNode in="n"/><feMergeNode in="SourceGraphic"/></feMerge>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 444 2172 280" width="2172" height="280" overflow="hidden" role="img" aria-label="Soft flowing golden ribbon">
<defs><clipPath id="frame"><rect width="2172" height="724" rx="28.314"/></clipPath><linearGradient id="base" gradientUnits="userSpaceOnUse" x1="0" y1="444" x2="0" y2="724"><stop stop-color="{paper}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>
<linearGradient id="gold" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="2172" y2="0">{grad}</linearGradient>
<filter id="bloom" filterUnits="userSpaceOnUse" x="-100" y="430" width="2372" height="300" color-interpolation-filters="sRGB">{bloom}</filter></defs>
<g clip-path="url(#frame)"><rect y="444" width="2172" height="280" fill="url(#base)"/><g fill="none" stroke="url(#gold)" stroke-linejoin="round" filter="url(#bloom)">
{motion}
</g></g>
<rect x="1.164" y="1.164" width="2169.672" height="721.672" rx="27.15" fill="none" stroke="{stroke}" stroke-width="2.328"/>
</svg>
'''


def refresh_existing():
    root = Path(__file__).resolve().parents[1] / "assets" / "footer"
    updates = []
    # The ribbon must loop seamlessly and stay inside the card, with room for the glow.
    for i in range(0, 2173, 36):
        for k in range(0, 25):
            u = k / 24
            assert abs(y_at(i, u, 0) - y_at(i, u, 1)) < 1e-6
            assert all(470 < y_at(i, u, j / 72) < 698 for j in range(72))
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
        assert len(anims) == STRANDS
        for anim in anims:
            values = anim.attrib["values"].split(";")
            assert len(values) == FRAMES+1 and values[0] == values[-1]
        assert "prefers-reduced-motion" not in wave
        updates.append((root / f"footer-wave-{theme}.svg",wave))
    for path,new in updates:
        path.write_text(new,encoding="utf-8")
    print("Verified static contact tiles and one continuous wave per theme.")


if __name__ == "__main__":
    refresh_existing()
