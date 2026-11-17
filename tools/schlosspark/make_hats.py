"""Carnival hats for hedgehogs (32x32, drawn at 8x then downsampled).
Hat sprite is drawn 5px above the hog centre; the hog faces right."""
import math, sys, os
import numpy as np
from PIL import Image
from draw import *

OUT_DIR = sys.argv[1]
os.makedirs(OUT_DIR, exist_ok=True)
S = 8
RED = rgb('#D81E1E'); BLUE = rgb('#1D6FB8'); YEL = rgb('#F7D21E'); WH = rgb('#F4F4F4')
GOLD = rgb('#E8B828'); BLACK = rgb('#1B1B1F')
LWH = 9


def finish(s, name):
    im = to_pil(s).resize((32, 32), Image.LANCZOS)
    a = np.array(im)
    a[..., 3] = np.where(a[..., 3] > 100, 255, 0)
    Image.fromarray(a).save(os.path.join(OUT_DIR, name))
    return Image.fromarray(a)


def P(*pts):
    return [(x * S, y * S) for x, y in pts]


def ball(c, x, y, r, col):
    shape(c, lambda q: q.arc(x * S, y * S, r * S, 0, 2 * math.pi), col, lw=LWH)


# ---------------------------------------------------------------- Narrenkappe (jester cap)
s, c = surface(256, 256)
c.translate(0, -1.2 * S)
# white point, curling back (left)
def white(q):
    q.move_to(*P((9, 16))[0]); q.curve_to(*P((7, 10))[0], *P((5, 7))[0], *P((3.2, 5.2))[0])
    q.curve_to(*P((9, 5))[0], *P((14, 8))[0], *P((17, 14))[0]); q.close_path()
shape(c, white, WH, lw=LWH)
# blue point, tall in the middle
def blue(q):
    q.move_to(*P((14, 14))[0]); q.curve_to(*P((14, 9))[0], *P((13, 6))[0], *P((12, 3.0))[0])
    q.curve_to(*P((19, 4))[0], *P((23, 9))[0], *P((23, 16))[0]); q.close_path()
shape(c, blue, BLUE, lw=LWH)
# yellow point, curling forward (right, over the face)
def yellow(q):
    q.move_to(*P((18, 16.5))[0]); q.curve_to(*P((21, 11))[0], *P((26, 11))[0], *P((29.5, 16.5))[0])
    q.curve_to(*P((27, 15.5))[0], *P((25, 17))[0], *P((24.5, 20))[0]); q.close_path()
shape(c, yellow, YEL, lw=LWH)
c.translate(0, 0)
ball(c, 3.4, 5.4, 2.1, WH)
ball(c, 12, 3.6, 2.0, BLUE)
ball(c, 29.3, 16.8, 2.0, YEL)
# red brim band, curved
def brim(q):
    q.move_to(*P((5, 14))[0]); q.curve_to(*P((12, 15))[0], *P((19, 16))[0], *P((25, 20))[0])
    q.line_to(*P((23.8, 21.6))[0])
    q.curve_to(*P((18, 19.5))[0], *P((11, 18.5))[0], *P((5.5, 17.2))[0]); q.close_path()
shape(c, brim, RED, lw=LWH)
c.set_source_rgba(1, 1, 1, 0.45); c.set_line_width(10)
c.move_to(*P((7, 15.3))[0]); c.curve_to(*P((12, 16))[0], *P((18, 17))[0], *P((22, 19.5))[0]); c.stroke()
finish(s, 'Narrenkappe.png')


# ---------------------------------------------------------------- Garde-Dreispitz (carnival guard tricorn)
def tricorn(c):
    c.save(); c.translate(0, -3.0 * S)
    # white feather plume behind
    def plume(q):
        q.move_to(*P((9, 9))[0]); q.curve_to(*P((6, 6))[0], *P((9, 3.4))[0], *P((14, 3.6))[0])
        q.curve_to(*P((12, 5))[0], *P((12, 7))[0], *P((13, 9))[0]); q.close_path()
    shape(c, plume, WH, lw=LWH)
    # crown of the hat
    shape(c, lambda q: poly_path(q, P((8, 13), (10, 7.5), (21, 7.5), (23, 13))), BLACK, lw=LWH)
    # turned-up brim (tricorn: side wings)
    def brimp(q):
        q.move_to(*P((3, 9.5))[0]); q.curve_to(*P((6, 13))[0], *P((10, 11.5))[0], *P((15.5, 10.5))[0])
        q.curve_to(*P((21, 11.5))[0], *P((25, 13))[0], *P((29, 9.5))[0])
        q.curve_to(*P((28, 15))[0], *P((25, 17.5))[0], *P((15.5, 17.5))[0])
        q.curve_to(*P((7, 17.5))[0], *P((4, 15))[0], *P((3, 9.5))[0]); q.close_path()
    shape(c, brimp, RED, lw=LWH)
    # white trim along the brim edge
    c.set_source_rgb(*WH); c.set_line_width(14)
    c.move_to(*P((3.6, 10.5))[0]); c.curve_to(*P((6, 13.4))[0], *P((10, 12))[0], *P((15.5, 11.2))[0])
    c.curve_to(*P((21, 12))[0], *P((25, 13.4))[0], *P((28.4, 10.5))[0]); c.stroke()
    # gold cockade
    shape(c, lambda q: q.arc(15.5 * S, 13.6 * S, 2.4 * S, 0, 2 * math.pi), GOLD, lw=LWH)
    shape(c, lambda q: q.arc(15.5 * S, 13.6 * S, 1.0 * S, 0, 2 * math.pi), RED, lw=6)
    c.restore()


s, c = surface(256, 256)
tricorn(c)
finish(s, 'GardeDreispitz.png')

# ---------------------------------------------------------------- Gardeuniform: tricorn + jacket front
s, c = surface(256, 256)
# jacket: red front panel with white crossbelts and gold buttons, hog y 15..26 => hat y 20..31
def jacket(q):
    q.move_to(*P((9.5, 23.5))[0]); q.curve_to(*P((13, 22.5))[0], *P((20, 22.5))[0], *P((23.5, 23.5))[0])
    q.curve_to(*P((25, 26.5))[0], *P((24.5, 29.5))[0], *P((22.5, 31))[0])
    q.line_to(*P((10.5, 31))[0])
    q.curve_to(*P((8.5, 29.5))[0], *P((8, 26.5))[0], *P((9.5, 23.5))[0]); q.close_path()
shape(c, jacket, RED, lw=LWH)
c.save(); c.new_path(); jacket(c); c.clip()
c.set_source_rgb(*WH); c.set_line_width(1.8 * S)
c.move_to(*P((9, 23))[0]); c.line_to(*P((24, 32))[0])
c.move_to(*P((24, 23))[0]); c.line_to(*P((9, 32))[0]); c.stroke()
c.restore()
# epaulettes (gold) and buttons
for ex in (9.5, 23.5):
    shape(c, lambda q: blob_path(q, ex * S, 23.6 * S, 2.2 * S, 1.3 * S, 8, 0.0), GOLD, lw=6)
for by in (25.3, 29.3):
    shape(c, lambda q: q.arc(16.5 * S, by * S, 0.9 * S, 0, 2 * math.pi), GOLD, lw=6)
tricorn(c)
finish(s, 'Gardeuniform.png')

# ---------------------------------------------------------------- preview sheet
HOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../share/hedgewars/Data/Graphics/Hedgehog.png')
hog = Image.open(HOG).convert('RGBA').crop((0, 0, 32, 32))
sheet = Image.new('RGBA', (3 * 2 * 40, 44), (150, 195, 240, 255))
for i, n in enumerate(['Narrenkappe', 'GardeDreispitz', 'Gardeuniform']):
    hat = Image.open(os.path.join(OUT_DIR, n + '.png'))
    for j, flip in enumerate((False, True)):
        cell = Image.new('RGBA', (40, 44))
        h = hog.transpose(Image.FLIP_LEFT_RIGHT) if flip else hog
        ht = hat.transpose(Image.FLIP_LEFT_RIGHT) if flip else hat
        cell.alpha_composite(h, (4, 10))
        cell.alpha_composite(ht, (4, 5))
        sheet.alpha_composite(cell, ((i * 2 + j) * 40, 0))
sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save(sys.argv[2])
print('hats ok')
