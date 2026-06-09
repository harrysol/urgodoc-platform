#!/usr/bin/env python3
"""
Photo-montage: add a realistic second floor onto the REAL front photo of the
house by lifting the roof and inserting a wall+window band copied from the
house's own facade pixels. No CG, no GPU - uses the actual photograph.
Tweak the coordinates below to fit the photo.
"""
import numpy as np
from PIL import Image, ImageFilter
import os

SRC = "/tmp/photos/img_04.jpg"
OUT = os.path.join(os.path.dirname(__file__), "..", "renders", "photomontage")
os.makedirs(OUT, exist_ok=True)

# --- facade coordinates in the photo (full-res px) ---
HX0, HX1 = 65, 545      # house left/right
RY, EY   = 150, 178     # roof top y, eave y (top of walls)
H_NEW    = 90           # added second-floor height (px)
BAND_TOP = 176          # source band top (wall+windows start)
FEATHER  = 5

im = Image.open(SRC).convert("RGB")
a = np.array(im).astype(np.float32)
out = a.copy()

roof     = a[RY:EY, HX0:HX1].copy()                       # the flat roof + fascia
newfloor = a[BAND_TOP:BAND_TOP+H_NEW, HX0:HX1].copy()     # wall + windows slice

# raise the roof by H_NEW, then drop the new floor band beneath it
out[RY-H_NEW:EY-H_NEW, HX0:HX1] = roof
out[EY-H_NEW:EY,       HX0:HX1] = newfloor

# subtle shadow line under the new floor (floor separation) for realism
sh0 = EY-6
out[sh0:EY, HX0:HX1] *= np.linspace(1.0, 0.82, 6)[:, None, None]

# feather the left/right vertical edges of the inserted block into background
for m in range(FEATHER):
    al = m / FEATHER
    y0, y1 = RY-H_NEW, EY
    out[y0:y1, HX0+m] = al*out[y0:y1, HX0+m] + (1-al)*a[y0:y1, HX0+m]
    out[y0:y1, HX1-1-m] = al*out[y0:y1, HX1-1-m] + (1-al)*a[y0:y1, HX1-1-m]

res = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
# light blend of a 1px blur at the seams to kill hard lines
blur = res.filter(ImageFilter.GaussianBlur(1.2))
mask = Image.new("L", res.size, 0)
mk = np.array(mask);
for sy in (RY-H_NEW, EY-H_NEW, EY):
    mk[max(0,sy-3):sy+3, HX0:HX1] = 120
mask = Image.fromarray(mk)
res = Image.composite(blur, res, mask)

res.save(os.path.join(OUT, "front_two_story.png"))
print("wrote", os.path.join(OUT, "front_two_story.png"), res.size)
