"""Build a clean ivory hero from the approved full-resolution artwork."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import subprocess
import io
import hashlib

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "assets/identity/hero-gold.png"
target = source.with_name("hero-gold-light.png")

def refine_hero_accents(image, is_dark):
    """Restore the background beneath the old accents, then draw the new rules.

    Coordinates are defined in the original 2048 x 731 composition.
    Text, map, crest and border are outside the edited regions.
    """
    pixels = np.array(image.convert("RGB"), dtype=np.float32)

    def restore(box, horizontal):
        x0, y0, x1, y1 = box
        if horizontal:
            before = pixels[y0-3:y0, x0:x1].mean(axis=0)
            after = pixels[y1:y1+3, x0:x1].mean(axis=0)
            weight = np.linspace(0, 1, y1-y0)[:, None, None]
            pixels[y0:y1, x0:x1] = before[None] * (1-weight) + after[None] * weight
        else:
            before = pixels[y0:y1, x0-3:x0].mean(axis=1)
            after = pixels[y0:y1, x1:x1+3].mean(axis=1)
            weight = np.linspace(0, 1, x1-x0)[None, :, None]
            pixels[y0:y1, x0:x1] = before[:, None] * (1-weight) + after[:, None] * weight

    restore((108,109,520,130), True)
    restore((120,417,1240,437), True)
    restore((125,479,145,599), False)
    result = Image.fromarray(np.uint8(np.clip(pixels,0,255)))
    draw = ImageDraw.Draw(result)
    gold = (236,193,135) if is_dark else (153,86,23)
    graphite = (65,68,70) if is_dark else (200,183,163)
    separator = (77,80,81) if is_dark else (200,183,163)
    draw.line((112,119,500,119), fill=graphite, width=3)
    draw.line((112,119,232,119), fill=gold, width=3)
    draw.line((125,426,1210,426), fill=separator, width=2)
    return result


def generate():
    original = Image.open(source).convert("RGB")
    # Exact approved crop: 1978 x 600. Recover the two edge pixels only
    # when migrating the previous 1976px crop; no backup image is kept.
    bounds = (35,64,2013,664)
    if original.size == (1976,600):
        raw = subprocess.check_output(["git","show","79c248d657eddebb65b60b8463e67da12a56461a:assets/identity/hero-banner.png"], cwd=ROOT)
        sha = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
        if sha != "c074aa94b4a3a6d59fb1e334f272b07b4fef4e17":
            raise ValueError("Original approved banner hash mismatch")
        im = Image.open(io.BytesIO(raw)).convert("RGB")
    elif original.size == (2048,731):
        im = original
    elif original.size == (1978,600):
        im = Image.new("RGB",(2048,731),(13,16,17))
        im.paste(original,(35,64))
    else:
        raise ValueError(f"Unexpected hero dimensions: {original.size}")
    # The exact top-rule color also marks the already-refined dark artwork.
    if im.getpixel((160,119)) != (236,193,135):
        im = refine_hero_accents(im, True)
    a = np.asarray(im).astype(np.float32)/255
    r,g,b = a.transpose(2,0,1)
    y = .2126*r+.7152*g+.0722*b
    h,w = y.shape
    yy,xx = np.mgrid[:h,:w]
    paper = np.array([250.,247.,242.])
    wall = np.empty((h,w,3),np.float32)
    wall[:] = paper
    # Recover the lettering and icon strokes from local contrast, without inverting the wall.
    smooth = np.asarray(Image.fromarray(np.uint8(y*255)).filter(ImageFilter.GaussianBlur(18))).astype(np.float32)/255
    contrast = np.maximum(y-smooth,0)
    ink = np.clip((contrast-.035)/.62,0,1)
    ink = np.maximum(ink,np.clip((y-.20)/.58,0,1))
    warm = np.clip((r-b-.08)/.26,0,1)
    fg = np.array([40.,35.,30.])*(1-warm[...,None])+np.array([145.,82.,25.])*warm[...,None]
    # Keep the approved left-hand text and graphics; fade only the empty edge.
    left = (xx<1240)&(yy>90)&(yy<632)
    left_alpha = ink*left*np.clip((1240-xx)/50,0,1)
    wall = wall*(1-left_alpha[...,None])+fg*left_alpha[...,None]
    # Reconstruct fine map dots; broad spotlights and wall texture are not transferred.
    dot = np.clip((contrast-.075)/.38,0,1)
    dot *= ((xx>=1120)&(xx<2002)&(yy>=105)&(yy<=575))
    dot *= np.clip((xx-1120)/75,0,1)
    wall = wall*(1-dot[...,None])+np.array([167.,115.,60.])*dot[...,None]
    out = Image.fromarray(np.uint8(np.clip(wall,0,255))).convert("RGBA")
    # Trace the original crest at native resolution. Coordinates are from the original artwork.
    # Preserve recessed black metal areas, but exclude the surrounding wall and top spotlights.
    outlines = [
        [(72,46),(146,75),(235,83),(328,86),(411,56),(395,105),(370,113),(354,132),(356,147),(375,183),(411,208),(389,193),(381,210),(400,228),(401,249),(395,280),(380,308),(359,335),(330,356),(314,363),(300,374),(276,380),(257,373),(247,368),(232,377),(207,379),(183,369),(164,354),(145,342),(120,316),(100,283),(87,251),(81,227),(103,200),(96,185),(72,201),(101,148),(102,133),(88,107),(84,96),(99,105),(88,78)],
        [(199,389),(224,382),(247,373),(270,383),(296,390),(288,399),(272,410),(247,422),(224,408),(207,398)]
    ]
    scale=3
    mask=Image.new("L",(w*scale,h*scale))
    draw=ImageDraw.Draw(mask)
    for poly in outlines:
        draw.polygon([((x+1350)*scale,(y0+110)*scale) for x,y0 in poly],fill=255)
    mask=mask.resize((w,h),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(.5))
    # Remove map dots from behind the crest's silhouette and add a restrained contact shadow.
    shadow_mask=Image.new("L",im.size)
    shadow_mask.paste(mask,(2,8))
    shadow_mask=shadow_mask.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v*.22))
    shadow=Image.new("RGBA",im.size,(53,37,23,0))
    shadow.putalpha(shadow_mask)
    out=Image.alpha_composite(out,shadow)
    crest=im.convert("RGBA")
    crest.putalpha(mask)
    out=Image.alpha_composite(out,crest)
    frame=ImageDraw.Draw(out)
    frame.rounded_rectangle((36,64,2011,663),radius=17,outline=(216,205,190,255),width=2)
    # Crop away the outside margins. Both variants use identical framing and dimensions.
    refine_hero_accents(out, False).crop(bounds).save(target,optimize=True)
    cropped = im.crop(bounds)
    if original.size != cropped.size or not np.array_equal(np.asarray(original), np.asarray(cropped)):
        cropped.save(source,optimize=True)
    with Image.open(source) as check:
        assert check.size == (1978,600)
        check.verify()
    with Image.open(target) as check:
        assert check.size == (1978,600)
        check.verify()

if __name__ == "__main__":
    generate()
