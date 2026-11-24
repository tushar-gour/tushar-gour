"""Shared visual design system for the profile's generated cards."""
from xml.sax.saxutils import escape

SERIF = "Georgia, 'Times New Roman', serif"
SANS = "Arial, Helvetica, sans-serif"

def palette(is_dark):
    return {"bg":"#101110","fg":"#F0E9DD","muted":"#B8AA99","line":"#38322D","track":"#3A332B","accent":"#F8BA6A","bar":"#9A8066","colors":["#F8BA6A","#E3D2B5","#C5A37C","#A5805B","#79634E","#594E43"]} if is_dark else {"bg":"#FAF7F2","fg":"#28231E","muted":"#695C4E","line":"#D8CDBE","track":"#E2D9CC","accent":"#995617","bar":"#9A8066","colors":["#E9A54F","#D8C1A0","#B88D61","#9B7952","#715F50","#AFA399"]}

def header(title, meta, p):
    return f'''  <rect x="36" y="24" width="6" height="30" rx="1" fill="{p['accent']}"/>
  <text x="56" y="49" font-family="{SERIF}" font-size="30" font-weight="700" fill="{p['fg']}">{title}</text>
  <text x="1084" y="47" text-anchor="end" font-family="{SANS}" font-size="15" font-weight="500" fill="{p['muted']}" letter-spacing="0.5">{meta}</text>
  <line x1="36" y1="74" x2="1084" y2="74" stroke="{p['line']}" stroke-width="1.2"/>'''

def card(height, title, meta, p):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 {height}" width="1120" height="{height}" role="img" aria-label="{title}">
  <rect x="0.6" y="0.6" width="1118.8" height="{height-1.2:.1f}" rx="14" fill="{p['bg']}" stroke="{p['line']}" stroke-width="1.2"/>
{header(title, meta, p)}'''

def text(x, y, value, size, weight, fill, anchor="start", font=SANS):
    return f'  <text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(str(value))}</text>'

def line(x, y, x2, y2, p):
    return f'  <line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{p["line"]}" stroke-width="1.2"/>'

def rect(x,y,w,h,r,color):
    return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{color}"/>'
