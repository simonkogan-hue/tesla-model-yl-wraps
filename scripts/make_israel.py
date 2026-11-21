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

# --- Sides: two flag stripes running the full length of the car ---------
# In the template, each side panel's inner edge (toward the sheet centre) is the
# beltline / hood line and its outer edge is the rocker. Following those edges row
# by row keeps the stripes parallel to the body lines and lets the upper stripe
# carry on through the front fender and rear quarter panel.
from scipy import ndimage
lab, _ = ndimage.label(alpha > 128)
lab3 = np.repeat(np.repeat(lab, S, 0), S, 1)
stripe = np.zeros((H, W), bool)
TOP_OFF, BOT_OFF, THICK = 12, 14, 20     # px (1024 scale)

def comp(seed):
    return lab[seed[1], seed[0]]

SIDES = {
    "left":  dict(fender=(209, 176), doors=[(166, 393), (162, 625)], quarter=(203, 852)),
    "right": dict(fender=(873, 178), doors=[(872, 394), (945, 626)], quarter=(785, 853)),
}
star_spots = []
for side, parts in SIDES.items():
    left = side == "left"
    ids_top = [comp(parts["fender"]), *map(comp, parts["doors"]), comp(parts["quarter"])]
    ids_bot = list(map(comp, parts["doors"]))
    def edge_fit(cid, use_inner, deg=2, upto=0.88):
        """Smooth (quadratic) fit of a panel edge x(y), ignoring the curved ends."""
        ys = np.where((lab == cid).any(1))[0]
        y0, y1 = ys.min(), ys.max()
        core = ys[(ys > y0 + 0.12 * (y1 - y0)) & (ys < y0 + upto * (y1 - y0))]
        pick_max = (use_inner and left) or (not use_inner and not left)
        ex = [np.where(lab[y] == cid)[0].max() if pick_max else np.where(lab[y] == cid)[0].min() for y in core]
        return np.poly1d(np.polyfit(core, ex, deg))

    def paint(cid, fit, off, sign):
        """sign=-1 paints toward smaller x from the edge, +1 toward larger x."""
        m = lab3 == cid
        rows = np.where(m.any(1))[0]
        xx = np.arange(W)
        for r in rows:
            e = fit(r / S) * S
            if sign < 0:
                a, b = e - p(off + THICK), e - p(off)
            else:
                a, b = e + p(off), e + p(off + THICK)
            band = (xx >= a) & (xx < b) & m[r]
            stripe[r, band] = True

    door_ids = set(ids_bot)
    for cid in ids_top:
        fit = edge_fit(cid, True, deg=1) if cid in door_ids else edge_fit(cid, True)
        paint(cid, fit, TOP_OFF, -1 if left else 1)
    for cid in ids_bot:
        ys, xs_all = np.where(lab == cid)
        paint(cid, edge_fit(cid, False, deg=1, upto=0.55), BOT_OFF, 1 if left else -1)
        # star centred between the two stripes, at the door's middle row
        cy = int(np.median(ys))
        row = np.where(lab[cy] == cid)[0]
        lo, hi = row.min() + BOT_OFF + THICK, row.max() - TOP_OFF - THICK
        if not left:
            lo, hi = row.min() + TOP_OFF + THICK, row.max() - BOT_OFF - THICK
        star_spots.append(((lo + hi) / 2, cy, (hi - lo) / 2 - 12))

arr3 = np.array(img)
arr3[stripe] = BLUE
img = Image.fromarray(arr3)
d = ImageDraw.Draw(img)
for cx, cy, r in star_spots:
    magen_david(cx, cy, min(r, 40), 6, rot=math.pi / 2)

# --- Rear spoiler bar: blue; liftgate: star ------------------------------
magen_david(512, 955, 34, 6)

# --- Rear bumper corners: blue stripe ------------------------------------
rect(230, 960, 390, 972)
rect(648, 960, 794, 972)

img = img.resize((1024, 1024), Image.LANCZOS)
# Solid-blue panels (pillars/roof rails, mirrors, rear spoiler), picked by connected component
arr = np.array(img)
for seed in [(342, 413), (679, 415), (329, 772), (696, 773), (262, 281), (756, 283), (548, 859)]:
    m = ndimage.binary_dilation(lab == lab[seed[1], seed[0]], iterations=2)
    arr[m] = BLUE
img = Image.fromarray(arr)
out = np.dstack([np.array(img), alpha])
Image.fromarray(out, "RGBA").save(out_path, optimize=True)
