import os
from PIL import Image

src_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'footer', 'footer-banner.png')
im = Image.open(src_path)
w, h = im.size

# Cut points
cut1 = 445
cut2 = 587

col1 = im.crop((0, 0, cut1, h))
col2 = im.crop((cut1, 0, cut2, h))
col3 = im.crop((cut2, 0, w, h))

out_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'footer')
col1.save(os.path.join(out_dir, 'footer-col1.png'), 'PNG', optimize=True)
col2.save(os.path.join(out_dir, 'footer-col2.png'), 'PNG', optimize=True)
col3.save(os.path.join(out_dir, 'footer-col3.png'), 'PNG', optimize=True)

print(f"Col 1 size: {col1.size} ({(cut1/w)*100:.3f}%)")
print(f"Col 2 size: {col2.size} ({((cut2-cut1)/w)*100:.3f}%)")
print(f"Col 3 size: {col3.size} ({((w-cut2)/w)*100:.3f}%)")
