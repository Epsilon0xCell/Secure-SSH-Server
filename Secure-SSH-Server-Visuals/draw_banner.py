#!/usr/bin/env python3
"""Secure-SSH-Server wordmark banner: a cutaway of a tall old house, floors stacked like
shelves, cut open along the front. Down the middle runs the dumbwaiter shaft from cellar
to attic. At the kitchen level, bottom left, a cook slides a covered dish and a folded
note into the car. Halfway up, the car passes a landing where a hand has just drawn back.
At the top floor a chambermaid waits by an open hatch holding an engagement ring box.
Copper pans and a checkered red cloth fill the kitchen; the upper rooms get plainer as
they rise, enamel white walls, narrow beds, a washstand. In the scullery corner a chalk
delivery board lists the house name as Secure-SSH-Server in Anek Odia, in the same hand
as the kitchen orders. Warm light pools in the kitchen and thins floor by floor."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
W, H = 2560, 640
v = sys.argv[1] if len(sys.argv) > 1 else "ship"
GREEN = (18, 42, 30); COPPER = (196, 120, 62); HERB = (96, 148, 84); RED = (168, 44, 40); WHITE = (238, 236, 226)
img = Image.new("RGB", (W, H), (24, 34, 28)); d = ImageDraw.Draw(img, "RGBA")
# house shell and floor bands, plainer as they rise
floors = [(0, 160, (52, 54, 50)), (160, 320, (58, 60, 54)), (320, 480, (64, 64, 56)), (480, 640, (44, 48, 38))]
for y0, y1, col in floors:
    d.rectangle([180, y0, 2380, y1], fill=col)
    d.rectangle([180, y1 - 10, 2380, y1], fill=(30, 30, 26))
d.rectangle([180, 0, 2380, 640], outline=(16, 18, 16), width=10)
# the shaft, a narrow vertical slot from cellar to attic, the house's lit spine
sx0, sx1 = 1180, 1330
d.rectangle([sx0, 8, sx1, 632], fill=(14, 16, 14))
d.line([(1255, 8), (1255, 300)], fill=(216, 186, 132), width=5)
d.ellipse([1228, 16, 1282, 70], outline=COPPER, width=7)  # pulley at the top
# car halfway up, passing the landing
d.rectangle([1204, 300, 1306, 384], fill=WHITE)
for lx in range(1222, 1296, 18):
    d.line([(lx, 314), (lx, 370)], fill=(120, 118, 108), width=5)
d.line([(1255, 384), (1255, 632)], fill=(216, 186, 132), width=5)
# a hand just drawn back at the halfway landing (right of the shaft)
d.ellipse([1360, 322, 1420, 348], fill=(222, 196, 168))
for fx in range(4):
    d.rectangle([1408 + fx * 13, 306 - fx * 3, 1418 + fx * 13, 330 - fx * 3], fill=(222, 196, 168))
d.rectangle([1330, 300, 1352, 384], fill=(214, 206, 188))  # landing hatch edge
# top floor: chambermaid by an open hatch, ring box in her hands; narrow bed, washstand
mx, my = 1520, 66
d.ellipse([mx - 17, my - 34, mx + 17, my], fill=(222, 196, 168))
d.polygon([(mx - 24, my + 76), (mx - 16, my), (mx + 16, my), (mx + 24, my + 76)], fill=(70, 92, 120))
d.polygon([(mx - 24, my + 22), (mx + 24, my + 22), (mx + 20, my + 40), (mx - 20, my + 40)], fill=WHITE)  # apron
d.rectangle([mx + 22, my + 34, mx + 52, my + 52], fill=(120, 40, 44))  # ring box
d.rectangle([mx + 22, my + 34, mx + 52, my + 41], fill=(232, 226, 210))
d.ellipse([mx + 33, my + 24, mx + 41, my + 34], fill=(220, 224, 228))  # the ring, upright
d.rectangle([1760, 96, 2050, 132], fill=(214, 212, 200)); d.rectangle([1760, 132, 2050, 148], fill=(90, 80, 66))  # narrow bed
if v != "v1":
    d.rectangle([1760, 96, 1830, 132], fill=(244, 242, 234)); d.rectangle([1900, 96, 2050, 132], fill=HERB)  # pillow and blanket
    d.rectangle([300, 40, 380, 120], outline=(150, 152, 140), width=4)  # faint attic window
    d.line([(340, 40), (340, 120)], fill=(150, 152, 140), width=3)
d.rectangle([2180, 84, 2246, 148], fill=WHITE); d.ellipse([2192, 70, 2234, 88], fill=(206, 208, 214))  # washstand and basin
# middle floor: a plainer room, a bed and a chair, hatch door closed
d.rectangle([420, 250, 660, 282], fill=(206, 204, 194)); d.rectangle([420, 282, 660, 296], fill=(84, 74, 60))
if v != "v1":
    d.rectangle([420, 250, 486, 282], fill=(244, 242, 234)); d.rectangle([540, 250, 660, 282], fill=(120, 128, 110))
d.rectangle([820, 236, 856, 296], fill=(84, 74, 60))
if v != "v1":
    d.rectangle([820, 236, 856, 262], fill=(100, 88, 70))  # chair back above its seat
d.rectangle([sx0 - 130, 196, sx0 - 108, 300], fill=(200, 194, 180))  # closed hatch door, this floor
# kitchen floor: copper pans, checkered cloth, the cook loading the car
for i, px in enumerate((330, 420, 510)):
    r = 30 - i * 3
    d.line([(px, 500), (px, 522)], fill=(150, 88, 40), width=6)
    d.ellipse([px - r, 522, px + r, 522 + 2 * r], fill=COPPER, outline=(150, 88, 40), width=3)
d.polygon([(640, 520), (900, 520), (930, 632), (660, 632)], fill=(238, 232, 222))
for i in range(5):
    for j in range(2):
        if (i + j) % 2 == 0:
            x = 656 + i * 52; y = 528 + j * 48
            d.polygon([(x, y), (x + 46, y), (x + 50, y + 42), (x + 3, y + 42)], fill=RED)
# cook at the hatch, sliding a covered dish and a folded note into the low car
ckx, cky = 1010, 500
d.ellipse([ckx - 18, cky - 36, ckx + 18, cky], fill=(222, 196, 168))
d.arc([ckx - 20, cky - 42, ckx + 20, cky - 6], 180, 360, fill=(240, 238, 230), width=8)  # cook's cap
d.polygon([(ckx - 26, cky + 84), (ckx - 18, cky), (ckx + 18, cky), (ckx + 26, cky + 84)], fill=(200, 196, 186))
d.line([(ckx + 16, cky + 26), (ckx + 84, cky + 44)], fill=(222, 196, 168), width=13)  # arm reaching to the car
d.rectangle([sx0 - 96, 520, sx0 - 24, 610], fill=WHITE)  # low car at kitchen level
d.ellipse([sx0 - 88, 500, sx0 - 32, 524], fill=(206, 208, 214))  # covered dish going in
d.polygon([(sx0 - 80, 540), (sx0 - 44, 534), (sx0 - 40, 560), (sx0 - 76, 566)], fill=(240, 236, 222))  # folded note
# scullery chalk delivery board with the house name, bottom right
bw = 620 if v == "ship" else 480
bx0, by0 = 2380 - bw - 60, 486
d.rectangle([bx0, by0, bx0 + bw, by0 + 118], fill=(22, 34, 26), outline=(150, 128, 84), width=4)
f = ImageFont.truetype("fonts/AnekOdia.ttf", 46 if v == "ship" else 36)
txt = "Secure-SSH-Server"; tw = d.textlength(txt, font=f)
d.text((bx0 + (bw - tw) / 2, by0 + 20), txt, font=f, fill=(240, 240, 232))
for ly in (by0 + 84, by0 + 98):  # ruled chalk lines under the name, like the day's other orders
    d.line([(bx0 + 26, ly), (bx0 + bw - 26, ly)], fill=(200, 204, 196, 120), width=2)
# warm light pooled in the kitchen, thinning upward
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
gd.ellipse([200, 420, 1500, 660], fill=(255, 196, 110, 46))
gd.ellipse([1100, 240, 1500, 460], fill=(255, 196, 110, 20))
img = Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(34))).convert("RGB")
rng = np.random.default_rng(5); a = np.asarray(img).astype(np.int16); n = rng.normal(0, 4, a.shape[:2])[..., None]
img = Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))
out = "banner.png" if v == "ship" else f"scratch/banner-{v}.png"
img.save(out); print(out)
