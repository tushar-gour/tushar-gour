"""Create a travelling vector ribbon; never deform the contact artwork."""
import math
import re
from pathlib import Path
from xml.etree import ElementTree

PERIOD = 3000
DURATION = 14
X = [0, 160, 350, 543, 760, 930, 1086, 1300, 1470, 1629, 1850, 2050, 2172, 2400, 2700, 3000]
A = [502, 500, 524, 572, 627, 643, 627, 574, 558, 553, 545, 590, 617, 642, 565, 502]
B = [590, 557, 541, 548, 583, 626, 645, 630, 597, 553, 528, 507, 470, 488, 570, 590]
STOPS = [(0,0,.3),(.06,0,.5),(.14,2,1),(.18,3,.9),(.27,1,.8),(.325,2,1),(.39,0,.45),(.50,2,1),(.55,3,.9),(.60,1,.55),(.70,0,.35),(.79,1,.65),(.85,2,1),(.93,4,.5),(1,0,.3)]


def ribbon_path(u, extra=0):
    """Two periodic, C1-continuous cubic spline tiles, in global coordinates."""
    y = [(1-u)*a+u*b+extra+math.sin(math.pi*u)*8*math.sin(2*math.pi*x/PERIOD+.6)
         for x,a,b in zip(X,A,B)]
    n = len(X)-1
    slope = [(y[1]-y[n-1])/(X[1]+PERIOD-X[n-1]) if i in (0,n)
             else (y[i+1]-y[i-1])/(X[i+1]-X[i-1]) for i in range(n+1)]
    parts = [f"M 0 {y[0]:.2f}"]
    for tile in range(2):
        for i in range(n):
            a,b = X[i]+tile*PERIOD,X[i+1]+tile*PERIOD
            h = (b-a)/3
            parts.append(f"C {a+h:.2f} {y[i]+h*slope[i]:.2f} {b-h:.2f} {y[i+1]-h*slope[i+1]:.2f} {b:.2f} {y[i+1]:.2f}")
    return " ".join(parts)


def wave_motion(x, theme):
    dark = theme == "dark"
    paper, bottom = ("#0b0a0c","#09090b") if dark else ("#f9f6f0","#faf7f2")
    colors = ["#8e420e","#f28c20","#fff2bd","#ffb342","#b46214"] if dark else ["#c9a37b","#ac631d","#743b13","#b6742c","#c19b74"]
    stops = "".join(f'<stop offset="{p}" stop-color="{colors[c]}" stop-opacity="{o}"/>' for p,c,o in STOPS)
    defs = f'''<linearGradient id="base" gradientUnits="userSpaceOnUse" x1="0" y1="430" x2="0" y2="724"><stop stop-color="{paper}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>
<linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="0" y1="426" x2="0" y2="466"><stop stop-color="white" stop-opacity="0"/><stop offset="1" stop-color="white"/></linearGradient>
<mask id="replace-wave" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="{x}" y="420" width="543" height="304"><rect x="{x}" y="420" width="543" height="304" fill="url(#fade)"/></mask>
<clipPath id="wave-region" clipPathUnits="userSpaceOnUse"><rect x="{x}" y="444" width="543" height="280"/></clipPath>
<linearGradient id="gold" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{PERIOD}" y2="0" spreadMethod="repeat">{stops}</linearGradient>
<filter id="bloom" filterUnits="userSpaceOnUse" x="-80" y="425" width="6160" height="320" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="{12 if dark else 7}"/></filter>
<filter id="halo" filterUnits="userSpaceOnUse" x="-30" y="440" width="6060" height="290" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="{3.5 if dark else 2.5}"/></filter>
<path id="crest" d="{ribbon_path(0)}"/><path id="ribbon-edge" d="{ribbon_path(1)}"/>'''
    lines = []
    for i in range(25):
        u = (i+1)/26
        opacity = (.23 if dark else .25)+(1-u)*.1
        lines.append(f'<path d="{ribbon_path(u)}" stroke-width="{1.2 if i%5==0 else .8}" opacity="{opacity}"/>')
    tail = [f'<path d="{ribbon_path(.22+i*.07,13+i*4)}" stroke-width=".75" opacity="{.12*(1-i/10)}"/>' for i in range(9)]
    threads = "\n".join(tail+lines)
    overlay = f'''<g class="wave-motion">
<rect x="{x}" y="420" width="543" height="304" fill="url(#base)" mask="url(#replace-wave)"/>
<g clip-path="url(#wave-region)">
<g fill="none" stroke="url(#gold)" stroke-linejoin="round" transform="translate(-{PERIOD} 0)">
<animateTransform attributeName="transform" type="translate" from="-{PERIOD} 0" to="0 0" dur="{DURATION}s" repeatCount="indefinite" calcMode="linear"/>
<g filter="url(#bloom)" opacity="{.67 if dark else .28}"><use xlink:href="#crest" stroke-width="{22 if dark else 12}"/><use xlink:href="#ribbon-edge" stroke-width="12" opacity=".5"/></g>
{threads}
<g filter="url(#halo)" opacity="{.86 if dark else .38}"><use xlink:href="#crest" stroke-width="8"/><use xlink:href="#ribbon-edge" stroke-width="4"/></g>
<use xlink:href="#ribbon-edge" stroke-width="1.65" opacity=".8"/>
<use xlink:href="#crest" stroke-width="{3.1 if dark else 2.5}"/>
</g></g></g>'''
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
            assert new.count("<animateTransform ") == 1 and "skewY" not in new
            ElementTree.fromstring(new)
            updates.append((path,new))
    for path,new in updates:
        path.write_text(new,encoding="utf-8")
    print("Verified 8 vector ribbons and unchanged original artwork.")


if __name__ == "__main__":
    refresh_existing()
