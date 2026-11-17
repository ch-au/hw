"""Shared cartoon drawing helpers (pycairo) for the Schlosspark theme/map."""
import math, random
import cairo
import numpy as np
from PIL import Image

OUT = (0.13, 0.09, 0.06)          # dark brown outline, Worms-ish cartoon look
LW = 6

def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

# palette
SAND = rgb('#CFA368'); SAND_L = rgb('#E9C88E'); SAND_D = rgb('#A27645'); SAND_DD = rgb('#7E5A33')
SLATE = rgb('#56647A'); SLATE_L = rgb('#7A8AA3'); SLATE_D = rgb('#3B4556')
GLASS = rgb('#1E2C44'); GLASS_L = rgb('#6A8FBF')
GRASS = rgb('#5DB83A'); GRASS_L = rgb('#93DE55'); GRASS_D = rgb('#347A1E')
EARTH = rgb('#8C5B33'); EARTH_D = rgb('#5E3B1F'); EARTH_L = rgb('#B07A48')
BASALT = rgb('#6E6158'); BASALT_D = rgb('#4C423C'); BASALT_L = rgb('#8C7E73')
WHITE = rgb('#F1F0E8'); WHITE_S = rgb('#C8CAC2'); CREAM = rgb('#F3E2A6'); CREAM_S = rgb('#CDB777')
TREE = rgb('#3F8F2C'); TREE_L = rgb('#6DBE3E'); TREE_D = rgb('#285E1C'); AUTUMN = rgb('#B9762E')
BRONZE = rgb('#4F6E55'); BRONZE_L = rgb('#7FA184')


def surface(w, h):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    c = cairo.Context(s)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    return s, c


def to_pil(s):
    w, h = s.get_width(), s.get_height()
    a = np.ndarray((h, w, 4), np.uint8, buffer=s.get_data(), strides=(s.get_stride(), 4, 1)).copy()
    # cairo is premultiplied BGRA
    b, g, r, al = [a[..., i].astype(np.float32) for i in range(4)]
    m = np.maximum(al, 1) / 255.0
    out = np.stack([np.clip(r / m, 0, 255), np.clip(g / m, 0, 255), np.clip(b / m, 0, 255), al], -1)
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def poly_path(c, pts, close=True):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    if close:
        c.close_path()


def rect_path(c, x, y, w, h):
    c.rectangle(x, y, w, h)


def arch_path(c, x, y, w, h):
    """window/door with round top: x,y = top-left of bounding box"""
    r = w / 2
    c.move_to(x, y + h)
    c.line_to(x, y + r)
    c.arc(x + r, y + r, r, math.pi, 2 * math.pi)
    c.line_to(x + w, y + h)
    c.close_path()


def shape(c, path, fill, lw=LW, outline=OUT, deco=None):
    """path: callable(c) building the path. fill: colour tuple or callable(c, extents)."""
    c.new_path()
    path(c)
    ext = c.path_extents()
    c.save()
    c.clip()
    if callable(fill):
        fill(c, ext)
    else:
        c.set_source_rgb(*fill)
        c.paint()
    if deco:
        deco(c, ext)
    c.restore()
    if lw:
        c.new_path()
        path(c)
        c.set_source_rgb(*outline)
        c.set_line_width(lw)
        c.stroke()


def vgrad(c, ext, top, bot):
    x0, y0, x1, y1 = ext
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *top)
    g.add_color_stop_rgb(1, *bot)
    c.set_source(g)
    c.paint()


def side_shade(c, ext, frac=0.22, light=True, dark=True, alpha=0.35):
    x0, y0, x1, y1 = ext
    w = x1 - x0
    if light:
        c.set_source_rgba(1, 1, 0.9, alpha * 0.7)
        c.rectangle(x0, y0, w * frac * 0.6, y1 - y0)
        c.fill()
    if dark:
        c.set_source_rgba(0.15, 0.08, 0.02, alpha)
        c.rectangle(x1 - w * frac, y0, w * frac, y1 - y0)
        c.fill()


def stone_fill(base=SAND, line=SAND_D, light=SAND_L, bh=26, bw=58, seed=1, shade=True):
    def f(c, ext):
        rnd = random.Random(seed)
        x0, y0, x1, y1 = ext
        c.set_source_rgb(*base)
        c.paint()
        # colour variation per block
        row = 0
        y = y0 - (y0 % bh)
        while y < y1:
            off = (bw / 2) * (row % 2)
            x = x0 - (x0 % bw) - off
            while x < x1:
                v = rnd.uniform(-0.06, 0.06)
                c.set_source_rgba(1 if v > 0 else 0.3, 0.9 if v > 0 else 0.2, 0.7 if v > 0 else 0.1, abs(v) * 2.2)
                c.rectangle(x, y, bw, bh)
                c.fill()
                x += bw
            y += bh
            row += 1
        c.set_source_rgba(*line, 0.75)
        c.set_line_width(2.2)
        row = 0
        y = y0 - (y0 % bh)
        while y < y1:
            c.move_to(x0, y); c.line_to(x1, y)
            off = (bw / 2) * (row % 2)
            x = x0 - (x0 % bw) - off
            while x < x1:
                c.move_to(x, y); c.line_to(x, y + bh)
                x += bw
            y += bh
            row += 1
        c.stroke()
        # light top edges on blocks
        c.set_source_rgba(*light, 0.55)
        c.set_line_width(1.6)
        y = y0 - (y0 % bh)
        while y < y1:
            c.move_to(x0, y + 2.5); c.line_to(x1, y + 2.5)
            y += bh
        c.stroke()
        if shade:
            side_shade(c, ext)
    return f


def slate_fill(base=SLATE, line=SLATE_D, light=SLATE_L, rowh=18, seed=2, shade=True):
    def f(c, ext):
        x0, y0, x1, y1 = ext
        c.set_source_rgb(*base)
        c.paint()
        c.set_source_rgba(*line, 0.8)
        c.set_line_width(2)
        y = y0 - (y0 % rowh)
        r = 0
        while y < y1:
            # scalloped shingles
            x = x0 - (x0 % 22) - 11 * (r % 2)
            while x < x1:
                c.move_to(x, y)
                c.curve_to(x, y + rowh * 0.9, x + 22, y + rowh * 0.9, x + 22, y)
                x += 22
            y += rowh
            r += 1
        c.stroke()
        if shade:
            g = cairo.LinearGradient(x0, 0, x1, 0)
            g.add_color_stop_rgba(0, *light, 0.45)
            g.add_color_stop_rgba(0.45, *light, 0.0)
            g.add_color_stop_rgba(0.6, 0, 0, 0, 0.0)
            g.add_color_stop_rgba(1, 0, 0, 0, 0.30)
            c.set_source(g)
            c.paint()
    return f


def window(c, x, y, w, h, arched=True, frame=SAND_L, cross=True, lw=4):
    fw = max(5, w * 0.16)
    pth = (lambda cc: arch_path(cc, x - fw, y - fw, w + 2 * fw, h + 2 * fw)) if arched else \
          (lambda cc: rect_path(cc, x - fw, y - fw, w + 2 * fw, h + 2 * fw))
    shape(c, pth, frame, lw=lw)
    gp = (lambda cc: arch_path(cc, x, y, w, h)) if arched else (lambda cc: rect_path(cc, x, y, w, h))

    def glass(cc, ext):
        vgrad(cc, ext, rgb('#33507A'), GLASS)
        cc.set_source_rgba(*GLASS_L, 0.75)
        cc.set_line_width(max(3, w * 0.12))
        cc.move_to(x + w * 0.15, y + h * 0.55)
        cc.line_to(x + w * 0.55, y + h * 0.15)
        cc.stroke()
        if cross:
            cc.set_source_rgb(*frame)
            cc.set_line_width(max(2.5, w * 0.09))
            cc.move_to(x + w / 2, y); cc.line_to(x + w / 2, y + h)
            cc.move_to(x, y + h * (0.45 if arched else 0.4)); cc.line_to(x + w, y + h * (0.45 if arched else 0.4))
            cc.stroke()
    shape(c, gp, glass, lw=lw * 0.8)
    # sill
    shape(c, lambda cc: rect_path(cc, x - fw * 1.5, y + h + fw * 0.6, w + fw * 3, fw * 1.1), SAND_L, lw=lw * 0.8)


def cone(c, cx, base_y, w, tip_y, col=SLATE, light=SLATE_L, dark=SLATE_D, lw=LW, flare=0.0):
    pts = [(cx - w / 2 - flare, base_y), (cx, tip_y), (cx + w / 2 + flare, base_y)]

    def f(cc, ext):
        cc.set_source_rgb(*col); cc.paint()
        cc.set_source_rgba(*light, 0.8)
        poly_path(cc, [(cx - w / 2 - flare, base_y), (cx, tip_y), (cx - w * 0.12, base_y)]); cc.fill()
        cc.set_source_rgba(*dark, 0.8)
        poly_path(cc, [(cx + w * 0.18, base_y), (cx, tip_y), (cx + w / 2 + flare, base_y)]); cc.fill()
        cc.set_source_rgba(*dark, 0.6)
        cc.set_line_width(2)
        yy = base_y - 16
        while yy > tip_y + 10:
            t = (base_y - yy) / (base_y - tip_y)
            hw = (w / 2 + flare) * (1 - t)
            cc.move_to(cx - hw, yy); cc.line_to(cx + hw, yy)
            yy -= 16
        cc.stroke()
    shape(c, lambda cc: poly_path(cc, pts), f, lw=lw)


def finial(c, x, y_base, h, ball=10):
    c.set_source_rgb(*OUT)
    c.set_line_width(5)
    c.move_to(x, y_base); c.line_to(x, y_base - h); c.stroke()
    shape(c, lambda cc: cc.arc(x, y_base - h, ball, 0, 2 * math.pi), rgb('#D9B341'), lw=4)


def blob_path(c, cx, cy, rx, ry, n=9, jitter=0.18, seed=0):
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + rnd.uniform(-jitter, jitter)
        pts.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r))
    # smooth closed curve through points (Catmull-Rom -> Bezier)
    c.move_to(*pts[0])
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        c.curve_to(*c1, *c2, *p2)
    c.close_path()


def bumpy_blob(c, cx, cy, rx, ry, bumps=11, depth=0.16, seed=0):
    """cauliflower-ish outline for tree crowns / bushes / clouds"""
    rnd = random.Random(seed)
    pts = []
    for i in range(bumps):
        a = 2 * math.pi * i / bumps + rnd.uniform(-0.1, 0.1)
        pts.append((cx + math.cos(a) * rx, cy + math.sin(a) * ry))
    c.move_to(*pts[0])
    for i in range(bumps):
        p1 = pts[i]; p2 = pts[(i + 1) % bumps]
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        dx, dy = mx - cx, my - cy
        d = math.hypot(dx, dy) or 1
        k = (depth + rnd.uniform(-0.04, 0.06)) * max(rx, ry)
        c.curve_to(p1[0] + dx / d * k, p1[1] + dy / d * k, p2[0] + dx / d * k, p2[1] + dy / d * k, *p2)
    c.close_path()


def foliage(c, cx, cy, rx, ry, base=TREE, light=TREE_L, dark=TREE_D, seed=0, lw=LW):
    def f(cc, ext):
        vgrad(cc, ext, light, base)
        rnd = random.Random(seed + 99)
        x0, y0, x1, y1 = ext
        # darker lower-right, leaf clumps
        cc.set_source_rgba(*dark, 0.55)
        bumpy_blob(cc, cx + rx * 0.35, cy + ry * 0.45, rx * 0.8, ry * 0.6, 9, 0.12, seed + 5); cc.fill()
        for _ in range(int(rx * ry / 900)):
            px = rnd.uniform(x0, x1); py = rnd.uniform(y0, y1)
            cc.set_source_rgba(*(light if py < cy else dark), 0.35)
            cc.arc(px, py, rnd.uniform(6, 14), math.pi * 0.9, math.pi * 2.1)
            cc.set_line_width(3)
            cc.stroke()
    shape(c, lambda cc: bumpy_blob(cc, cx, cy, rx, ry, max(7, int((rx + ry) / 22)), 0.16, seed), f, lw=lw)


def binarize_alpha(img, thr=110):
    a = np.array(img)
    al = a[..., 3]
    a[..., 3] = np.where(al >= thr, 255, 0).astype(np.uint8)
    a[al < thr, :3] = 0
    return Image.fromarray(a, 'RGBA')
