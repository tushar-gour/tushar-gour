"""Generate the light hero from the approved dark artwork, preserving the crest."""
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "assets/identity/hero-gold.png"
target = source.with_name("hero-gold-light.png")

def generate():
    original = Image.open(source).convert("RGB")
    size = original.size
    im = original.resize((2048, 731), Image.Resampling.LANCZOS) if size != (2048, 731) else original
    a = np.asarray(im).astype("float32") / 255
    r, g, b = a.transpose(2, 0, 1)
    y = .2126*r + .7152*g + .0722*b
    pts = [0,.04,.10,.18,.30,.48,.65,.82,1]
    colors = np.array([[250,247,242],[249,246,240],[244,239,230],[235,226,212],[218,201,179],[181,152,117],[133,103,74],[71,56,43],[40,35,30]])
    neutral = np.stack([np.interp(y,pts,colors[:,i]) for i in range(3)],axis=-1)
    warm = np.clip((r-b-.045)/.22,0,1)*np.clip((y-.13)/.25,0,1)
    bronzepts = [0,.12,.28,.45,.64,.8,1]
    bronze = np.array([[250,247,242],[241,230,213],[208,180,140],[154,104,55],[124,74,25],[148,82,24],[156,85,23]])
    accent = np.stack([np.interp(y,bronzepts,bronze[:,i]) for i in range(3)],axis=-1)
    original_tone = neutral*(1-warm[...,None])+accent*warm[...,None]
    blur = np.asarray(Image.fromarray(np.uint8(y*255)).filter(ImageFilter.GaussianBlur(15))).astype("float32")/255
    dots = np.clip((np.maximum(y-blur,0)-.035)/.42,0,1)
    base = np.array([247,243,236])
    dot = np.array([150,103,54])
    wall = base+(dot-base)*dots[...,None]
    x = np.arange(im.width)[None,:]
    mix = np.clip((x-1180)/150,0,1)
    out = original_tone*(1-mix[...,None])+wall*mix[...,None]
    # Keep the original metallic crest; the mask follows its outer silhouette.
    mask = Image.new("L", im.size)
    ImageDraw.Draw(mask).polygon([(1418,151),(1492,180),(1678,198),(1765,161),(1754,199),(1738,218),(1750,212),(1730,258),(1761,321),(1753,325),(1753,373),(1737,408),(1701,449),(1680,473),(1648,487),(1647,502),(1628,515),(1598,533),(1570,519),(1547,505),(1548,490),(1524,480),(1504,463),(1477,441),(1450,408),(1435,375),(1429,331),(1451,302),(1420,314),(1450,253),(1434,208),(1463,224),(1430,191)],fill=255)
    alpha = np.asarray(mask.filter(ImageFilter.GaussianBlur(1.4))).astype("float32")/255
    metal = np.clip(a*255*.91+np.array([18,12,5]),0,255)
    out = out*(1-alpha[...,None])+metal*alpha[...,None]
    # Preserve the frame without carrying dark-mode spotlight pools into light mode.
    edge = np.ones_like(y)
    edge[:67]=0
    edge[660:]=0
    edge[:,:39]=0
    edge[:,2010:]=0
    out = out*edge[...,None]+original_tone*(1-edge[...,None])
    result = Image.fromarray(np.uint8(np.clip(out,0,255)))
    if size != result.size:
        result = result.resize(size,Image.Resampling.LANCZOS)
    result.save(target, optimize=True)
    with Image.open(target) as check:
        check.verify()
    print(f"Generated {target.relative_to(ROOT)}")

if __name__ == "__main__":
    generate()
