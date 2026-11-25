"""Animate the original footer pixels without redrawing the artwork."""
import math
import re


def wave_motion(x):
    """Return the clipped, phase-aligned mesh and its shared mask."""
    def displacement(px, t):
        phase = 2 * math.pi * t
        a = 2 * math.pi * px / 1600
        b = 2 * math.pi * px / 1050 + .7
        # Subtract the rest phase so each loop begins at the untouched artwork.
        return 25 * (math.sin(a - phase) - math.sin(a)) + 5 * (math.sin(b - 2 * phase) - math.sin(b))

    clips, strips = [], []
    for j in range(48):
        left, right = x + j * 543 / 48, x + (j + 1) * 543 / 48
        width = right - left
        ys = [displacement(left, k / 120) for k in range(120)]
        angles = [math.degrees(math.atan((displacement(right, k / 120) - y) / width)) for k, y in enumerate(ys)]
        ys.append(ys[0])
        angles.append(angles[0])
        dy = ";".join(f"0 {(0 if abs(v) < .00005 else v):.4f}" for v in ys)
        angle = ";".join(f"{(0 if abs(v) < .00005 else v):.4f}" for v in angles)
        clips.append(f'<clipPath id="strip{j}" clipPathUnits="userSpaceOnUse"><rect x="-1.5" y="405" width="{width+3:.4f}" height="319"/></clipPath>')
        strips.append(f'<g transform="translate({left:.4f} 0)"><g><animateTransform attributeName="transform" type="translate" values="{dy}" dur="8s" repeatCount="indefinite" calcMode="linear"/><g><animateTransform attributeName="transform" type="skewY" values="{angle}" dur="8s" repeatCount="indefinite" calcMode="linear"/><g clip-path="url(#strip{j})"><use xlink:href="#artwork" transform="translate({-left:.4f} 0)"/></g></g></g></g>')
    gradient = f'<linearGradient id="waveMask" x1="0" y1="0" x2="0" y2="724" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="white" stop-opacity="0"/><stop offset="{425/724}" stop-color="white" stop-opacity="0"/><stop offset="{465/724}" stop-color="white"/><stop offset="{690/724}" stop-color="white"/><stop offset="{720/724}" stop-color="white" stop-opacity="0"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient><mask id="motionMask" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="{x}" y="0" width="543" height="724"><rect x="{x}" width="543" height="724" fill="url(#waveMask)"/></mask>'
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

def refresh_existing():
    """Regenerate motion only; preserve embedded artwork and existing frame."""
    from pathlib import Path
    from xml.etree import ElementTree
    root = Path(__file__).resolve().parents[1]
    updates = []
    for theme in ("dark", "light"):
        for i, key in enumerate(("github", "linkedin", "email", "resume")):
            path = root / "assets" / "footer" / f"connect-{key}-{theme}.svg"
            old = path.read_text(encoding="utf-8")
            start = old.index('<linearGradient id="waveMask"')
            defs_end = old.index("</defs>", start)
            overlay_start = old.index('<g class="wave-motion"')
            overlay_end = old.rindex("\n</g>\n</g>\n<rect") + len("\n</g>")
            defs, overlay = wave_motion(i * 543)
            updated = old[:start] + defs + old[defs_end:overlay_start] + overlay + old[overlay_end:]
            assert re.search(r"data:image/png;base64,([A-Za-z0-9+/=]+)", updated)[1] == re.search(r"data:image/png;base64,([A-Za-z0-9+/=]+)", old)[1]
            assert updated.count("<animateTransform ") == 96
            ElementTree.fromstring(updated)
            updates.append((path, updated))
    for path, updated in updates:
        path.write_text(updated, encoding="utf-8")
    print("Verified 8 SVGs; all original embedded image bytes unchanged.")


if __name__ == "__main__":
    refresh_existing()
