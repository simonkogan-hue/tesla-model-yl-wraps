"""Build an original 'Aurora Sweep' wrap for the Tesla Model Y L from the official template."""
import sys
import numpy as np
from PIL import Image, ImageFilter

tpl_path, out_path = sys.argv[1], sys.argv[2]
tpl = Image.open(tpl_path).convert("RGBA")
W, H = tpl.size
alpha = np.array(tpl)[..., 3]

y, x = np.mgrid[0:H, 0:W].astype(np.float32)
xn, yn = x / W, y / H

def lerp(a, b, t):
    t = np.clip(t, 0, 1)[..., None]
    return np.array(a, np.float32) * (1 - t) + np.array(b, np.float32) * t

# Base: midnight navy, deepening toward the rear (bottom of the sheet).
img = lerp((22, 30, 58), (8, 10, 22), yn ** 1.3)

# Distance from the centre line -> side panels get the aurora, roof stays calm.
side = np.abs(xn - 0.5) * 2  # 0 at centre, 1 at edges

# Aurora band: sweeps up from the rear-low corner toward the front (top of sheet).
# Mirrored left/right automatically because it uses |x - 0.5|.
u = (1 - yn) * 0.9 + side * 0.55  # diagonal coordinate
wave = 0.05 * np.sin(yn * 9.0 + side * 4.0)
band_center = 0.95 + wave
d = (u - band_center) / 0.16
glow = np.exp(-d ** 2)

# Colour along the band: teal -> cyan -> violet
hue_t = np.clip((1 - yn) * 1.1, 0, 1)
teal, cyan, violet = (0, 200, 170), (60, 230, 255), (150, 90, 255)
band_col = np.where(
    (hue_t < 0.5)[..., None],
    lerp(teal, cyan, hue_t * 2),
    lerp(cyan, violet, (hue_t - 0.5) * 2),
)
img = img * (1 - glow[..., None] * 0.9) + band_col * (glow[..., None] * 0.9)

# Thin pinstripe trailing the band.
ps = np.exp(-(((u - (band_center - 0.24)) / 0.012) ** 2)) * (side > 0.6)
img = img * (1 - ps[..., None]) + np.array((235, 240, 255), np.float32) * ps[..., None]

# Subtle star-speckle on the roof/hood for depth.
rng = np.random.default_rng(7)
stars = (rng.random((H, W)) > 0.9985) & (side < 0.45)
star_layer = Image.fromarray((stars * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
s = np.array(star_layer, np.float32)[..., None] / 255.0 * 1.6
img = np.clip(img + s * 200, 0, 255)

out = np.dstack([img.astype(np.uint8), alpha])
Image.fromarray(out, "RGBA").save(out_path, optimize=True)
