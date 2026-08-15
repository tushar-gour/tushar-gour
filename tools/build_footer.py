#!/usr/bin/env python3
import base64
import os

banner_path = os.path.join(os.path.dirname(__file__), "..", "assets", "footer", "footer-banner.png")
with open(banner_path, "rb") as f:
    b64_img = base64.b64encode(f.read()).decode("utf-8")

svg_content = f'''<svg version="1.2" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1024 322" width="100%" height="100%">
  <defs>
    <style>
      .link-btn {{ cursor: pointer; }}
      .link-btn:hover rect {{ stroke: #FF6B35; stroke-width: 1.5px; fill: rgba(255, 107, 53, 0.08); }}
    </style>
  </defs>

  <!-- 1:1 Pixel-Exact Footer Graphic -->
  <image width="1024" height="322" href="data:image/png;base64,{b64_img}" />

  <!-- Interactive Hyperlink Overlays -->
  <!-- 1. GITHUB -->
  <a href="https://github.com/tushar-gour" xlink:href="https://github.com/tushar-gour" target="_blank" rel="noopener noreferrer" class="link-btn" id="footer-link-github">
    <rect x="335" y="88" width="75" height="126" rx="14" fill="transparent" />
  </a>

  <!-- 2. LINKEDIN -->
  <a href="https://linkedin.com/in/tushar-gour" xlink:href="https://linkedin.com/in/tushar-gour" target="_blank" rel="noopener noreferrer" class="link-btn" id="footer-link-linkedin">
    <rect x="480" y="88" width="75" height="126" rx="14" fill="transparent" />
  </a>

  <!-- 3. EMAIL -->
  <a href="mailto:tushargour004@gmail.com" xlink:href="mailto:tushargour004@gmail.com" target="_blank" rel="noopener noreferrer" class="link-btn" id="footer-link-email">
    <rect x="618" y="88" width="75" height="126" rx="14" fill="transparent" />
  </a>
</svg>
'''

out_dark = os.path.join(os.path.dirname(__file__), "..", "assets", "footer", "footer-editorial-dark.svg")
out_light = os.path.join(os.path.dirname(__file__), "..", "assets", "footer", "footer-editorial-light.svg")

with open(out_dark, "w", encoding="utf-8") as f:
    f.write(svg_content)
with open(out_light, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"Generated {out_dark} ({len(svg_content)} bytes)")
print(f"Generated {out_light} ({len(svg_content)} bytes)")
