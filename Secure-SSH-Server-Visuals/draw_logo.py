#!/usr/bin/env python3
"""Secure-SSH-Server logo: the pulley at the top of the shaft. A copper wheel in a dark
iron bracket, a rope running over it, one end dropping out of frame and the other holding
a small square car shown as a plain box with a slatted front. Flat shapes, hard edges,
kitchen enamel white for the car, copper for wheel and rope shadow, a single herb green
leaf sprig tied to the bracket as the house's mark. The name sits below in Anek Odia,
upright and even, white on the dark green of a painted door. No key, no lock, no shield,
no terminal window. At 64 pixels, wheel, rope, and box must still read."""
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
W = H = 1024
v = sys.argv[1] if len(sys.argv) > 1 else "ship"
GREEN = (18, 42, 30); COPPER = (196, 120, 62); IRON = (36, 38, 36); WHITE = (238, 236, 226); HERB = (96, 148, 84)
img = Image.new("RGB", (W, H), GREEN); d = ImageDraw.Draw(img, "RGBA")
# painted door panels behind the mark
d.rectangle([70, 60, 954, 700], outline=(30, 62, 42), width=4)
# iron bracket across the top, wheel hung at centre
d.rectangle([262, 108, 762, 140], fill=IRON)
d.rectangle([262, 108, 288, 220], fill=IRON); d.rectangle([736, 108, 762, 220], fill=IRON)
cx, cy, r = 512, 208, 88
d.line([(cx, 140), (cx, cy - r)], fill=IRON, width=12)
d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=COPPER)
d.ellipse([cx - r + 16, cy - r + 16, cx + r - 16, cy + r - 16], outline=(150, 88, 40), width=8)
for ang in (0, 60, 120, 180, 240, 300):  # spokes
    import math
    x2 = cx + int((r - 14) * np.cos(np.radians(ang))); y2 = cy + int((r - 14) * np.sin(np.radians(ang)))
    d.line([(cx, cy), (x2, y2)], fill=(150, 88, 40), width=9)
d.ellipse([cx - 17, cy - 17, cx + 17, cy + 17], fill=IRON)
# herb sprig tied to the bracket, right side
sx, sy = 700, 128
d.line([(sx, sy), (sx + 8, sy + 54)], fill=HERB, width=5)
for k in range(3):
    yy = sy + 10 + k * 16
    d.polygon([(sx + 4, yy), (sx - 16, yy + 10), (sx + 4, yy + 18)], fill=HERB)
    d.polygon([(sx + 4, yy), (sx + 24, yy + 10), (sx + 4, yy + 18)], fill=HERB)
# rope over the wheel: left end drops out of frame, right end holds the car
rope_w = 11 if v != "v1" else 8
d.line([(cx - r + 6, cy), (cx - r + 6, 780)], fill=(216, 186, 132), width=rope_w)
d.line([(cx + r - 6, cy), (cx + r - 6, 452)], fill=(216, 186, 132), width=rope_w)
d.arc([cx - r + 6, cy - 12, cx + r - 6, cy + 40], 180, 360, fill=(216, 186, 132), width=rope_w)
# the car: plain enamel white box with a slatted front
bx0, by0, bw, bh = cx + r - 82, 452, 152, 168
d.rectangle([bx0, by0, bx0 + bw, by0 + bh], fill=WHITE)
d.rectangle([bx0, by0, bx0 + bw, by0 + 22], fill=(214, 212, 200))
for lx in range(bx0 + 22, bx0 + bw - 14, 24):
    d.line([(lx, by0 + 40), (lx, by0 + bh - 18)], fill=(120, 118, 108), width=7)
d.rectangle([bx0, by0, bx0 + bw, by0 + bh], outline=(168, 166, 156), width=4)
if v != "v1":
    f = ImageFont.truetype("fonts/AnekOdia.ttf", 88)
    txt = "Secure-SSH-Server"; tw = d.textlength(txt, font=f)
    d.text(((W - tw) / 2, 800), txt, font=f, fill=WHITE)
rng = np.random.default_rng(9); a = np.asarray(img).astype(np.int16); n = rng.normal(0, 3, a.shape[:2])[..., None]
img = Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))
out = "logo.png" if v == "ship" else f"scratch/logo-{v}.png"
img.save(out); print(out)
img.resize((64, 64), Image.LANCZOS).save(f"scratch/logo64-{v}.png"); print("64px saved")
