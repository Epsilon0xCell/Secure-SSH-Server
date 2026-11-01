#!/usr/bin/env python3
"""Secure-SSH-Server introduction banner: a lamplit kitchen, nothing to read in it.
Foreground: a kitchen worktable close, checkered red cloth over one corner, a covered
silver dish on a folded cloth with steam escaping at the lid rim in one thin curl, and a
small sealed envelope with no writing on its face. Midground: the dumbwaiter hatch at
waist height, door standing open, the square car waiting inside at kitchen level with
its slatted front toward the viewer, the rope rising from the car into darkness. On the
wall beside the hatch, copper pans, a string of dried herbs, enamel jugs. Background:
the far wall in shadow, a doorway into a black corridor, and above the hatch the faint
rectangle of the next floor's closed door with a line of lamplight under it. One light
source only, a lamp over the table. No words, numbers, labels, logos, or screens."""
import sys
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
W, H = 1600, 900
v = sys.argv[1] if len(sys.argv) > 1 else "ship"
GREEN = (18, 42, 30); COPPER = (196, 120, 62); HERB = (96, 148, 84); RED = (168, 44, 40); WHITE = (238, 236, 226)
img = Image.new("RGB", (W, H), (12, 26, 18)); d = ImageDraw.Draw(img, "RGBA")
# walls: kitchen warmth near the lamp side, shadow swallowing the far wall
for x in range(W):
    t = x / W
    d.line([(x, 0), (x, H)], fill=(int(26 - 12 * t), int(48 - 20 * t), int(34 - 14 * t)))
d.rectangle([0, 700, W, H], fill=(16, 30, 20))  # floor
# doorway into a black corridor, far right background
d.rectangle([1330, 240, 1520, 700], fill=(4, 8, 6))
d.rectangle([1330, 240, 1520, 700], outline=(30, 48, 36), width=6)
# the next floor's closed door above the hatch, lamplight line under it
door_a = 120 if v == "v1" else 84
d.rectangle([880, 58, 1064, 238], outline=(140, 150, 130, door_a), width=4)
if v == "ship":
    d.rectangle([904, 82, 1040, 150], outline=(140, 150, 130, 60), width=3)
    d.rectangle([904, 162, 1040, 224], outline=(140, 150, 130, 60), width=3)
d.line([(884, 240), (1060, 240)], fill=(255, 206, 130), width=5)
# shelf of enamel jugs, string of dried herbs, row of copper pans
d.rectangle([120, 300, 560, 314], fill=(52, 40, 26))
for i, jx in enumerate((160, 260, 360, 460)):
    d.rectangle([jx, 252, jx + 52, 300], fill=WHITE)
    d.rectangle([jx, 252, jx + 52, 266], fill=(70, 92, 120))
    d.arc([jx + 40, 258, jx + 66, 288], 270, 90, fill=(200, 198, 188), width=4)
d.line([(600, 210), (600, 330)], fill=(150, 128, 84), width=3)
for i, hy in enumerate(range(228, 330, 26)):
    d.polygon([(600, hy), (586, hy + 18), (600, hy + 30), (614, hy + 18)], fill=HERB)
if v == "ship":
    d.line([(624, 214), (850, 214)], fill=(120, 96, 54), width=5)  # pan rail
for i, px in enumerate((640, 730, 820)):
    r = 34 - i * 4
    if v == "ship":
        d.line([(px, 214), (px, 240)], fill=(150, 88, 40), width=6)  # handle to the rail
    d.ellipse([px - r, 236, px + r, 236 + 2 * r], fill=COPPER, outline=(150, 88, 40), width=3)
    d.ellipse([px - 7, 224, px + 7, 240], outline=(150, 88, 40), width=4)
    d.ellipse([px - r + 10, 246, px - r + 26, 262], fill=(226, 160, 104))  # lamp highlight
# the dumbwaiter hatch at waist height, door open, car waiting inside
hx, hy, hw, hh = 880, 330, 240, 300
d.rectangle([hx - 14, hy - 14, hx + hw + 14, hy + hh + 14], fill=(40, 30, 20))  # hatch frame
d.rectangle([hx, hy, hx + hw, hy + hh], fill=(6, 10, 8))  # shaft dark
d.line([(hx + hw // 2, hy), (hx + hw // 2, hy + 74)], fill=(206, 170, 118), width=5)  # rope rising
d.rectangle([hx + 34, hy + 74, hx + hw - 34, hy + 226], fill=WHITE)  # the car, enamel white
for sx in range(hx + 52, hx + hw - 52, 22):  # slatted front
    d.line([(sx, hy + 92), (sx, hy + 208)], fill=(120, 118, 108), width=6)
d.rectangle([hx + 34, hy + 74, hx + hw - 34, hy + 92], fill=(214, 212, 200))
d.polygon([(hx - 14, hy - 14), (hx - 118, hy + 30), (hx - 118, hy + hh - 20), (hx - 14, hy + hh + 14)], fill=(214, 206, 188))  # open door
d.ellipse([hx - 104, hy + 150, hx - 88, hy + 166], fill=COPPER)  # door knob
# lamp over the table: the one light source
d.line([(360, 0), (360, 120)], fill=(24, 24, 22), width=5)
d.polygon([(312, 168), (408, 168), (382, 118), (338, 118)], fill=(30, 34, 30), outline=COPPER, width=2)
d.ellipse([338, 158, 382, 176], fill=(255, 208, 128))
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
gd.ellipse([60, 110, 700, 560], fill=(255, 196, 110, 54))
img = Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(40))).convert("RGB")
d = ImageDraw.Draw(img, "RGBA")
# worktable in the foreground
d.polygon([(60, 620), (900, 620), (980, 900), (0, 900)], fill=(74, 54, 34))
d.rectangle([60, 606, 900, 624], fill=(92, 68, 44))
# checkered red cloth over the near corner
cx0, cy0, cw = 560, 624, 330
d.polygon([(cx0, cy0), (cx0 + cw, cy0), (cx0 + cw + 44, 780), (cx0 + 30, 780)], fill=(238, 232, 222))
for i in range(6):
    for j in range(4):
        if (i + j) % 2 == 0:
            x = cx0 + 14 + i * 52 + j * 3; y = cy0 + 10 + j * 38
            d.polygon([(x, y), (x + 48, y), (x + 52, y + 34), (x + 3, y + 34)], fill=RED)
# covered silver dish on a folded cloth, steam at the lid rim
d.ellipse([210, 690, 470, 730], fill=(226, 222, 210))
if v == "ship":
    d.pieslice([226, 596, 454, 716], 180, 360, fill=(198, 202, 208))  # the cover, filled so it reads
    d.arc([226, 596, 454, 716], 180, 360, fill=(226, 228, 232), width=3)
else:
    d.arc([226, 596, 454, 716], 180, 360, fill=(206, 208, 214))
d.ellipse([226, 672, 454, 706], fill=(216, 218, 224))
d.ellipse([328, 590, 352, 606], fill=COPPER)  # lid knob
steam = 3 if v != "v1" else 1
for k in range(steam):
    bx = 300 + k * 42
    d.arc([bx, 520 - k * 8, bx + 34, 592 - k * 8], 270, 90, fill=(240, 242, 238, 170), width=4)
    d.arc([bx + 6, 492 - k * 8, bx + 40, 556 - k * 8], 90, 270, fill=(240, 242, 238, 130), width=3)
# sealed envelope beside the dish, face blank (on the bare table in the ship render)
if v == "ship":
    d.polygon([(286, 786), (452, 774), (462, 838), (296, 850)], fill=(240, 236, 222))
    d.polygon([(286, 786), (452, 774), (372, 816)], fill=(228, 224, 208))
    d.ellipse([418, 792, 442, 814], fill=(178, 44, 40))  # wax seal, no mark on it
else:
    d.polygon([(540, 700), (700, 686), (712, 752), (552, 766)], fill=(240, 236, 222))
    d.polygon([(540, 700), (700, 686), (628, 730)], fill=(228, 224, 208))
    d.ellipse([664, 706, 688, 728], fill=(178, 44, 40))
rng = np.random.default_rng(11); a = np.asarray(img).astype(np.int16); n = rng.normal(0, 4, a.shape[:2])[..., None]
img = Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))
out = "intro-banner.png" if v == "ship" else f"scratch/intro-{v}.png"
img.save(out); print(out)
