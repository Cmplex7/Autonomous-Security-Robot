# -*- coding: utf-8 -*-
"""
Convert anh Sharingan (hinh tron) -> polar iris map cho Uncanny Eyes.

Texture 256x64: cot = goc (0-360 do), hang = ban kinh.
Voi iScale = 120 (IRIS_MIN = IRIS_MAX = 120), hang d tuong ung
ban kinh q = (127 - 2*d)/128: hang 0 = mep ngoai iris, hang 63 = tam.

Cach dung:
  python make_iris.py <anh_vao> <ten_mang> <file_ra.h> [cx cy r]
  (cx cy r tuy chon: tam va ban kinh hinh tron trong anh; mac dinh
   tam anh va r = min(w,h)/2)

Vi du:
  python make_iris.py anh1.jpg iris_tomoe iris_tomoe.h
"""
import sys
import math
from PIL import Image

IRIS_MAP_WIDTH = 256
IRIS_MAP_HEIGHT = 64

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    src_path, array_name, out_path = sys.argv[1:4]

    im = Image.open(src_path).convert('RGB')
    w, h = im.size
    if len(sys.argv) >= 7:
        cx, cy, r = float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
    else:
        cx, cy = w / 2.0, h / 2.0
        r = min(w, h) / 2.0

    # Lay mau bilinear cho muot
    big = im.resize((w * 2, h * 2), Image.LANCZOS)
    px = big.load()

    vals = []
    preview = Image.new('RGB', (IRIS_MAP_WIDTH, IRIS_MAP_HEIGHT))
    pv = preview.load()
    for d in range(IRIS_MAP_HEIGHT):
        q = (127 - 2 * d) / 128.0          # 0.99 (mep) -> 0.008 (tam)
        for c in range(IRIS_MAP_WIDTH):
            ang = 2 * math.pi * c / IRIS_MAP_WIDTH - math.pi
            x = cx + q * r * math.cos(ang)
            y = cy + q * r * math.sin(ang)
            xi = min(max(int(round(x * 2)), 0), w * 2 - 1)
            yi = min(max(int(round(y * 2)), 0), h * 2 - 1)
            R, G, B = px[xi, yi]
            pv[c, d] = (R, G, B)
            vals.append(((R & 0xF8) << 8) | ((G & 0xFC) << 3) | (B >> 3))

    with open(out_path, 'w') as f:
        f.write('// Sinh tu %s boi make_iris.py\n' % src_path)
        f.write('// Polar iris map %dx%d, dung voi IRIS_MIN=IRIS_MAX=120\n\n'
                % (IRIS_MAP_WIDTH, IRIS_MAP_HEIGHT))
        f.write('const uint16_t %s[%d * %d] = {\n'
                % (array_name, IRIS_MAP_HEIGHT, IRIS_MAP_WIDTH))
        for i in range(0, len(vals), 12):
            chunk = ', '.join('0x%04X' % v for v in vals[i:i + 12])
            f.write('  ' + chunk + ',\n')
        f.write('};\n')

    # Anh preview: texture trai phang + dung lai hinh tron de soat mat
    preview.resize((IRIS_MAP_WIDTH, IRIS_MAP_HEIGHT * 2), Image.NEAREST) \
           .save(out_path.replace('.h', '_unwrap.png'))
    size = 240
    recon = Image.new('RGB', (size, size), (255, 255, 255))
    rp = recon.load()
    for y in range(size):
        for x in range(size):
            dx, dy = x - size / 2 + 0.5, y - size / 2 + 0.5
            dist = math.sqrt(dx * dx + dy * dy) / (size / 2)
            if dist >= 1.0:
                continue
            d = int((127 - dist * 128) * 120 / 240)   # giong firmware, iScale=120
            d = min(max(d, 0), IRIS_MAP_HEIGHT - 1)
            c = int((math.atan2(dy, dx) + math.pi) / (2 * math.pi) * IRIS_MAP_WIDTH) \
                % IRIS_MAP_WIDTH
            rp[x, y] = pv[c, d]
    recon.save(out_path.replace('.h', '_preview.png'))
    print('OK: %s (+_unwrap.png, +_preview.png)' % out_path)

if __name__ == '__main__':
    main()
