"""Animate the original footer pixels without redrawing the artwork."""
import math
import re


def wave_motion(x):
    """Return the clipped, phase-aligned mesh and its shared mask."""
    def displacement(px, t):
        phase = 2 * math.pi * t
        return 16 * math.sin(2 * math.pi * px / 1550 - phase) + 5 * math.sin(2 * math.pi * px / 940 + 2 * phase + .7)

    clips, strips = [], []
    for j in range(24):
        left, right = x + j * 543 / 24, x + (j + 1) * 543 / 24
        width = right - left
        ys = [displacement(left, k / 48) for k in range(48)]
        angles = [math.degrees(math.atan((displacement(right, k / 48) - y) / width)) for k, y in enumerate(ys)]
        ys.append(ys[0])
        angles.append(angles[0])
        dy = ";".join(f"0 {v:.4f}" for v in ys)
        angle = ";".join(f"{v:.4f}" for v in angles)
        clips.append(f'<clipPath id="strip{j}"><rect x="-.25" y="400" width="{width+.5:.4f}" height="324"/></clipPath>')
        strips.append(f'<g transform="translate({left:.4f} 0)"><g><animateTransform attributeName="transform" type="translate" values="{dy}" dur="9s" repeatCount="indefinite" calcMode="linear"/><g><animateTransform attributeName="transform" type="skewY" values="{angle}" dur="9s" repeatCount="indefinite" calcMode="linear"/><g clip-path="url(#strip{j})"><use xlink:href="#artwork" transform="translate({-left:.4f} 0)"/></g></g></g></g>')
    gradient = f'<linearGradient id="waveMask" x1="0" y1="0" x2="0" y2="724" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="white" stop-opacity="0"/><stop offset="{424/724}" stop-color="white" stop-opacity="0"/><stop offset="{454/724}" stop-color="white"/><stop offset="{680/724}" stop-color="white"/><stop offset="{710/724}" stop-color="white" stop-opacity="0"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient><mask id="motionMask" maskUnits="userSpaceOnUse" x="{x}" y="0" width="543" height="724"><rect x="{x}" width="543" height="724" fill="url(#waveMask)"/></mask>'
    return gradient + "\n" + "\n".join(clips), '<g class="wave-motion" mask="url(#motionMask)">\n' + "\n".join(strips) + "\n</g>"


def animate_footer(svg, x):
    """Keep the original embedded PNG and apply a masked wave-only deformation."""
    match = re.search(r'<g clip-path="url\(#frame\)">(<image [^>]+/>)</g>', svg)
    if not match:
        raise ValueError("Unexpected footer source")
    defs, overlay = wave_motion(x)
    image = match[1].replace("<image ", '<image id="artwork" ', 1)
    svg = svg.replace("</defs>", image + "\n" + defs + "</defs>", 1)
    svg = svg.replace(match[0], '<style>@media (prefers-reduced-motion: reduce) {.wave-motion {display:none}}</style>\n<g clip-path="url(#frame)"><use xlink:href="#artwork"/>\n' + overlay + "\n</g>", 1)
    return svg
