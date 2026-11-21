"""Israel flag-style wrap (blue & white with Magen David stars) for Tesla Model Y L."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw

tpl_path, out_path = sys.argv[1], sys.argv[2]
tpl = Image.open(tpl_path).convert("RGBA")
alpha = np.array(tpl)[..., 3]
S = 3                       # supersample factor
W = H = 1024 * S
BLUE = (0, 56, 184)         # Israel flag blue
WHITE = (250, 250, 252)

img = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(img)

def p(v):  # scale helper
    return v * S

def magen_david(cx, cy, r, width, rot=0.0, fill=None):
    """Two overlapping equilateral triangle outlines (as on the flag)."""
    for k in (0, 1):
        base = rot + (math.pi if k else 0) - math.pi / 2
        pts = [(p(cx) + p(r) * math.cos(base + i * 2 * math.pi / 3),
                p(cy) + p(r) * math.sin(base + i * 2 * math.pi / 3)) for i in range(3)]
        if fill:
            d.polygon(pts, fill=fill)
        d.line(pts + [pts[0]], fill=BLUE, width=p(width), joint="curve")

def rect(x0, y0, x1, y1, c=BLUE):
    d.rectangle([p(x0), p(y0), p(x1), p(y1)], fill=c)

# --- Hood (centre trapezoid): flag laid across it -------------------------
rect(360, 168, 670, 196)      # top stripe
rect(360, 340, 670, 368)      # bottom stripe
magen_david(512, 268, 58, 9)

# --- Front bumper (top wide panel): thin blue accent stripe --------------
rect(300, 72, 728, 84)

# --- Doors, both sides: stripes run along the car, star between them -----
for x_a, x_b, cx in ((38, 58, 108), (966, 986, 916)):
    # x mirrored for right side
    for xa, xb in ((x_a, x_b), (x_a + 120 if x_a < 500 else x_a - 120, x_b + 120 if x_a < 500 else x_b - 120)):
        rect(xa, 270, xb, 745)
    for cy in (400, 625):     # front door, rear door
        magen_david(cx, cy, 36, 6, rot=math.pi / 2)

# --- Rear spoiler bar: blue; liftgate: star ------------------------------
magen_david(512, 955, 34, 6)

# --- Rear bumper corners: blue stripe ------------------------------------
rect(230, 960, 390, 972)
rect(648, 960, 794, 972)

img = img.resize((1024, 1024), Image.LANCZOS)
# Solid-blue panels (pillars/roof rails, mirrors, rear spoiler), picked by connected component
from scipy import ndimage
lab, _ = ndimage.label(alpha > 128)
arr = np.array(img)
for seed in [(342, 413), (679, 415), (329, 772), (696, 773), (262, 281), (756, 283), (548, 859)]:
    m = ndimage.binary_dilation(lab == lab[seed[1], seed[0]], iterations=2)
    arr[m] = BLUE
img = Image.fromarray(arr)
out = np.dstack([np.array(img), alpha])
Image.fromarray(out, "RGBA").save(out_path, optimize=True)
