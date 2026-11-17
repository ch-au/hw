"""Generates Data/Maps/Schlosspark/map.png (+ previews): playable castle with big tower,
park terrace and a high-rise estate on a wooded hill.  Cartoon style, drawn from scratch."""
import math, random, sys, os
import cairo
from draw import *

W, H = 4096, 2048
OUTDIR = sys.argv[1]
s, c = surface(W, H)
rnd = random.Random(7)

PARK_Y = 1600
TERR_Y = 1440


# ---------------------------------------------------------------- ground
def earth_fill(seed):
    def f(cc, ext):
        x0, y0, x1, y1 = ext
        g = cairo.LinearGradient(0, y0, 0, y1)
        g.add_color_stop_rgb(0, *EARTH_L)
        g.add_color_stop_rgb(0.25, *EARTH)
        g.add_color_stop_rgb(1, *EARTH_D)
        cc.set_source(g); cc.paint()
        r = random.Random(seed)
        for _ in range(int((x1 - x0) * (y1 - y0) / 5000)):
            px, py = r.uniform(x0, x1), r.uniform(y0 + 40, y1)
            rr = r.uniform(8, 26)
            shape(cc, lambda q: blob_path(q, px, py, rr * 1.3, rr, 7, 0.25, r.randint(0, 999)),
                  rgb('#9B8A78') if r.random() < 0.6 else rgb('#7D6E61'), lw=3)
        # roots / cracks
        cc.set_source_rgba(*EARTH_D, 0.6); cc.set_line_width(3)
        for _ in range(int((x1 - x0) / 60)):
            px, py = r.uniform(x0, x1), r.uniform(y0 + 30, y0 + 160)
            cc.move_to(px, py)
            for k in range(4):
                px += r.uniform(-25, 25); py += r.uniform(10, 30)
                cc.line_to(px, py)
            cc.stroke()
    return f


def ground(x_top0, x_top1, x_bot0, x_bot1, top_fn, seed):
    def path(cc):
        n = 80
        cc.move_to(x_bot0, H + 10)
        # left side, a bit ragged
        for i in range(1, 8):
            t = i / 8
            cc.line_to(x_bot0 + (x_top0 - x_bot0) * t + random.Random(seed + i).uniform(-25, 25), H - (H - top_fn(x_top0)) * t)
        for i in range(n + 1):
            x = x_top0 + (x_top1 - x_top0) * i / n
            cc.line_to(x, top_fn(x))
        for i in range(1, 8):
            t = 1 - i / 8
            cc.line_to(x_bot1 + (x_top1 - x_bot1) * t + random.Random(seed + 50 + i).uniform(-25, 25), H - (H - top_fn(x_top1)) * t)
        cc.line_to(x_bot1, H + 10)
        cc.close_path()
    shape(c, path, earth_fill(seed))

    # grass cap with drips
    def gpath(cc):
        n = 120
        r = random.Random(seed + 3)
        cc.move_to(x_top0 - 8, top_fn(x_top0) - 6)
        for i in range(n + 1):
            x = x_top0 + (x_top1 - x_top0) * i / n
            cc.line_to(x, top_fn(x) - 10)
        cc.line_to(x_top1 + 8, top_fn(x_top1) + 30)
        for i in range(n, -1, -1):
            x = x_top0 + (x_top1 - x_top0) * i / n
            d = 30 + (r.uniform(0, 34) if i % 3 == 0 else r.uniform(0, 10))
            cc.line_to(x, top_fn(x) + d)
        cc.close_path()

    def gfill(cc, ext):
        vgrad(cc, ext, GRASS_L, GRASS)
        r = random.Random(seed + 9)
        cc.set_source_rgba(*GRASS_D, 0.7); cc.set_line_width(2.5)
        x0, y0, x1, y1 = ext
        for _ in range(int((x1 - x0) / 9)):
            x = r.uniform(x0, x1); y = top_fn(min(max(x, x_top0), x_top1))
            cc.move_to(x, y + r.uniform(8, 26)); cc.line_to(x + r.uniform(-5, 5), y + r.uniform(-4, 6)); cc.stroke()
    shape(c, gpath, gfill)


def left_top(x):
    return PARK_Y + 6 * math.sin(x / 90.0)


ground(170, 2210, 290, 2110, left_top, 11)


def right_top(x):
    t = (x - 2380) / (3990 - 2380)
    return 1700 - 150 * math.sin(t * math.pi * 0.85) + 10 * math.sin(x / 70.0)


ground(2380, 3990, 2470, 3930, right_top, 23)

# ---------------------------------------------------------------- terrace wall
shape(c, lambda q: rect_path(q, 230, TERR_Y, 1900, PARK_Y - TERR_Y + 12),
      stone_fill(BASALT, BASALT_D, BASALT_L, bh=32, bw=70, seed=4))
# basement windows in the terrace
for x in list(range(300, 1060, 150)) + list(range(1480, 2100, 150)):
    shape(c, lambda q: arch_path(q, x, TERR_Y + 50, 46, 70), GLASS, lw=4)
    c.set_source_rgba(*BASALT_L, 1); c.set_line_width(3)
    for k in range(1, 4):
        c.move_to(x + k * 11.5, TERR_Y + 60); c.line_to(x + k * 11.5, TERR_Y + 120)
    c.stroke()

# ---------------------------------------------------------------- castle
def wall(x, y, w, h, seed, base=SAND):
    shape(c, lambda q: rect_path(q, x, y, w, h), stone_fill(base, SAND_D, SAND_L, seed=seed))


def cornice(x, y, w, h=14):
    shape(c, lambda q: rect_path(q, x, y, w, h), SAND_L, lw=4)


# far-right low wing
wall(2005, 1250, 110, TERR_Y - 1250, 31)
shape(c, lambda q: poly_path(q, [(1995, 1252), (2125, 1252), (2095, 1150), (2025, 1150)]), slate_fill(), lw=LW)
cone(c, 2060, 1150, 44, 1075)
finial(c, 2060, 1075, 22, 7)
window(c, 2035, 1300, 40, 70, arched=False)

# left wing (round corner building)
wall(330, 1150, 240, TERR_Y - 1150, 5)
cornice(320, 1142, 260)
shape(c, lambda q: poly_path(q, [(315, 1145), (585, 1145), (545, 1020), (355, 1020)]), slate_fill(seed=5), lw=LW)
shape(c, lambda q: poly_path(q, [(355, 1022), (545, 1022), (500, 990), (400, 990)]), slate_fill(SLATE_D), lw=5)
for wx in (370, 470):
    window(c, wx, 1210, 50, 100)
    window(c, wx, 1340, 50, 70)

# main hall
wall(860, 1060, 840, TERR_Y - 1060, 7)
# hall roof
shape(c, lambda q: poly_path(q, [(845, 1068), (1715, 1068), (1645, 790), (915, 790)]), slate_fill(seed=8), lw=LW)
shape(c, lambda q: rect_path(q, 912, 782, 736, 12), SLATE_D, lw=4)
# upper little dormers
for dx in (1010, 1160, 1400, 1550):
    shape(c, lambda q: poly_path(q, [(dx - 26, 900), (dx, 852), (dx + 26, 900)]), SLATE_D, lw=4)
    shape(c, lambda q: poly_path(q, [(dx - 12, 898), (dx, 875), (dx + 12, 898)]), GLASS, lw=3)
# lantern cupola
shape(c, lambda q: rect_path(q, 1240, 655, 84, 140), slate_fill(SLATE_D, SLATE, SLATE_L, seed=3), lw=LW)
for k in range(3):
    shape(c, lambda q: rect_path(q, 1252 + k * 22, 680, 14, 70), GLASS, lw=3)
shape(c, lambda q: rect_path(q, 1230, 645, 104, 14), SLATE_D, lw=4)
cone(c, 1282, 648, 120, 555)
finial(c, 1282, 555, 40, 8)
# dormers
for i, dx in enumerate((960, 1090, 1225, 1360, 1495, 1625)):
    if dx == 1625:
        continue
    shape(c, lambda q: rect_path(q, dx - 42, 975, 84, 100), stone_fill(SAND, SAND_D, SAND_L, bh=20, bw=42, seed=i), lw=5)
    window(c, dx - 22, 995, 44, 60)
    shape(c, lambda q: poly_path(q, [(dx - 52, 980), (dx, 900), (dx + 52, 980)]), slate_fill(seed=i, rowh=14), lw=5)
    finial(c, dx, 905, 26, 6)
cornice(850, 1060, 860, 16)
# facade windows
for k, wx in enumerate(range(900, 1660, 95)):
    window(c, wx, 1120, 40, 78, arched=False)
    window(c, wx, 1300, 44, 96, arched=True)
cornice(860, 1240, 840, 12)
# balcony in the middle
shape(c, lambda q: rect_path(q, 1060, 1230, 330, 34), SAND_L, lw=5)
c.set_source_rgb(*OUT); c.set_line_width(3)
for bx in range(1072, 1390, 18):
    c.move_to(bx, 1236); c.line_to(bx, 1260)
c.stroke()

# right gable wing
wall(1690, 960, 320, TERR_Y - 960, 13)
gable = [(1680, 968), (1850, 715), (2020, 968)]
shape(c, lambda q: poly_path(q, gable), stone_fill(SAND, SAND_D, SAND_L, seed=14))
# gable coping (thick stone edge)
c.set_source_rgb(*OUT); c.set_line_width(26); poly_path(c, gable, close=False); c.stroke()
c.set_source_rgb(*SAND_L); c.set_line_width(16); poly_path(c, gable, close=False); c.stroke()
finial(c, 1850, 712, 30, 8)
window(c, 1828, 820, 44, 70, arched=False)
for wx in (1720, 1800, 1880, 1950):
    window(c, wx, 1010, 38, 76, arched=False)
for wx in (1730, 1900):
    window(c, wx, 1110, 70, 90, arched=False)
# round bay with balustrade
shape(c, lambda q: rect_path(q, 1720, 1215, 260, 225), stone_fill(SAND_L, SAND_D, SAND_L, seed=15))
shape(c, lambda q: rect_path(q, 1710, 1195, 280, 26), SAND_L, lw=5)
for wx in (1745, 1815, 1885):
    window(c, wx, 1260, 40, 110, arched=True)

# ---------------------------------------------------------------- big tower
TX0, TX1 = 560, 860
wall(TX0, 450, TX1 - TX0, TERR_Y - 450, 21)
# loggia / arcade
shape(c, lambda q: rect_path(q, 535, 1000, 350, 100), stone_fill(SAND_L, SAND_D, SAND_L, seed=22))
for ax in range(552, 870, 52):
    shape(c, lambda q: arch_path(q, ax, 1022, 34, 64), rgb('#20283A'), lw=4)
shape(c, lambda q: arch_path(q, 680, 1012, 60, 80), rgb('#20283A'), lw=4)
cornice(525, 990, 370, 16)
cornice(525, 1098, 370, 14)
# flanking pinnacle turrets at the loggia
for px in (545, 875):
    shape(c, lambda q: rect_path(q, px - 22, 940, 44, 60), stone_fill(SAND, SAND_D, SAND_L, bh=20, bw=22), lw=5)
    cone(c, px, 942, 58, 860, lw=5)
    finial(c, px, 860, 20, 6)
# roof slopes of hall touching the tower
# tower windows
for wy in (590, 720, 850):
    window(c, 640, wy, 30, 64)
    window(c, 750, wy, 30, 64)
for wy in (1150, 1280):
    window(c, 615, wy, 56, 100)
    window(c, 750, wy, 56, 100)
# clock
shape(c, lambda q: q.arc(710, 520, 40, 0, 2 * math.pi), SAND_L, lw=5)
shape(c, lambda q: q.arc(710, 520, 30, 0, 2 * math.pi), rgb('#F4EBD0'), lw=3)
c.set_source_rgb(*OUT); c.set_line_width(4)
c.move_to(710, 520); c.line_to(710, 497); c.move_to(710, 520); c.line_to(728, 528); c.stroke()
for k in range(12):
    a = k * math.pi / 6
    c.arc(710 + 24 * math.cos(a), 520 + 24 * math.sin(a), 2, 0, 2 * math.pi); c.fill()
# corbel cornice + parapet
shape(c, lambda q: rect_path(q, 540, 420, 340, 34), SAND_L, lw=5)
for kx in range(548, 880, 28):
    shape(c, lambda q: poly_path(q, [(kx, 454), (kx + 16, 454), (kx + 12, 478), (kx + 4, 478)]), SAND, lw=3)
shape(c, lambda q: rect_path(q, 545, 378, 330, 44), SAND, lw=5)
c.set_source_rgb(*OUT)
for kx in range(560, 870, 20):
    shape(c, lambda q: q.arc(kx, 400, 6, 0, 2 * math.pi), rgb('#5C4A35'), lw=0)
shape(c, lambda q: rect_path(q, 538, 372, 344, 12), SAND_L, lw=4)
# crown drum
wall(640, 230, 140, 145, 24)
for ox in (655, 700, 745):
    shape(c, lambda q: arch_path(q, ox, 270, 20, 50), rgb('#20283A'), lw=3)
cornice(632, 222, 156, 12)
# corner turrets
for tx in (600, 820):
    wall(tx - 32, 245, 64, 130, 25 + tx)
    shape(c, lambda q: arch_path(q, tx - 8, 280, 16, 40), rgb('#20283A'), lw=3)
    cornice(tx - 38, 238, 76, 12)
    cone(c, tx, 240, 76, 150)
    finial(c, tx, 150, 26, 7)
# main pointed roof
cone(c, 710, 226, 176, 95, flare=4)
finial(c, 710, 95, 55, 10)

# ---------------------------------------------------------------- terrace front: balustrade + stairs
def balustrade(x0, x1, y):
    shape(c, lambda q: rect_path(q, x0, y + 34, x1 - x0, 12), SAND_L, lw=4)   # bottom rail
    for bx in range(int(x0) + 10, int(x1) - 6, 22):
        shape(c, lambda q: blob_path(q, bx, y + 22, 6, 13, 8, 0.0), SAND_L, lw=3)
    shape(c, lambda q: rect_path(q, x0 - 4, y, x1 - x0 + 8, 13), SAND_L, lw=4)  # top rail
    for px in range(int(x0), int(x1) + 1, 220):
        shape(c, lambda q: rect_path(q, px - 10, y - 6, 20, 52), SAND, lw=4)


balustrade(232, 1100, TERR_Y - 46)
balustrade(1400, 2128, TERR_Y - 46)
# stairs
for k in range(8):
    yy = TERR_Y + k * 20
    shape(c, lambda q: rect_path(q, 1120 - k * 6, yy, 260 + k * 12, 22),
          lambda q, e: vgrad(q, e, rgb('#B9AFA4'), rgb('#8B8178')), lw=4)
# stair pillars with bronze stags
for px in (1092, 1408):
    shape(c, lambda q: rect_path(q, px - 26, 1360, 52, PARK_Y - 1360), stone_fill(BASALT, BASALT_D, BASALT_L, bh=24, bw=26), lw=5)
    shape(c, lambda q: rect_path(q, px - 32, 1350, 64, 16), BASALT_L, lw=4)
    sgn = 1 if px < 1200 else -1

    def stag(q, px=px, sgn=sgn):
        pts = [(-24, 0), (-22, -34), (-26, -46), (-12, -50), (14, -50), (20, -62), (22, -84),
               (30, -86), (28, -60), (24, -46), (22, -34), (24, 0), (16, 0), (14, -30), (-12, -30), (-14, 0)]
        poly_path(q, [(px + sgn * x, 1350 + y) for x, y in pts])
    shape(c, stag, lambda q, e: vgrad(q, e, BRONZE_L, BRONZE), lw=4)
    # antlers
    c.set_source_rgb(*OUT); c.set_line_width(5)
    ax, ay = px + sgn * 26, 1350 - 86
    c.move_to(ax, ay); c.line_to(ax - sgn * 12, ay - 26); c.move_to(ax - sgn * 6, ay - 12); c.line_to(ax - sgn * 22, ay - 16)
    c.move_to(ax, ay); c.line_to(ax + sgn * 8, ay - 28); c.move_to(ax + sgn * 4, ay - 14); c.line_to(ax + sgn * 18, ay - 20)
    c.stroke()

# ---------------------------------------------------------------- topiary in the park
def yew_ball(x, r, seed):
    foliage(c, x, PARK_Y - r * 0.85, r, r * 0.95, rgb('#2F7A2A'), rgb('#5BAA3C'), rgb('#1D5219'), seed)


def yew_cone(x, w, h, seed):
    def p(q):
        q.move_to(x - w / 2, PARK_Y)
        q.curve_to(x - w / 2, PARK_Y - h * 0.5, x - w * 0.15, PARK_Y - h * 0.9, x, PARK_Y - h)
        q.curve_to(x + w * 0.15, PARK_Y - h * 0.9, x + w / 2, PARK_Y - h * 0.5, x + w / 2, PARK_Y)
        q.close_path()

    def f(q, e):
        vgrad(q, e, rgb('#5BAA3C'), rgb('#2F7A2A'))
        side_shade(q, e, 0.35, alpha=0.4)
    shape(c, p, f)


yew_ball(330, 85, 1)
yew_cone(950, 120, 230, 2)
yew_ball(1620, 95, 3)
yew_cone(2040, 110, 210, 4)
# red/pink flower beds along the park
for fx in range(260, 2160, 26):
    if 1060 < fx < 1440:
        continue
    col = [rgb('#E04848'), rgb('#F5E15A'), rgb('#F3F3F3')][int(fx / 26) % 3]
    shape(c, lambda q: q.arc(fx, PARK_Y - 8, 7, 0, 2 * math.pi), col, lw=3)

# ---------------------------------------------------------------- high-rise estate
def highrise(x, top, w, base_y, body, shade, band, seed, roof_boxes=2):
    r = random.Random(seed)
    base_y = max(right_top(x + k * w / 10) for k in range(11)) + 12

    def f(q, e):
        q.set_source_rgb(*body); q.paint()
        fh = 34
        y = top + 30
        while y < base_y:
            # recessed loggia strip (dark)
            q.set_source_rgb(*rgb('#3A4250'))
            q.rectangle(x + 10, y + 8, w - 20, fh - 16); q.fill()
            # windows reflections / awnings
            cx = x + 14
            while cx < x + w - 30:
                cw = 30
                roll = r.random()
                if roll < 0.12:
                    q.set_source_rgb(*r.choice([rgb('#E8792F'), rgb('#F2C230'), rgb('#C8443C'), rgb('#4E86C6'), rgb('#7DB65A')]))
                    q.rectangle(cx, y + 8, cw - 4, (fh - 16) * 0.7); q.fill()
                elif roll < 0.55:
                    q.set_source_rgba(*GLASS_L, 0.55)
                    q.rectangle(cx + 4, y + 10, cw - 12, fh - 22); q.fill()
                cx += cw
            # balcony slab
            q.set_source_rgb(*band)
            q.rectangle(x, y + fh - 8, w, 8); q.fill()
            q.set_source_rgba(0, 0, 0, 0.35)
            q.rectangle(x, y + fh, w, 2); q.fill()
            y += fh
        # vertical walls between loggias
        q.set_source_rgb(*body)
        for vx in range(int(x), int(x + w), 90):
            q.rectangle(vx, top, 12, base_y - top); q.fill()
        q.rectangle(x + w - 12, top, 12, base_y - top); q.fill()
        # shading: sunlit left, shaded right
        g = cairo.LinearGradient(x, 0, x + w, 0)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.18)
        g.add_color_stop_rgba(0.5, 1, 1, 1, 0)
        g.add_color_stop_rgba(0.75, *shade, 0)
        g.add_color_stop_rgba(1, *shade, 0.7)
        q.set_source(g); q.paint()
    shape(c, lambda q: rect_path(q, x, top, w, base_y - top), f)
    # roof edge
    shape(c, lambda q: rect_path(q, x - 6, top - 10, w + 12, 16), band, lw=5)
    # rooftop machine rooms
    for k in range(roof_boxes):
        bw = r.randint(50, 90); bh = r.randint(30, 60)
        bx = x + 20 + (w - 40 - bw) * (k + 0.5) / roof_boxes
        shape(c, lambda q: rect_path(q, bx, top - 10 - bh, bw, bh), lambda q, e: vgrad(q, e, body, shade), lw=5)
    # antenna
    ax = x + w * r.uniform(0.2, 0.8)
    c.set_source_rgb(*OUT); c.set_line_width(4)
    c.move_to(ax, top - 10); c.line_to(ax, top - 90)
    c.move_to(ax - 18, top - 70); c.line_to(ax + 18, top - 70)
    c.move_to(ax - 12, top - 54); c.line_to(ax + 12, top - 54); c.stroke()


BASE = 1700
highrise(2470, 760, 380, BASE, WHITE, rgb('#8E9AA6'), rgb('#FFFFFF'), 41, 3)
highrise(2930, 880, 200, BASE, rgb('#A68B74'), rgb('#5E4C3E'), rgb('#C9B39D'), 42, 1)
highrise(3110, 600, 290, BASE, CREAM, CREAM_S, rgb('#FFF6D2'), 43)
highrise(3380, 480, 230, BASE, rgb('#D8D9BC'), rgb('#8D8F6C'), rgb('#F1F1DE'), 44)
highrise(3650, 900, 150, BASE, WHITE, rgb('#8E9AA6'), rgb('#FFFFFF'), 45, 1)
highrise(3780, 740, 190, BASE, WHITE, rgb('#8E9AA6'), rgb('#FFFFFF'), 46)

# trees in front of the estate: back row (bigger, partly autumn), front row
trs = random.Random(5)
x = 2390
i = 0
while x < 3990:
    rr = trs.uniform(85, 150)
    autumn = trs.random() < 0.3
    base = AUTUMN if autumn else TREE
    light = rgb('#D9A04A') if autumn else TREE_L
    dark = rgb('#7E4A1B') if autumn else TREE_D
    foliage(c, x, right_top(x) - rr * 0.55 - trs.uniform(0, 60), rr * 1.05, rr * 0.85, base, light, dark, 100 + i)
    x += rr * trs.uniform(1.1, 1.6); i += 1
x = 2440
while x < 3960:
    rr = trs.uniform(60, 100)
    foliage(c, x, right_top(x) + 5, rr * 1.2, rr * 0.75, rgb('#4E9E30'), TREE_L, TREE_D, 300 + i)
    x += rr * trs.uniform(1.5, 2.2); i += 1

img = binarize_alpha(to_pil(s))
os.makedirs(OUTDIR, exist_ok=True)
img.save(os.path.join(OUTDIR, 'map.png'), optimize=True)
from PIL import Image
img.resize((256, 128), Image.LANCZOS).save(os.path.join(OUTDIR, 'preview.png'))
img.resize((512, 256), Image.LANCZOS).save(os.path.join(OUTDIR, 'preview@2x.png'))
print('ok', img.size)
