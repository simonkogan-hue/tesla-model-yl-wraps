# Tesla Model Y L Custom Wraps

Custom Paint Shop wraps for the **Tesla Model Y L**, built on Tesla's official template from [teslamotors/custom-wraps](https://github.com/teslamotors/custom-wraps/tree/main/modely-l).

## Wraps

| Israel Blue & White | Aurora Sweep |
|---|---|
| <img src="wraps/Israel_Blue_White.png" width="300"/> | <img src="wraps/Aurora_Sweep.png" width="300"/> |
| Israel flag colors: two blue stripes running the full length of each side (fender, doors, rear quarter), Magen David stars on the hood, doors and liftgate; blue pillars, mirrors and spoiler. | Midnight navy with a teal-to-violet glow along the sides and a starfield on the hood. |

Both files are 1024×1024 PNG and under 1 MB, as Tesla requires.

## How to install

### Option 1: Tesla mobile app (version 4.59.0 or later)
1. Open a wrap in the `wraps/` folder above, then download it (**Download raw file** button).
2. On your phone, save it to **Files** (best) or **Photos**. It needs to stay a PNG.
3. Open the Tesla app → **Creations** → **Wrap** → **Upload**, then pick the file.
4. In the car: **Toybox** → **Paint Shop** → **Wraps** tab → choose the wrap.

### Option 2: USB drive
1. Format a USB drive as exFAT or FAT32.
2. Make a folder named `Wraps` in the top level of the drive.
3. Copy the PNG files into `Wraps` (up to 10 files; keep file names short, letters/numbers/underscores only).
4. Plug the drive into the car's front USB port.
5. In the car: **Toybox** → **Paint Shop** → **Wraps** tab → choose the wrap.

## Requirements (from Tesla)
- PNG, 512×512 to 1024×1024 pixels
- Max 1 MB per file
- Design must follow the Model Y L template layout (`scripts/modely-l-template.png`)

## Rebuild or customize

The wraps are generated with Python from the template.

```bash
pip install pillow numpy scipy
python scripts/make_israel.py scripts/modely-l-template.png wraps/Israel_Blue_White.png
python scripts/make_wrap.py   scripts/modely-l-template.png wraps/Aurora_Sweep.png
```

Edit the colors, star sizes or stripe positions near the top of each script and rerun.

## Credits
Template © Tesla, from [teslamotors/custom-wraps](https://github.com/teslamotors/custom-wraps). The wraps are only shown in the car's on-screen 3D view, not on the real paint.
