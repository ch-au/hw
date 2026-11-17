"""Photo-faithful variant: two maps (Schloss, Hochhaus) cut out of the reference photos,
plus a theme (Schlosspark) whose sky/hills come from the high-rise photo."""
import os
PHOTO_DIR = os.environ.get('PHOTO_DIR', '.')  # folder with the two reference photos
import sys, os, math, random
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
from scipy import ndimage as ndi

OUT = sys.argv[1]
os.makedirs(OUT + '/Schloss', exist_ok=True); os.makedirs(OUT + '/Hochhaus', exist_ok=True); os.makedirs(OUT + '/theme', exist_ok=True)
H = 2048
rng = np.random.default_rng(3)


def noise(h, w, scale, seed):
    r = np.random.default_rng(seed)
    small = r.random((h // scale + 2, w // scale + 2)).astype(np.float32)
    return np.array(Image.fromarray((small * 255).astype(np.uint8)).resize((w + scale * 2, h + scale * 2), Image.BICUBIC))[:h, :w] / 255.0


def soil(w, h, seed):
    """realistic earth body texture"""
    n1 = noise(h, w, 40, seed); n2 = noise(h, w, 8, seed + 1); n3 = noise(h, w, 3, seed + 2)
    t = 0.5 * n1 + 0.3 * n2 + 0.2 * n3
    y = np.linspace(0, 1, h)[:, None]
    base = np.array([112, 78, 48], np.float32); dark = np.array([62, 42, 26], np.float32)
    col = base[None, None] * (1 - y[..., None] * 0.6) + dark[None, None] * (y[..., None] * 0.6)
    col = col * (0.75 + 0.5 * t[..., None])
    # pebbles
    peb = (n3 > 0.82) & (n2 > 0.55)
    col[peb] = col[peb] * 0.5 + np.array([150, 138, 124]) * 0.5
    return np.clip(col, 0, 255).astype(np.uint8)


def ragged_body(w, top_y, x0, x1, bx0, bx1, seed):
    """mask of a land body under a photo: from top_y down to H, tapering from [x0,x1] to [bx0,bx1]"""
    m = np.zeros((H, w), bool)
    n = noise(H, 1, 30, seed)[:, 0]
    n2 = noise(H, 1, 30, seed + 7)[:, 0]
    for y in range(top_y, H):
        t = (y - top_y) / max(1, H - top_y)
        l = int(x0 + (bx0 - x0) * t ** 1.4 + (n[y] - 0.5) * 60 * t)
        r = int(x1 + (bx1 - x1) * t ** 1.4 + (n2[y] - 0.5) * 60 * t)
        m[y, max(0, l):min(w, r)] = True
    return m


def compose(w, photo_rgba, px, py, body_top, bx, seed, name, ragged_sides=False):
    canvas = np.zeros((H, w, 4), np.uint8)
    pw, ph = photo_rgba.size
    # earth body (drawn first, photo goes on top)
    x0, x1 = px + 20, px + pw - 20
    body = ragged_body(w, body_top, x0, x1, x0 + bx, x1 - bx, seed)
    s = soil(w, H, seed)
    canvas[body, :3] = s[body]; canvas[body, 3] = 255
    # grass/turf fringe at the top of the body where it sticks out from under the photo
    img = Image.fromarray(canvas, 'RGBA')
    img.alpha_composite(photo_rgba, (px, py))
    a = np.array(img)
    a[..., 3] = np.where(a[..., 3] > 127, 255, 0).astype(np.uint8)
    a[a[..., 3] == 0, :3] = 0
    out = Image.fromarray(a, 'RGBA')
    out.save(f'{OUT}/{name}/map.png', optimize=True)
    out.resize((256, 128), Image.LANCZOS).save(f'{OUT}/{name}/preview.png')
    out.resize((512, 256), Image.LANCZOS).save(f'{OUT}/{name}/preview@2x.png')
    return out


# ---------------------------------------------------------------- map 1: Schloss
castle = Image.open('out/castle_cut.png')          # 3544x2430 with alpha
bb = castle.getbbox()
castle = castle.crop(bb)
S1 = 0.72
castle = castle.resize((int(castle.width * S1), int(castle.height * S1)), Image.LANCZOS)
castle = castle.filter(ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=2))
ca = np.array(castle); ch, cw = ca.shape[:2]
en = 0.6 * noise(ch, 1, 40, 31)[:, 0] + 0.4 * noise(ch, 1, 7, 32)[:, 0]
en2 = 0.6 * noise(ch, 1, 40, 33)[:, 0] + 0.4 * noise(ch, 1, 7, 34)[:, 0]
y0 = int(ch * 0.755)
for y in range(y0, ch):
    t = (y - y0) / (ch - y0)
    l = int(cw * 0.155 * (1 - t) ** 1.3 + (en[y] - 0.5) * 50)
    r = int(cw * 0.05 * (1 - t) ** 1.3 + (en2[y] - 0.5) * 40)
    ca[y, :max(0, l), 3] = 0
    if r > 0:
        ca[y, cw - r:, 3] = 0
castle = Image.fromarray(ca, 'RGBA')
W1 = castle.width + 300
py = H - castle.height - 230
compose(W1, castle, 150, py, py + castle.height - 40, 260, 11, 'Schloss')
print('Schloss', W1, castle.size, py)

# ---------------------------------------------------------------- map 2: Hochhaus
tw = Image.open('out/towers_cut.png').crop((110, 400, 1360, 1000))
S2 = 2.6
tw = tw.resize((int(tw.width * S2), int(tw.height * S2)), Image.LANCZOS)
tw = tw.filter(ImageFilter.UnsharpMask(radius=2.5, percent=90, threshold=2))
# ragged left/right edges of the forest so it doesn't end in a straight cut
a = np.array(tw)
hh, ww = a.shape[:2]
def edge_noise(seed):
    return 0.5 * noise(hh, 1, 90, seed)[:, 0] + 0.3 * noise(hh, 1, 23, seed + 1)[:, 0] + 0.2 * noise(hh, 1, 6, seed + 2)[:, 0]
nl = edge_noise(5); nr = edge_noise(8)
tree_top = int((585 - 400) * S2)
for y in range(tree_top, hh):
    t = (y - tree_top) / (hh - tree_top)
    cutl = int(nl[y] * 140 + t * 160)
    cutr = int(nr[y] * 140 + t * 160)
    a[y, :cutl, 3] = 0
    a[y, ww - cutr:, 3] = 0
tw = Image.fromarray(a, 'RGBA')
W2 = tw.width + 200
py2 = H - tw.height - 60
compose(W2, tw, 100, py2, H, 280, 21, 'Hochhaus')
print('Hochhaus', W2, tw.size, py2)

# ---------------------------------------------------------------- theme from photo 2
T = OUT + '/theme'
p2 = np.array(Image.open(PHOTO_DIR + '/hochhaus.png')).astype(np.float32)
# sky gradient: average colour of rows 0..265
col = p2[:265].mean(axis=1)                         # (265,3)
grad = np.array(Image.fromarray(col[:, None, :].astype(np.uint8)).resize((1, 512), Image.BICUBIC))
sky = np.repeat(grad, 1024, axis=1)
Image.fromarray(sky).convert('RGBA').save(T + '/Sky.png')
skytop = tuple(int(v) for v in col[0])
print('skytop', skytop)
# hills strip: rows 255..412 (above the buildings), sky made transparent
strip = p2[255:413].copy()
lum = strip.mean(-1)
skyref = p2[255:413].copy()
# hill pixels are clearly darker than the sky right above the ridge
rowsky = np.array([np.percentile(lum[:, i], 95) for i in range(strip.shape[1])])
hillmask = lum < (rowsky[None] - 12)
ridge = np.argmax(hillmask, axis=0).astype(np.float32)
ridge[~hillmask.any(0)] = strip.shape[0] - 1
ridge = ndi.median_filter(ridge, size=9)
rows = np.arange(strip.shape[0])[:, None]
alpha = np.clip((rows - ridge[None]) / 2.0 + 0.5, 0, 1)
ext_rows = 220
last = ndi.gaussian_filter1d(strip[-10:].mean(axis=0), 6, axis=0)   # (1500,3)
fade = np.linspace(1.0, 0.82, ext_rows)[:, None, None]
tn = noise(ext_rows, strip.shape[1], 3, 9)[..., None]
ext = last[None] * fade * (0.97 + 0.06 * tn)
rgb_all = np.concatenate([strip, ext], 0)
a_all = np.concatenate([alpha, np.ones((ext_rows, strip.shape[1]))], 0)
hz = np.dstack([np.clip(rgb_all, 0, 255), a_all * 255]).astype(np.uint8)
hz = Image.fromarray(hz, 'RGBA')
hz = hz.resize((int(hz.width * 1.35), int(hz.height * 1.35)), Image.LANCZOS)
# make it tileable: original + mirrored
tile = Image.new('RGBA', (hz.width * 2, hz.height))
tile.paste(hz, (0, 0)); tile.paste(hz.transpose(Image.FLIP_LEFT_RIGHT), (hz.width, 0))
tile.save(T + '/horizont.png', optimize=True)
print('horizont', tile.size)
# soft clouds, 4 frames 256x128
cl = Image.new('RGBA', (256, 512))
for i in range(4):
    fr = Image.new('L', (256, 128))
    d = ImageDraw.Draw(fr)
    r = random.Random(i)
    for _ in range(14):
        cx = r.uniform(50, 206); cy = r.uniform(55, 85); rr = r.uniform(18, 38)
        d.ellipse((cx - rr * 1.3, cy - rr, cx + rr * 1.3, cy + rr * 0.8), fill=255)
    fr = fr.filter(ImageFilter.GaussianBlur(7))
    shade = np.linspace(255, 215, 128)[:, None].repeat(256, 1)
    rgb = np.dstack([shade, shade + 5, np.full_like(shade, 255)]).clip(0, 255)
    frame = np.dstack([rgb, np.array(fr) * 0.85]).astype(np.uint8)
    cl.paste(Image.fromarray(frame, 'RGBA'), (0, i * 128))
cl.save(T + '/Clouds.png')
# sandstone land texture from the tower wall in photo 1
p1 = Image.open(PHOTO_DIR + '/schloss.png')
K = p1.width / 2000
patch = p1.crop((int(532 * K), int(432 * K), int(592 * K), int(472 * K)))
patch = patch.resize((160, 120), Image.LANCZOS)
quad = Image.new('RGB', (320, 240))
quad.paste(patch, (0, 0)); quad.paste(patch.transpose(Image.FLIP_LEFT_RIGHT), (160, 0))
quad.paste(patch.transpose(Image.FLIP_TOP_BOTTOM), (0, 120)); quad.paste(patch.transpose(Image.ROTATE_180), (160, 120))
lt = Image.new('RGB', (640, 480))
for x in (0, 320):
    for y in (0, 240):
        lt.paste(quad, (x, y))
lt.convert('RGBA').save(T + '/LandTex.png')
ImageEnhance.Brightness(lt).enhance(0.6).convert('RGBA').save(T + '/LandBackTex.png')
# border: rows 0-15 turf on top, 16-31 darker stone underside, no cartoon outline
bd = np.zeros((32, 128, 3), np.float32)
nn = noise(32, 128, 4, 12)
for y in range(16):
    g = np.array([88, 128, 52]) if y < 9 else np.array([110, 90, 60])
    bd[y] = g * (0.8 + 0.4 * nn[y][:, None])
lt_a = np.array(lt).astype(np.float32)
bd[16:] = lt_a[:16, :128] * np.linspace(1, 0.55, 16)[:, None, None]
Image.fromarray(np.dstack([bd.clip(0, 255), np.full((32, 128), 255)]).astype(np.uint8), 'RGBA').save(T + '/Border.png')
open(T + '/skytop.txt', 'w').write('%d, %d, %d' % skytop)
print('theme ok')
# icon: tower crown from the castle cut-out
cc = Image.open('out/castle_cut.png')
Kc = cc.width / 2000
crop = cc.crop((int(380 * Kc), int(20 * Kc), int(840 * Kc), int(480 * Kc)))
for size, name in ((32, 'icon.png'), (64, 'icon@2x.png')):
    ic = Image.new('RGBA', (size + 1, size), skytop + (255,))
    ic.alpha_composite(crop.resize((size, size), Image.LANCZOS), (0, 0))
    m = Image.new('L', (size + 1, size), 0); ImageDraw.Draw(m).ellipse((0, 0, size, size - 1), fill=255)
    ic.putalpha(m)
    ic.save(T + '/' + name)
