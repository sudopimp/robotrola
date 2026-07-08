#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
stls = sorted((root / "cad/stl").glob("*.stl"))
W, H = 1400, max(600, 80 + 48 * len(stls))
img = Image.new("RGB", (W, H), "#f4ead9")
d = ImageDraw.Draw(img)
d.text((40, 30), "Robotrola CAD Catalog", fill="#2b1b10")
y = 90
for stl in stls:
    d.rectangle((40, y, 1360, y + 34), outline="#9a612f")
    d.text((60, y + 9), stl.name, fill="#2b1b10")
    y += 48
out = root / "assets/visual/cad_catalog.png"
out.parent.mkdir(parents=True, exist_ok=True)
img.save(out)
print(out)
