"""Generates Data/Themes/Schlosspark: sky, horizon (wooded hills + distant town / high-rises),
clouds, sandstone land textures, grass border, falling leaves, icons."""
import math, random, sys, os
import cairo
import numpy as np
from PIL import Image
from draw import *

OUT_DIR = sys.argv[1]
os.makedirs(OUT_DIR, exist_ok=True)
SKY_TOP = rgb('#3F7FD6')
SKY_BOT = rgb('#B7D3F0')


def save(s, name, binar=False):
    im = to_pil(s)
    im.save(os.path.join(OUT_DIR, name), optimize=True)
    return im


# ---------------------------------------------------------------- Sky (tileable horizontally)
s, c = surface(1024, 512)
g = cairo.LinearGradient(0, 0, 0, 512)
g.add_color_stop_rgb(0, *SKY_TOP)
g.add_color_stop_rgb(0.65, *rgb('#78A9E6'))
g.add_color_stop_rgb(1, *SKY_BOT)
c.set_source(g); c.paint()
# faint far cloud streaks, drawn wrapped
r = random.Random(3)
for _ in range(9):
    cx, cy = r.uniform(0, 1024), r.uniform(180, 420)
    rx, ry = r.uniform(80, 180), r.uniform(12, 26)
    for dx in (-1024, 0, 1024):
        c.set_source_rgba(1, 1, 1, 0.22)
        bumpy_blob(c, cx + dx, cy, rx, ry, 9, 0.2, int(cx)); c.fill()
save(s, 'Sky.png')

# ---------------------------------------------------------------- Horizon
HH = 640
PER = 1024


def ridge(x, amp, base, phase, k=(1, 2, 5)):
    w = 2 * math.pi / PER
    return base - amp * (0.55 * math.sin(w * k[0] * x + phase) + 0.3 * math.sin(w * k[1] * x + phase * 2.3)
                         + 0.15 * math.sin(w * k[2] * x + phase * 0.7))


def tree_edge(c, width, yfun, col, seed, bump=9, step=18):
    """ridge silhouette with little tree-crown bumps along the top"""
    rr = random.Random(seed)
    c.move_to(0, HH + 5)
    c.line_to(0, yfun(0))
    x = 0
    while x < width:
        nx = min(width, x + step)
        y0, y1 = yfun(x), yfun(nx)
        h = bump * (0.6 + 0.8 * ((int(x / step) * 7919 + seed) % 10) / 10)
        c.curve_to(x, y0 - h, nx, y1 - h, nx, y1)
        x = nx
    c.line_to(width, HH + 5)
    c.close_path()


def horizon(width, skyline):
    s, c = surface(width, HH)
    # far ridge (hazy)
    far = lambda x: ridge(x, 60, 300, 0.4)
    tree_edge(c, width, far, None, 1, 6, 14)
    g = cairo.LinearGradient(0, 220, 0, HH)
    g.add_color_stop_rgb(0, *rgb('#6E93B9')); g.add_color_stop_rgb(1, *rgb('#8DB0D0'))
    c.set_source(g); c.fill_preserve()
    c.set_source_rgba(*rgb('#4E6F93'), 0.9); c.set_line_width(3); c.stroke()
    # near ridge, darker blue-green forest (Taunus-like)
    near = lambda x: ridge(x, 45, 400, 2.1, (1, 3, 7))
    tree_edge(c, width, near, None, 2, 12, 20)
    g = cairo.LinearGradient(0, 330, 0, HH)
    g.add_color_stop_rgb(0, *rgb('#4F7F78')); g.add_color_stop_rgb(1, *rgb('#6C9A96'))
    c.set_source(g); c.fill_preserve()
    c.set_source_rgba(*rgb('#2E5552'), 1); c.set_line_width(3.5); c.stroke()
    # light streak of a forest track
    c.set_source_rgba(1, 1, 1, 0.12); c.set_line_width(6)
    for x in range(0, width, PER):
        c.move_to(x + 200, near(x + 200) + 40); c.curve_to(x + 350, near(x + 350) + 30, x + 500, near(x + 500) + 60, x + 700, near(x + 700) + 55); c.stroke()
    # town strip at the foot of the hills
    rr = random.Random(11)
    town_y = 540
    x = 0
    houses = []
    while x < width:
        w = rr.randint(14, 30); h = rr.randint(10, 26)
        houses.append((x, w, h, rr.random()))
        x += w + rr.randint(-2, 6)
    # repeat pattern every PER for seamless tiling
    houses = [hh for hh in houses if hh[0] < PER]
    for rep in range(0, width, PER):
        for (hx, w, h, t) in houses:
            X = hx + rep
            col = rgb('#C9D3D9') if t < 0.6 else rgb('#B48C7A')
            c.rectangle(X, town_y - h, w, h)
            c.set_source_rgb(*col); c.fill_preserve()
            c.set_source_rgba(*rgb('#5B6E7E'), 0.8); c.set_line_width(1.5); c.stroke()
            if t > 0.6:
                poly_path(c, [(X - 2, town_y - h), (X + w / 2, town_y - h - 9), (X + w + 2, town_y - h)])
                c.set_source_rgb(*rgb('#9A5A4C')); c.fill()
    if skyline:
        # distant hazy high-rises + a small church spire, centre only
        for (bx, bw, bh) in [(760, 70, 150), (840, 55, 120), (905, 90, 175), (1010, 60, 130), (1150, 80, 160), (1240, 50, 110)]:
            c.rectangle(bx, town_y - bh, bw, bh)
            c.set_source_rgb(*rgb('#D7DEE3')); c.fill_preserve()
            c.set_source_rgba(*rgb('#6F8496'), 0.9); c.set_line_width(2); c.stroke()
            c.set_source_rgba(*rgb('#8FA2B3'), 0.8); c.set_line_width(1.5)
            for yy in range(int(town_y - bh + 10), town_y - 4, 10):
                c.move_to(bx + 5, yy); c.line_to(bx + bw - 5, yy)
            c.stroke()
        poly_path(c, [(560, town_y), (560, town_y - 60), (568, town_y - 100), (576, town_y - 60), (576, town_y)])
        c.set_source_rgb(*rgb('#B79D7E')); c.fill()
    # foreground: dark band of treetops (park in front)
    fg = lambda x: ridge(x, 14, 585, 4.0, (2, 5, 11))
    tree_edge(c, width, fg, None, 3, 16, 26)
    g = cairo.LinearGradient(0, 540, 0, HH)
    g.add_color_stop_rgb(0, *rgb('#3E7A3A')); g.add_color_stop_rgb(1, *rgb('#2D5E2B'))
    c.set_source(g); c.fill_preserve()
    c.set_source_rgb(*rgb('#1E3E1C')); c.set_line_width(4); c.stroke()
    return s


save(horizon(2048, True), 'horizont.png')
hl = horizon(1024, False)
save(hl, 'horizontL.png')
save(hl, 'horizontR.png')

# ---------------------------------------------------------------- Clouds: 4 frames 256x128
s, c = surface(256, 512)
for i in range(4):
    cy = i * 128 + 66
    r = random.Random(20 + i)
    def p(q, i=i, cy=cy):
        bumpy_blob(q, 128, cy, 100 - i * 8, 38 - i * 2, 10, 0.32, 40 + i)
    def f(q, e, cy=cy):
        vgrad(q, e, (1, 1, 1), rgb('#D5E2F0'))
        q.set_source_rgba(*rgb('#A9BCD3'), 0.6)
        q.rectangle(0, cy + 14, 256, 60); q.fill()
    shape(c, p, f, lw=4, outline=rgb('#5C7090'))
save(s, 'Clouds.png')

# ---------------------------------------------------------------- Land textures (tileable 640x480)
def landtex(base, line, light, name, darken=0.0):
    s, c = surface(640, 480)
    c.rectangle(0, 0, 640, 480)
    c.save(); c.clip()
    stone_fill(base, line, light, bh=30, bw=64, seed=9, shade=False)(c, (0, 0, 640, 480))
    c.restore()
    if darken:
        c.set_source_rgba(0.1, 0.05, 0.0, darken); c.paint()
    save(s, name)


landtex(SAND, SAND_D, SAND_L, 'LandTex.png')
landtex(SAND_D, SAND_DD, SAND, 'LandBackTex.png', 0.25)

# ---------------------------------------------------------------- Border 128x32 (rows 0-15 top/grass, 16-31 underside)
s, c = surface(128, 32)
c.set_source_rgb(*SAND); c.paint()
c.rectangle(0, 0, 128, 16); c.set_source_rgb(*GRASS); c.fill()
c.rectangle(0, 0, 128, 4); c.set_source_rgb(*GRASS_L); c.fill()
c.rectangle(0, 0, 128, 2); c.set_source_rgb(*rgb('#1F4A12')); c.fill()
for x in range(0, 128, 8):   # drips into the stone, period divides 128
    c.move_to(x, 11); c.curve_to(x + 1, 16, x + 7, 16, x + 8, 11)
c.line_to(128, 11); c.line_to(128, 9); c.line_to(0, 9); c.close_path()
c.set_source_rgb(*GRASS); c.fill()
c.rectangle(0, 14, 128, 2); c.set_source_rgba(*GRASS_D, 0.0); c.fill()
c.rectangle(0, 16, 128, 16); c.set_source_rgb(*SAND); c.fill()
c.rectangle(0, 26, 128, 6); c.set_source_rgb(*SAND_D); c.fill()
c.rectangle(0, 30, 128, 2); c.set_source_rgb(*OUT); c.fill()
im = to_pil(s)
a = np.array(im); a[..., 3] = 255
Image.fromarray(a).save(os.path.join(OUT_DIR, 'Border.png'))

# ---------------------------------------------------------------- Flake: falling leaves, 4 frames 64x64
s, c = surface(64, 256)
cols = [rgb('#D98B2B'), rgb('#B9541F'), rgb('#E7C43C'), rgb('#7FAE3A')]
for i in range(4):
    cx, cy = 32, i * 64 + 32
    c.save(); c.translate(cx, cy); c.rotate(i * 0.9)
    def leaf(q):
        q.move_to(-14, 0); q.curve_to(-6, -12, 8, -12, 15, 0); q.curve_to(8, 12, -6, 12, -14, 0); q.close_path()
    shape(c, leaf, cols[i], lw=2.5)
    c.set_source_rgb(*OUT); c.set_line_width(1.5); c.move_to(-17, 0); c.line_to(12, 0); c.stroke()
    c.restore()
save(s, 'Flake.png')

# ---------------------------------------------------------------- icons: mini castle tower + high-rise
def icon(size, name):
    s, c = surface(size + 1, size)
    k = size / 32
    c.scale(k, k)
    shape(c, lambda q: q.arc(16.5, 16, 15.5, 0, 2 * math.pi), lambda q, e: vgrad(q, e, SKY_TOP, SKY_BOT), lw=1.2)
    c.save(); c.arc(16.5, 16, 15, 0, 2 * math.pi); c.clip()
    shape(c, lambda q: q.rectangle(19, 11, 8, 22), WHITE, lw=1)
    for yy in range(13, 30, 3):
        c.set_source_rgb(*GLASS); c.rectangle(20, yy, 6, 1.2); c.fill()
    shape(c, lambda q: q.rectangle(8, 10, 8, 23), SAND, lw=1)
    shape(c, lambda q: poly_path(q, [(6.5, 10.5), (12, 2), (17.5, 10.5)]), SLATE, lw=1)
    c.set_source_rgb(*GLASS); c.rectangle(10.5, 14, 3, 4); c.fill(); c.rectangle(10.5, 21, 3, 4); c.fill()
    shape(c, lambda q: q.rectangle(0, 28, 33, 6), GRASS, lw=1)
    c.restore()
    save(s, name)


icon(32, 'icon.png')
icon(64, 'icon@2x.png')
print('theme ok')
