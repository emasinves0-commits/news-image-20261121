"""make.fun news poster, Saturday 21 November 2026: "Saturday Atlas" (1024x1024).

Evolved broadsheet: pure white page, ink-black grotesque sans, signal-red accents, thin rules.
New for today: a left-hand "THE DAY SO FAR" timeline rail, a big-lead + stacked-leads top block,
a region scoreboard, a wide map beside the red DATE CHECK box, briefs in four balanced columns.
Pure PIL, no external images, no network, no randomness, no timestamps.
Usage: python3 draw.py [output_dir]   (default: directory of this file) -> <output_dir>/entry.png
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
FL = "/usr/share/fonts/truetype/liberation/"
SANS_B = FL + "LiberationSans-Bold.ttf"
SANS = FL + "LiberationSans-Regular.ttf"
if not os.path.exists(SANS_B):
    SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PAPER = (255, 255, 255)
INK = (10, 10, 10)
RED = (217, 35, 15)
GREY = (52, 52, 52)
RULE = (10, 10, 10)
SEA = (226, 232, 240)
LAND = (196, 200, 208)

_fc = {}


def F(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


def wrap(text, font, maxw):
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def fit_block(text, path, maxw, maxlines, start, minsize, lead=1.28):
    """Largest size whose wrapped text fits maxw within maxlines. Returns (font, lines, lineheight)."""
    for s in range(start, minsize - 1, -1):
        f = F(path, s)
        lines = wrap(text, f, maxw)
        if len(lines) <= maxlines and all(f.getlength(l) <= maxw for l in lines):
            return f, lines, int(s * lead)
    raise ValueError("text does not fit: " + text)


def fit_line(text, path, maxw, start, minsize=8):
    for s in range(start, minsize - 1, -1):
        if F(path, s).getlength(text) <= maxw:
            return F(path, s)
    raise ValueError("line does not fit: " + text)


def ctext(d, cx, y, text, font, fill):
    d.text((cx - font.getlength(text) / 2, y), text, font=font, fill=fill)


# ---------- supersampled vector helper ----------
K = 4


class SD:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.im = Image.new("RGB", (int(w * K), int(h * K)), bg)
        self.d = ImageDraw.Draw(self.im)

    def _p(self, pts):
        return [(x * K, y * K) for x, y in pts]

    def poly(self, pts, fill=None, outline=None, width=1):
        self.d.polygon(self._p(pts), fill=fill, outline=outline, width=int(width * K))

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.rectangle([x0 * K, y0 * K, x1 * K, y1 * K], fill=fill, outline=outline, width=int(width * K))

    def ell(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.ellipse([x0 * K, y0 * K, x1 * K, y1 * K], fill=fill, outline=outline, width=int(width * K))

    def line(self, pts, fill, width=1):
        self.d.line(self._p(pts), fill=fill, width=max(1, int(width * K)), joint="curve")

    def pie(self, box, a0, a1, fill):
        self.d.pieslice([v * K for v in box], a0, a1, fill=fill)

    def out(self):
        return self.im.resize((int(self.w), int(self.h)), Image.LANCZOS)


def vgrad(s, y0, y1, c0, c1, x0=0, x1=None):
    x1 = s.w if x1 is None else x1
    n = int((y1 - y0) * 2)
    for i in range(n):
        t = i / max(1, n - 1)
        c = tuple(int(c0[j] + (c1[j] - c0[j]) * t) for j in range(3))
        s.rect(x0, y0 + i / 2, x1, y0 + (i + 1) / 2 + 0.2, fill=c)


def star(cx, cy, r, rot=-90):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.4
        a = math.radians(rot + i * 36)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def lit_windows(s, bx, top, bw, bot, seed, col=(240, 190, 90)):
    for wy in range(int(top + 5), int(bot - 4), 8):
        for wx in range(int(bx + 3), int(bx + bw - 4), 6):
            if (wx * 3 + wy * seed) % 5 < 2:
                s.rect(wx, wy, wx + 2.4, wy + 3.4, fill=col)


def person(s, x, yb, ph, col, skin=(226, 192, 162)):
    s.ell(x - ph * 0.17, yb - ph, x + ph * 0.17, yb - ph * 0.66, fill=skin)
    s.rect(x - ph * 0.22, yb - ph * 0.66, x + ph * 0.22, yb, fill=col)


def eu_flag(s, x, y, w, h):
    s.rect(x, y, x + w, y + h, fill=(0, 51, 153))
    for i in range(12):
        a = math.radians(i * 30)
        s.poly(star(x + w / 2 + h * 0.34 * math.cos(a), y + h / 2 + h * 0.34 * math.sin(a), max(1.6, h * 0.07)), fill=(255, 204, 0))


def uk_flag(s, x, y, w, h):
    s.rect(x, y, x + w, y + h, fill=(1, 33, 105))
    for wd, col in ((h * 0.19, (255, 255, 255)), (h * 0.09, (200, 16, 46))):
        s.line([(x, y), (x + w, y + h)], col, wd)
        s.line([(x + w, y), (x, y + h)], col, wd)
    s.rect(x, y + h / 2 - h * 0.16, x + w, y + h / 2 + h * 0.16, fill=(255, 255, 255))
    s.rect(x + w / 2 - h * 0.16, y, x + w / 2 + h * 0.16, y + h, fill=(255, 255, 255))
    s.rect(x, y + h / 2 - h * 0.09, x + w, y + h / 2 + h * 0.09, fill=(200, 16, 46))
    s.rect(x + w / 2 - h * 0.09, y, x + w / 2 + h * 0.09, y + h, fill=(200, 16, 46))


def pole_flag(s, x, ytop, ybot, fw, fh, stripes, vertical=False):
    s.line([(x, ytop - 2), (x, ybot)], (70, 70, 76), 1.4)
    n = len(stripes)
    for i, c in enumerate(stripes):
        if vertical:
            s.rect(x + i * fw / n, ytop, x + (i + 1) * fw / n, ytop + fh, fill=c)
        else:
            s.rect(x, ytop + i * fh / n, x + fw, ytop + (i + 1) * fh / n, fill=c)


# ---------- richer helpers for the mini-scenes ----------
_RAD = Image.radial_gradient("L")


def glow(s, cx, cy, r, col, a=0.8):
    n = max(2, int(2 * r * K))
    m = _RAD.resize((n, n), Image.BILINEAR).point(lambda v: int(a * max(0, 255 - v)))
    s.im.paste(Image.new("RGB", (n, n), col), (int((cx - r) * K), int((cy - r) * K)), m)


def cloud(s, x, y, sc, col=(255, 255, 255)):
    for dx, dy, r in ((0, 0, 5), (6, -3, 6), (13, -1, 5), (19, 1, 4), (7, 2, 5)):
        s.ell(x + dx * sc - r * sc, y + dy * sc - r * sc * 0.6, x + dx * sc + r * sc, y + dy * sc + r * sc * 0.6, fill=col)


def ridge(s, base, amp, x0, x1, bot, col, ph=0.0, f1=0.045, f2=0.11, step=3):
    pts = [(x0, bot)]
    x = x0
    while x <= x1 + step:
        y = base - amp * (0.55 * math.sin(x * f1 + ph) + 0.30 * math.sin(x * f2 + ph * 1.7) + 0.15 * math.sin(x * 0.27 + ph * 0.6))
        pts.append((x, y))
        x += step
    pts.append((x1 + step, bot))
    s.poly(pts, fill=col)


def acacia(s, x, yb, sc, col=(40, 36, 30)):
    s.line([(x, yb), (x - 1 * sc, yb - 9 * sc), (x + 2 * sc, yb - 13 * sc)], col, 1.3 * sc)
    s.line([(x - 1 * sc, yb - 9 * sc), (x - 6 * sc, yb - 12 * sc)], col, 1.0 * sc)
    s.ell(x - 11 * sc, yb - 17 * sc, x + 13 * sc, yb - 11 * sc, fill=col)
    s.ell(x - 7 * sc, yb - 19 * sc, x + 8 * sc, yb - 14 * sc, fill=col)


def palm(s, x, yb, hgt, trunk=(70, 52, 34), leaf=(52, 104, 50)):
    s.line([(x, yb), (x - 1.5, yb - hgt * 0.5), (x - 2.5, yb - hgt)], trunk, 1.8)
    tx, ty = x - 2.5, yb - hgt
    for ang in (-170, -140, -110, -70, -40, -10):
        a = math.radians(ang)
        s.line([(tx, ty), (tx + hgt * 0.32 * math.cos(a), ty + hgt * 0.22 * math.sin(a) + hgt * 0.10)], leaf, 1.7)


def pine(s, x, yb, hgt, col=(38, 70, 44)):
    s.line([(x, yb), (x, yb - hgt * 0.55)], (60, 44, 30), 1.4)
    s.ell(x - hgt * 0.34, yb - hgt, x + hgt * 0.34, yb - hgt * 0.62, fill=col)


def head_person(s, x, yb, ph, col, skin=(226, 192, 162), hair=(30, 26, 24)):
    s.rect(x - ph * 0.20, yb - ph * 0.62, x + ph * 0.20, yb, fill=col)
    s.ell(x - ph * 0.15, yb - ph, x + ph * 0.15, yb - ph * 0.68, fill=skin)
    s.pie([x - ph * 0.16, yb - ph * 1.01, x + ph * 0.16, yb - ph * 0.72], 180, 360, hair)


def flag_wave(s, x, y, fw, fh, stripes, vertical=False, wave=1.2):
    """Pole flag with a gentle wave (drawn as thin column strips)."""
    n = len(stripes)
    cols = max(8, int(fw))
    for k in range(cols):
        t = k / cols
        dy = math.sin(t * 5.0) * wave
        x0, x1 = x + t * fw, x + (t + 1.0 / cols) * fw + 0.3
        for i, c in enumerate(stripes):
            if vertical:
                if int(t * n) == i:
                    s.rect(x0, y + dy, x1, y + dy + fh, fill=c)
            else:
                s.rect(x0, y + dy + i * fh / n, x1, y + dy + (i + 1) * fh / n, fill=c)

MAP = {
    "na": [(-168, 66), (-156, 71), (-125, 70), (-95, 70), (-80, 63), (-65, 60), (-56, 52), (-66, 45), (-70, 42), (-76, 35), (-81, 30), (-80, 25), (-84, 30), (-90, 29), (-97, 26), (-97, 20), (-90, 21), (-87, 21), (-83, 10), (-78, 8), (-85, 10), (-92, 15), (-105, 20), (-112, 28), (-117, 32), (-124, 40), (-124, 48), (-135, 57), (-150, 60), (-160, 58), (-165, 62)],
    "gl": [(-72, 78), (-55, 82), (-25, 82), (-20, 72), (-40, 64), (-50, 62), (-58, 70)],
    "sa": [(-78, 8), (-72, 12), (-62, 10), (-50, 0), (-35, -6), (-39, -15), (-48, -26), (-58, -35), (-65, -42), (-68, -52), (-74, -50), (-73, -40), (-71, -20), (-76, -14), (-81, -5), (-79, 1)],
    "eu": [(-10, 36), (-9, 43), (-2, 44), (-4, 48), (2, 51), (8, 54), (8, 57), (12, 56), (14, 54), (22, 55), (28, 60), (22, 63), (18, 60), (16, 56), (10, 58), (5, 60), (5, 62), (14, 68), (25, 71), (31, 70), (40, 67), (60, 69), (70, 73), (80, 73), (100, 77), (115, 74), (140, 72), (160, 70), (180, 68), (180, 65), (165, 60), (156, 51), (150, 59), (140, 54), (135, 44), (129, 41), (129, 35), (126, 35), (125, 39), (121, 40), (122, 31), (120, 25), (110, 20), (108, 16), (109, 11), (105, 9), (100, 13), (100, 5), (104, 1), (98, 8), (98, 16), (94, 17), (92, 22), (87, 21), (80, 15), (77, 8), (73, 17), (72, 21), (67, 24), (57, 26), (50, 30), (48, 29), (51, 25), (56, 26), (58, 23), (52, 16), (49, 14.3), (45, 13), (43, 13), (35, 28), (34, 31), (36, 36), (28, 37), (26, 40), (23, 38), (22, 37), (19, 41), (18, 40), (13, 44), (9, 44), (3, 43), (0, 39), (-6, 36)],
    "af": [(-17, 21), (-6, 35), (10, 37), (32, 31), (43, 12), (51, 12), (40, -5), (40, -15), (35, -25), (27, -34), (18, -34), (12, -17), (9, -1), (8, 4), (-8, 4), (-17, 14)],
    "au": [(114, -22), (122, -18), (130, -12), (137, -12), (142, -11), (146, -19), (153, -27), (150, -37), (141, -38), (131, -31), (115, -34)],
    "uk": [(-6, 50), (2, 51), (0, 53), (-3, 58), (-6, 57), (-5, 54), (-3, 54)],
    "ie": [(-10, 52), (-6, 52), (-6, 55), (-9, 54)],
    "jp": [(131, 34), (135, 34), (140, 35), (142, 38), (141, 41), (139, 40), (136, 37), (132, 35)],
    "hk": [(140, 42), (145, 43), (142, 45)],
    "su": [(95, 5), (104, -5), (106, -6), (98, 2)],
    "bo": [(109, 1), (117, 7), (119, 1), (116, -4), (110, -3)],
    "jv": [(105.2, -6.8), (108, -6.3), (114.5, -7.7), (114.4, -8.7), (106, -7.4)],
    "mg": [(44, -13), (50, -15), (47, -25), (44, -22)],
    "nz": [(172, -35), (178, -38), (174, -42), (170, -46), (167, -45)],
}


# ---------- small shared scene bits ----------
def trail(s, x0, y0, x1, y1, col=(255, 200, 120), w=1.4, head=(255, 255, 255)):
    s.line([(x0, y0), (x1, y1)], col, w)
    s.ell(x1 - 1.8, y1 - 1.8, x1 + 1.8, y1 + 1.8, fill=head)


def burst(s, cx, cy, r, c1=(255, 214, 90), c2=(255, 110, 24)):
    glow(s, cx, cy, r * 1.8, c2, 0.8)
    pts = []
    for i in range(16):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.radians(i * 22.5)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    s.poly(pts, fill=c2)
    s.ell(cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5, fill=c1)


def stars(s, w, h, n, ymax, seed=7):
    for i in range(n):
        sx = (i * 97 + seed * 31) % int(w)
        sy = (i * 53 + seed * 17) % max(1, int(ymax))
        s.ell(sx, sy, sx + 1.3, sy + 1.3, fill=(235, 232, 210))


def skyline(s, w, base, col, seed, hmax, hmin=10, step=14, win=True):
    x = 0
    k = seed
    while x < w:
        k = (k * 37 + 11) % 97
        bw = 10 + k % 12
        bh = hmin + (k * 5) % int(hmax - hmin)
        s.rect(x, base - bh, x + bw, base, fill=col)
        if win:
            lit_windows(s, x, base - bh, bw, base, seed)
        x += bw + 1 + (k % 3)


def nato_star(s, cx, cy, r, col=(255, 255, 255)):
    s.ell(cx - r, cy - r, cx + r, cy + r, outline=col, width=max(1.0, r * 0.14))
    for a in (0, 90, 180, 270):
        ra = math.radians(a)
        s.poly([(cx + r * 1.15 * math.cos(ra), cy + r * 1.15 * math.sin(ra)),
                (cx + r * 0.16 * math.cos(ra + 1.2), cy + r * 0.16 * math.sin(ra + 1.2)),
                (cx - r * 0.1 * math.cos(ra), cy - r * 0.1 * math.sin(ra)),
                (cx + r * 0.16 * math.cos(ra - 1.2), cy + r * 0.16 * math.sin(ra - 1.2))], fill=col)


def tank(s, x, yb, sc, col=(70, 82, 60)):
    s.rect(x - 11 * sc, yb - 4 * sc, x + 11 * sc, yb, fill=(40, 44, 36))
    s.rect(x - 9 * sc, yb - 8 * sc, x + 8 * sc, yb - 4 * sc, fill=col)
    s.rect(x - 4 * sc, yb - 11 * sc, x + 4 * sc, yb - 8 * sc, fill=col)
    s.line([(x + 3 * sc, yb - 9.5 * sc), (x + 15 * sc, yb - 11 * sc)], col, 1.6 * sc)


# ---------- LEAD illustrations ----------
def il_cop(w, h):
    s = SD(w, h, (170, 214, 226))
    vgrad(s, 0, h, (88, 140, 200), (255, 226, 176))
    glow(s, w * 0.30, h * 0.60, 60, (255, 240, 190), 0.95)
    cloud(s, w * 0.52, h * 0.16, 1.2, (255, 244, 232))
    cloud(s, w * 0.80, h * 0.26, 1.0, (255, 236, 220))
    ridge(s, h * 0.52, 22, 0, w, h, (146, 166, 200), 0.4)
    s.poly([(w * 0.60, h * 0.55), (w * 0.69, h * 0.14), (w * 0.82, h * 0.55)], fill=(116, 138, 176))
    s.poly([(w * 0.69, h * 0.14), (w * 0.665, h * 0.28), (w * 0.69, h * 0.24), (w * 0.705, h * 0.31), (w * 0.725, h * 0.23), (w * 0.745, h * 0.29)], fill=(248, 250, 252))
    ridge(s, h * 0.63, 12, 0, w, h, (80, 118, 148), 2.0)
    vgrad(s, h * 0.68, h, (58, 138, 190), (20, 80, 138))
    for k in range(14):
        yy = h * 0.74 + (k % 3) * 6
        xx = 10 + k * w / 14
        s.line([(xx, yy), (xx + 8, yy - 2), (xx + 16, yy)], (190, 224, 242), 1.0)
    s.rect(0, h * 0.86, w, h, fill=(206, 200, 188))
    s.rect(0, h * 0.86, w, h * 0.885, fill=(168, 162, 152))
    # conference hall with dome
    hx0, hx1 = w * 0.04, w * 0.46
    s.rect(hx0, h * 0.44, hx1, h * 0.88, fill=(238, 240, 242), outline=(84, 90, 100), width=1)
    s.pie([hx0 + 30, h * 0.16, hx1 - 30, h * 0.80], 180, 360, (206, 222, 234))
    s.pie([hx0 + 50, h * 0.28, hx1 - 50, h * 0.72], 180, 360, (170, 200, 222))
    n = int((hx1 - hx0) / 8)
    for k in range(n + 1):
        s.line([(hx0 + 3 + k * 8, h * 0.50), (hx0 + 3 + k * 8, h * 0.88)], (120, 134, 150), 0.8)
    s.rect(hx0, h * 0.64, hx1, h * 0.665, fill=(120, 134, 150))
    for k in range(6):
        s.rect(hx0 + 14 + k * 26, h * 0.70, hx0 + 24 + k * 26, h * 0.85, fill=(250, 214, 140))
    cols = ((200, 16, 46), (0, 51, 153), (0, 130, 60), (250, 200, 0), (30, 30, 30), (240, 240, 240), (230, 100, 20), (90, 40, 140), (0, 150, 150))
    for k, c in enumerate(cols):
        pole_flag(s, hx0 + 6 + k * 15, h * 0.16 + (k % 2) * 4, h * 0.44, 11, 8, [c])
    palm(s, hx1 + 12, h * 0.90, 46)
    palm(s, hx0 - 2, h * 0.92, 36)
    # oil derrick + crossed-out sign (no fossil fuels)
    ox = w * 0.56
    s.poly([(ox - 12, h * 0.88), (ox, h * 0.46), (ox + 12, h * 0.88)], outline=(40, 40, 46), width=1.6)
    s.line([(ox - 7, h * 0.70), (ox + 7, h * 0.70)], (40, 40, 46), 1.2)
    s.line([(ox - 4, h * 0.56), (ox + 4, h * 0.56)], (40, 40, 46), 1.2)
    s.ell(ox - 20, h * 0.30 - 14, ox + 20, h * 0.30 + 26, fill=(255, 255, 255), outline=RED, width=3)
    s.line([(ox - 14, h * 0.30 + 20), (ox + 14, h * 0.30 - 8)], RED, 3)
    s.ell(ox - 7, h * 0.30 - 2, ox + 7, h * 0.30 + 14, fill=(30, 30, 34))
    # overtime clock
    cx, cy, r = w * 0.92, h * 0.40, 21
    glow(s, cx, cy, 36, (255, 250, 220), 0.6)
    s.ell(cx - r, cy - r, cx + r, cy + r, fill=(252, 252, 250), outline=INK, width=2)
    for k in range(12):
        a = math.radians(k * 30)
        s.line([(cx + r * 0.82 * math.cos(a), cy + r * 0.82 * math.sin(a)), (cx + r * 0.95 * math.cos(a), cy + r * 0.95 * math.sin(a))], INK, 1)
    s.line([(cx, cy), (cx, cy - r * 0.72)], INK, 1.8)
    s.line([(cx, cy), (cx + r * 0.5, cy + r * 0.18)], RED, 1.8)
    s.ell(cx - 2, cy - 2, cx + 2, cy + 2, fill=RED)
    for k, c in enumerate(((60, 70, 100), (120, 60, 60), (50, 90, 80), (30, 30, 36), (90, 70, 110), (160, 120, 60))):
        person(s, w * 0.72 + k * 11, h - 1, 24 + (k * 3) % 6, c)
    return s.out()


def il_kyiv(w, h):
    s = SD(w, h, (14, 20, 44))
    hor = h * 0.72
    vgrad(s, 0, hor, (8, 10, 34), (170, 64, 34))
    stars(s, w, h * 0.45, 20, h * 0.45)
    s.rect(0, hor, w, h, fill=(24, 30, 58))
    for i in range(7):
        s.rect(6 + i * w / 7, hor + 8 + (i * 7) % 12, 6 + i * w / 7 + 18, hor + 9.4 + (i * 7) % 12, fill=(60, 70, 108))
    skyline(s, w, hor, (18, 16, 30), 3, 46, 14)
    cx = w * 0.62  # golden domes
    s.rect(cx - 16, hor - 34, cx + 16, hor, fill=(30, 22, 36))
    for dx, top in ((-11, 52), (0, 60), (11, 52)):
        s.pie([cx + dx - 6, hor - top, cx + dx + 6, hor - top + 12], 180, 360, (232, 178, 56))
        s.line([(cx + dx, hor - top), (cx + dx, hor - top - 6)], (232, 178, 56), 1)
    mx = w * 0.30  # museum with columns, damaged
    s.rect(mx - 22, hor - 26, mx + 22, hor, fill=(52, 46, 58))
    s.poly([(mx - 26, hor - 26), (mx, hor - 40), (mx + 26, hor - 26)], fill=(52, 46, 58))
    for k in range(5):
        s.rect(mx - 17 + k * 8, hor - 24, mx - 15 + k * 8, hor, fill=(90, 84, 96))
    burst(s, mx + 14, hor - 22, 9)
    by = hor + 3  # bridge
    s.rect(0, by, w, by + 4, fill=(8, 8, 14))
    for i in range(0, int(w), 40):
        s.pie([i, by - 2, i + 40, by + 26], 180, 360, (8, 8, 14))
        s.pie([i + 4, by + 3, i + 36, by + 22], 180, 360, (24, 30, 58))
    for k in range(5):  # incoming missiles + drones
        x0 = w * (0.62 + k * 0.07)
        trail(s, x0, 6 + k * 5, x0 - 36, 30 + k * 6, (255, 190, 100), 1.3)
    for k in range(4):
        dx = w * (0.76 + k * 0.05)
        s.rect(dx, 14 + k * 9, dx + 6, 16 + k * 9, fill=(200, 200, 210))
        s.line([(dx - 2, 15 + k * 9), (dx + 8, 15 + k * 9)], (200, 200, 210), 0.8)
    # air-defence streaks
    for k in range(3):
        trail(s, 20 + k * 40, hor, 36 + k * 44, 12 + k * 4, (160, 230, 255), 0.9, (210, 245, 255))
    return s.out()


def il_poland(w, h):
    s = SD(w, h, (20, 26, 52))
    hor = h * 0.74
    vgrad(s, 0, hor, (16, 20, 46), (210, 108, 70))
    stars(s, w, h * 0.4, 14, h * 0.4, 3)
    s.rect(0, hor, w, h, fill=(28, 34, 44))
    skyline(s, w, hor, (24, 24, 36), 8, 36, 12)
    px = w * 0.62  # tower (palace of culture silhouette)
    s.rect(px - 12, hor - 40, px + 12, hor, fill=(20, 20, 32))
    s.rect(px - 7, hor - 58, px + 7, hor - 40, fill=(20, 20, 32))
    s.poly([(px - 4, hor - 58), (px, hor - 76), (px + 4, hor - 58)], fill=(20, 20, 32))
    lit_windows(s, px - 12, hor - 40, 24, hor, 5)
    # red/white flag
    fx = w * 0.12
    s.line([(fx, hor - 56), (fx, hor)], (70, 70, 76), 1.4)
    flag_wave(s, fx, hor - 56, 40, 26, [(250, 250, 250), (220, 20, 60)], wave=1.5)
    # strike: missiles, blast
    for k in range(4):
        x0 = w * (0.36 + k * 0.1)
        trail(s, x0 + 34, 4 + k * 6, x0, hor - 6 - k * 4, (255, 200, 120), 1.4)
    burst(s, w * 0.44, hor - 8, 16)
    glow(s, w * 0.44, hor, 40, (255, 140, 40), 0.5)
    # NATO emblem
    nato_star(s, w * 0.90, h * 0.30, 13, (230, 236, 250))
    s.ell(w * 0.90 - 17, h * 0.30 - 17, w * 0.90 + 17, h * 0.30 + 17, outline=(130, 150, 210), width=1)
    return s.out()


# ---------- FEATURE illustrations ----------
def ic_natoland(w, h):
    s = SD(w, h, (0, 87, 183))
    s.rect(0, 0, w, h * 0.5, fill=(0, 87, 183))
    s.rect(0, h * 0.5, w, h, fill=(255, 215, 0))
    glow(s, w * 0.5, h * 0.5, 44, (255, 255, 255), 0.5)
    # map slice being traded
    pts = [(w * 0.60, h * 0.18), (w * 0.78, h * 0.22), (w * 0.92, h * 0.34), (w * 0.88, h * 0.55), (w * 0.72, h * 0.62), (w * 0.62, h * 0.50), (w * 0.66, h * 0.36)]
    s.poly(pts, fill=(60, 120, 74), outline=(20, 50, 30), width=1.2)
    s.line([(w * 0.70, h * 0.2), (w * 0.72, h * 0.62)], (20, 50, 30), 0.9)
    s.poly([(w * 0.745, h * 0.30), (w * 0.84, h * 0.30), (w * 0.84, h * 0.56), (w * 0.745, h * 0.56)], fill=(210, 60, 50))
    s.line([(w * 0.745, h * 0.30), (w * 0.84, h * 0.56)], (255, 255, 255), 1.0)
    # NATO medallion
    s.ell(w * 0.14, h * 0.12, w * 0.46, h * 0.88, fill=(24, 44, 100), outline=(255, 255, 255), width=1.5)
    nato_star(s, w * 0.30, h * 0.50, 13)
    # arrows both ways
    s.line([(w * 0.47, h * 0.40), (w * 0.58, h * 0.40)], (255, 255, 255), 2)
    s.poly([(w * 0.58, h * 0.33), (w * 0.62, h * 0.40), (w * 0.58, h * 0.47)], fill=(255, 255, 255))
    s.line([(w * 0.62, h * 0.70), (w * 0.50, h * 0.70)], INK, 2)
    s.poly([(w * 0.50, h * 0.63), (w * 0.46, h * 0.70), (w * 0.50, h * 0.77)], fill=INK)
    return s.out()


def ic_eu_arms(w, h):
    s = SD(w, h, (200, 214, 232))
    vgrad(s, 0, h, (120, 150, 200), (232, 226, 214))
    ridge(s, h * 0.58, 8, 0, w, h, (120, 140, 120), 1.0)
    s.rect(0, h * 0.72, w, h, fill=(110, 118, 84))
    eu_flag(s, 8, 6, 52, 34)
    s.line([(8, 4), (8, h * 0.74)], (70, 70, 76), 1.5)
    for k, (x, sc) in enumerate(((w * 0.45, 1.1), (w * 0.64, 1.3), (w * 0.84, 1.0))):
        tank(s, x, h * (0.74 + k % 2 * 0.1), sc)
    for k in range(4):  # ammo crates
        s.rect(66 + k * 14, h * 0.84 - (k % 2) * 7, 78 + k * 14, h * 0.84 + 5 - (k % 2) * 7, fill=(122, 98, 56), outline=(60, 46, 26), width=0.8)
    s.rect(w - 52, 6, w - 6, 24, fill=(0, 51, 153))
    s.rect(w - 52, 6, w - 6, 8, fill=(255, 204, 0))
    return s.out()


def ic_riyadh(w, h):
    s = SD(w, h, (240, 190, 130))
    vgrad(s, 0, h, (60, 70, 130), (250, 190, 120))
    glow(s, w * 0.2, h * 0.7, 40, (255, 226, 160), 0.8)
    s.rect(0, h * 0.78, w, h, fill=(196, 150, 96))
    skyline(s, w, h * 0.78, (120, 96, 96), 4, 26, 8, win=False)
    kx = w * 0.62  # Kingdom Centre style tower with arch
    s.poly([(kx - 10, h * 0.80), (kx - 7, h * 0.10), (kx + 7, h * 0.10), (kx + 10, h * 0.80)], fill=(60, 80, 108))
    s.pie([kx - 6, h * 0.08, kx + 6, h * 0.34], 0, 180, (240, 190, 130))
    ax = w * 0.38  # round tower
    s.rect(ax - 7, h * 0.30, ax + 7, h * 0.80, fill=(84, 96, 120))
    s.ell(ax - 9, h * 0.22, ax + 9, h * 0.38, fill=(96, 110, 136))
    s.line([(ax, h * 0.22), (ax, h * 0.08)], (84, 96, 120), 1)
    trail(s, 4, h * 0.10, w * 0.50, h * 0.42, (255, 120, 60), 1.6, (255, 240, 200))
    trail(s, w * 0.86, h * 0.74, w * 0.58, h * 0.24, (150, 230, 255), 1.2, (240, 250, 255))
    burst(s, w * 0.55, h * 0.30, 7, (255, 240, 200), (255, 170, 60))
    for k in range(5):
        s.rect(w * 0.60 + k * 8, h * 0.52 + (k * 5) % 9, w * 0.60 + k * 8 + 3, h * 0.52 + 3 + (k * 5) % 9, fill=(60, 50, 50))
    s.rect(w * 0.78, h * 0.70, w * 0.96, h * 0.78, fill=(110, 90, 70))
    return s.out()


def ic_cyclone(w, h):
    s = SD(w, h, (60, 70, 90))
    vgrad(s, 0, h, (60, 70, 92), (150, 164, 180))
    cx, cy = w * 0.46, h * 0.40
    glow(s, cx, cy, 44, (230, 236, 244), 0.8)
    for arm in range(4):
        pts = []
        for t in range(40):
            a = arm * 1.57 + t * 0.16
            r = 3 + t * 0.95
            pts.append((cx + r * math.cos(a) * 1.5, cy + r * math.sin(a) * 0.82))
        s.line(pts, (244, 246, 250), 4.6 - arm * 0.3)
    s.ell(cx - 5, cy - 4, cx + 5, cy + 4, fill=(40, 46, 62))
    s.rect(0, h * 0.72, w, h, fill=(40, 100, 140))
    for k in range(10):
        xx = k * 19
        s.line([(xx, h * 0.80 + (k % 3) * 4), (xx + 8, h * 0.76 + (k % 3) * 4), (xx + 16, h * 0.80 + (k % 3) * 4)], (210, 232, 244), 1.2)
    s.poly([(w * 0.62, h * 0.72), (w, h * 0.66), (w, h * 0.74), (w * 0.62, h * 0.76)], fill=(196, 176, 120))
    for x, y in ((w * 0.78, h * 0.72), (w * 0.88, h * 0.70), (w * 0.95, h * 0.69)):
        s.line([(x, y), (x + 5, y - 14), (x + 14, y - 18)], (50, 40, 30), 1.4)
        for ang in (-160, -110, -60, -20):
            a = math.radians(ang)
            s.line([(x + 14, y - 18), (x + 14 + 9 * math.cos(a), y - 18 + 7 * math.sin(a) + 3)], (40, 110, 60), 1.6)
    for k in range(6):
        s.line([(8 + k * 14, h * 0.08 + k * 3), (24 + k * 14, h * 0.14 + k * 3)], (200, 214, 230), 0.9)
    return s.out()


def ic_cyber(w, h):
    s = SD(w, h, (8, 20, 28))
    vgrad(s, 0, h, (6, 18, 30), (14, 52, 70))
    for k in range(18):  # code rain
        x = 5 + k * 10
        for j in range(5):
            s.rect(x, 4 + ((k * 13 + j * 9) % 40), x + 3, 7 + ((k * 13 + j * 9) % 40), fill=(40, 190 - j * 24, 120))
    s.rect(0, h * 0.82, w, h, fill=(30, 40, 50))
    bx = w * 0.12  # bank
    s.poly([(bx, h * 0.36), (bx + 40, h * 0.12), (bx + 80, h * 0.36)], fill=(214, 216, 222))
    s.rect(bx + 2, h * 0.36, bx + 78, h * 0.42, fill=(190, 192, 200))
    for k in range(6):
        s.rect(bx + 6 + k * 12, h * 0.42, bx + 12 + k * 12, h * 0.82, fill=(228, 230, 236))
    s.rect(bx, h * 0.82, bx + 80, h * 0.86, fill=(190, 192, 200))
    # lock (broken)
    lx = w * 0.62
    s.ell(lx - 9, h * 0.14, lx + 9, h * 0.58, outline=(230, 190, 40), width=3)
    s.rect(lx - 16, h * 0.42, lx + 16, h * 0.82, fill=(230, 190, 40))
    s.ell(lx - 3, h * 0.54, lx + 3, h * 0.62, fill=(60, 40, 10))
    s.poly([(lx - 2, h * 0.14), (lx + 3, h * 0.30), (lx - 4, h * 0.36), (lx + 4, h * 0.46)], fill=(8, 20, 28))
    # payment cards
    for k, c in enumerate(((220, 60, 40), (30, 70, 160), (240, 160, 20))):
        x = w * 0.74 + k * 6
        y = h * 0.20 + k * 11
        s.rect(x, y, x + 36, y + 22, fill=c, outline=(255, 255, 255), width=0.8)
        s.rect(x, y + 5, x + 36, y + 9, fill=(30, 30, 34))
    return s.out()


def ic_berlin(w, h):
    s = SD(w, h, (170, 200, 230))
    vgrad(s, 0, h, (110, 150, 206), (246, 226, 196))
    cloud(s, 24, 12, 0.8, (255, 255, 255))
    cloud(s, 140, 18, 0.7, (255, 250, 244))
    gx0, gx1 = w * 0.28, w * 0.74  # Brandenburg gate
    s.rect(gx0, h * 0.16, gx1, h * 0.26, fill=(214, 204, 178), outline=(120, 110, 90), width=0.8)
    s.rect(gx0 + 3, h * 0.26, gx1 - 3, h * 0.30, fill=(200, 190, 164))
    for k in range(6):
        x = gx0 + 5 + k * (gx1 - gx0 - 12) / 5
        s.rect(x, h * 0.30, x + 6, h * 0.74, fill=(226, 216, 190), outline=(130, 120, 100), width=0.6)
    s.rect(gx0, h * 0.74, gx1, h * 0.78, fill=(190, 180, 154))
    s.poly([(w * 0.51, h * 0.16), (w * 0.47, h * 0.04), (w * 0.55, h * 0.04)], fill=(96, 120, 84))
    s.rect(0, h * 0.78, w, h, fill=(120, 126, 112))
    for k, st in enumerate(([(0, 0, 0), (221, 0, 0), (255, 206, 0)], [(0, 51, 153)], [(0, 87, 183), (255, 215, 0)], [(200, 16, 46), (255, 255, 255), (30, 60, 150)])):
        x = 8 + k * 14
        s.line([(x, h * 0.18), (x, h * 0.80)], (70, 70, 76), 1.2)
        flag_wave(s, x, h * 0.18, 12, 8, st, wave=0.8)
    s.ell(w * 0.34, h * 0.80, w * 0.70, h * 0.98, fill=(70, 56, 44))
    for k in range(7):
        a = math.radians(200 + k * 23)
        person(s, w * 0.52 + 36 * math.cos(a), h * 0.90 + 8 * math.sin(a) + 6, 16, [(30, 40, 70), (110, 40, 50), (40, 80, 60)][k % 3])
    return s.out()


def ic_jurf(w, h):
    s = SD(w, h, (240, 210, 150))
    vgrad(s, 0, h, (130, 170, 214), (248, 224, 176))
    glow(s, w * 0.80, h * 0.24, 22, (255, 244, 200), 0.9)
    ridge(s, h * 0.58, 8, 0, w, h, (212, 176, 120), 0.8)
    s.rect(0, h * 0.68, w, h, fill=(210, 176, 122))
    for k in range(8):  # town blocks
        bx = 8 + k * 22 + (k % 2) * 3
        s.rect(bx, h * 0.52 - (k % 3) * 5, bx + 16, h * 0.76, fill=(226, 206, 170), outline=(150, 126, 90), width=0.7)
    s.rect(w * 0.54, h * 0.34, w * 0.64, h * 0.76, fill=(214, 190, 150))
    s.pie([w * 0.54, h * 0.24, w * 0.64, h * 0.44], 180, 360, (80, 140, 120))
    s.line([(w * 0.59, h * 0.24), (w * 0.59, h * 0.10)], (70, 70, 76), 1.2)
    flag_wave(s, w * 0.59, h * 0.10, 22, 13, [(206, 17, 38), (255, 255, 255), (20, 20, 20)], wave=1.0)
    s.rect(w * 0.605, h * 0.12, w * 0.605 + 22, h * 0.12 + 1, fill=(206, 17, 38))
    for k, x in enumerate((w * 0.30, w * 0.74, w * 0.88)):  # Iraqi army vehicles + troops
        tank(s, x, h * 0.90, 1.0, (86, 90, 64))
    for k in range(5):
        person(s, w * 0.42 + k * 7, h * 0.97, 16, (84, 88, 60))
    return s.out()


def ic_summit(w, h):
    s = SD(w, h, (180, 190, 210))
    vgrad(s, 0, h, (70, 84, 120), (226, 214, 200))
    s.rect(0, h * 0.78, w, h, fill=(96, 74, 62))
    specs = [((178, 34, 52), (255, 255, 255), (60, 60, 140)), ((222, 41, 16), (255, 222, 0), None), ((255, 255, 255), (0, 57, 166), (213, 43, 30))]
    for k in range(3):
        cx = w * (0.20 + k * 0.30)
        for j, c in enumerate(specs[k]):
            if c:
                s.rect(cx - 20, h * 0.06 + j * 6, cx + 20, h * 0.06 + (j + 1) * 6, fill=c)
        s.line([(cx - 20, h * 0.04), (cx - 20, h * 0.34)], (70, 70, 76), 1.2)
        head_person(s, cx, h * 0.98, 38, [(30, 34, 60), (20, 20, 24), (44, 44, 56)][k])
        s.poly([(cx - 3, h * 0.60), (cx + 3, h * 0.60), (cx + 1, h * 0.80)], fill=(210, 40, 40) if k != 1 else (230, 230, 240))
        s.rect(cx - 17, h * 0.82, cx + 17, h * 0.98, fill=(60, 44, 36), outline=(30, 22, 18), width=1)
    # handshake bridge
    s.line([(w * 0.28, h * 0.74), (w * 0.42, h * 0.74)], (226, 192, 162), 3)
    s.line([(w * 0.58, h * 0.74), (w * 0.72, h * 0.74)], (226, 192, 162), 3)
    return s.out()


def ic_voyager(w, h):
    s = SD(w, h, (4, 6, 18))
    vgrad(s, 0, h, (4, 4, 14), (14, 14, 40))
    stars(s, w, h, 40, h, 5)
    glow(s, w * 0.88, h * 0.5, 24, (80, 130, 220), 0.7)
    s.ell(w * 0.88 - 9, h * 0.5 - 9, w * 0.88 + 9, h * 0.5 + 9, fill=(40, 100, 190))
    s.poly([(w * 0.88 - 7, h * 0.5 - 3), (w * 0.88 - 1, h * 0.5 - 8), (w * 0.88 + 2, h * 0.5), (w * 0.88 - 4, h * 0.5 + 4)], fill=(80, 170, 100))
    vx, vy = w * 0.14, h * 0.5  # probe: dish, bus, boom
    s.ell(vx - 16, vy - 14, vx + 4, vy + 14, fill=(210, 212, 220), outline=(140, 140, 150), width=1)
    s.ell(vx - 8, vy - 6, vx + 2, vy + 6, fill=(160, 162, 172))
    s.rect(vx + 4, vy - 5, vx + 18, vy + 5, fill=(180, 160, 70), outline=(100, 90, 40), width=0.8)
    s.line([(vx + 18, vy - 3), (vx + 40, vy - 18)], (200, 200, 208), 1.2)
    s.line([(vx + 18, vy + 3), (vx + 36, vy + 22)], (200, 200, 208), 1.2)
    # radio signal arcs towards Earth
    for k in range(6):
        x0 = vx + 26 + k * 18
        s.pie([x0, vy - 8 - k * 2, x0 + 12, vy + 8 + k * 2], -50, 50, (255, 206, 90))
    s.line([(vx + 6, vy), (w * 0.88 - 12, vy)], (255, 206, 90), 0.8)
    return s.out()


def ic_swiss(w, h):
    s = SD(w, h, (200, 220, 240))
    vgrad(s, 0, h, (110, 160, 214), (236, 236, 240))
    s.poly([(w * 0.40, h * 0.72), (w * 0.60, h * 0.14), (w * 0.84, h * 0.72)], fill=(150, 164, 190))
    s.poly([(w * 0.60, h * 0.14), (w * 0.54, h * 0.32), (w * 0.60, h * 0.28), (w * 0.64, h * 0.36), (w * 0.68, h * 0.26)], fill=(250, 252, 254))
    s.poly([(w * 0.62, h * 0.72), (w * 0.82, h * 0.30), (w, h * 0.72)], fill=(120, 136, 168))
    s.rect(0, h * 0.72, w, h, fill=(96, 150, 84))
    # Swiss flag
    s.line([(10, 4), (10, h * 0.80)], (70, 70, 76), 1.4)
    s.rect(10, 5, 46, 41, fill=(218, 41, 28))
    s.rect(25, 12, 31, 34, fill=(255, 255, 255))
    s.rect(17, 20, 39, 26, fill=(255, 255, 255))
    # scales of justice
    sx = w * 0.27
    s.rect(sx - 1.5, h * 0.30, sx + 1.5, h * 0.86, fill=(40, 40, 46))
    s.rect(sx - 8, h * 0.86, sx + 8, h * 0.92, fill=(40, 40, 46))
    s.line([(sx - 20, h * 0.34), (sx + 20, h * 0.34)], (40, 40, 46), 1.6)
    for dx in (-20, 20):
        s.line([(sx + dx, h * 0.34), (sx + dx - 7, h * 0.58)], (40, 40, 46), 0.8)
        s.line([(sx + dx, h * 0.34), (sx + dx + 7, h * 0.58)], (40, 40, 46), 0.8)
        s.pie([sx + dx - 9, h * 0.52, sx + dx + 9, h * 0.70], 0, 180, (230, 190, 40))
    return s.out()


# ---------- the journalism (36 verified stories) ----------
LEADS = [
    ("1 • ANTALYA • GLOBAL", "COP31 in overtime: draft deal strips out every fossil-fuel mention",
     "UN climate talks in Antalya, Turkey spill into Saturday. The draft drops EVERY mention of fossil fuels and a $120bn adaptation target. "
     "France, Panama, Greece + 5 more demand the words back; Panama threatens to block any deal. “Worst COP ever” — Mohamed Adow, "
     "Power Shift Africa. A 3rd draft is due Saturday morning.", il_cop),
    ("2 • KYIV • EUROPE", "Kyiv under fire",
     "Russia launches a massive missile-and-drone assault on Ukraine the day after Putin's meeting with Trump and Xi; Kyiv's WWII museum "
     "is damaged. Ukraine hits the Crimea bridge; HIMARS wipes out a Russian command post in Sumy.", il_kyiv),
    ("3 • POLAND • EUROPE", "Missiles hit Poland",
     "Russian missiles and drones strike Polish territory; a blast is reported and Warsaw seeks NATO support. Trump downplayed "
     "the incursions hours before the missiles landed.", il_poland),
]
FEATS = [
    ("4 • EUROPE", "NATO for land?", "The US floats possible NATO membership for Ukraine in exchange for territorial concessions, a report says.", ic_natoland),
    ("5 • EUROPE", "EU arms Ukraine", "EU Council approves €1bn in military aid; the EU allocates a €7.9bn lump sum to Kyiv.", ic_eu_arms),
    ("6 • MIDDLE EAST", "Houthi missile over Riyadh",
     "Arab coalition intercepts a Houthi missile; debris falls on Riyadh, causing material damage. Yemen's government: Houthis turned Hodeidah's ports into weapons hubs.", ic_riyadh),
    ("7 • ASIA-PACIFIC", "Cyclone Akvan landfall", "Akvan crosses the Odisha–Andhra coast near Gopalpur, India, with strong winds and heavy rain.", ic_cyclone),
    ("8 • AMERICAS", "Banks hit by cyberattack", "JPMorgan, Visa and Mastercard report cyber incidents via third-party vendors; core payment networks unaffected.", ic_cyber),
    ("9 • EUROPE", "Berlin summit",
     "“Coalition of the willing” meets: Zelenskyy and US negotiators on Ukraine's future; Europeans ready to visit Moscow if given an active role.", ic_berlin),
    ("10 • MIDDLE EAST", "Iraq retakes Jurf al-Sakhar", "Iraqi forces enter the town after 12 years of Kataib Hezbollah rule and set up a “command headquarters”.", ic_jurf),
    ("11 • GLOBAL", "Trump–Xi–Putin", "At a historic three-way summit Trump calls Putin “a friend of mine” — and says he is too busy to see Kim Jong-un on the Asia trip.", ic_summit),
    ("12 • GLOBAL", "Voyager 1, one light-day out", "Voyager 1 sends a message from a stunning one light-day away from Earth.", ic_voyager),
    ("13 • EUROPE", "Swiss back ICJ verdict",
     "Switzerland calls the Myanmar genocide ruling an “important step forward” for Rohingya justice; first state ever convicted of genocide. Verdict was THU 19 Nov.", ic_swiss),
]
BRIEFS = [
    (14, "US clears ~900,000 AI chips for China in six months, a House panel says."),
    (15, "Indonesia demands Google explain the removal of 19,000 YouTube accounts."),
    (16, "India 239/1 at lunch, Day 3, Wellington Test v New Zealand (368); Rahul and Padikkal frustrate the hosts; deficit down to 129."),
    (17, "Medvedev beats Tiafoe 6–3, 6–4 in the Nitto ATP Finals group stage."),
    (18, "Bayern held 1–1 by Köln; Espanyol stun Athletic Club 1–0."),
    (19, "India A thrash Nepal by 306 runs in the Asia Cup Rising Stars."),
    (20, "India U17 qualify for the AFC U17 Asian Cup 2027 — 0–0 v Malaysia, top of Group E."),
    (21, "Tom Brady in talks to buy a minority stake in Chelsea FC."),
    (22, "2027 Hyundai Elantra unveiled at the Los Angeles Auto Show."),
    (23, "Sensex rallies nearly 898 points."),
    (24, "Bill Gates warns of a looming massive cyberattack."),
    (25, "California AG subpoenas Nvidia over its ex-CEO and China ties."),
    (26, "A second judge blocks Trump's triumphal arch — a “rushed job”."),
    (27, "Two Danes charged over a Russian-recruited plot to kill a Ukrainian rapper."),
    (28, "Indian man jailed 19+ years in the US over a Sikh-separatist murder plot."),
    (29, "Russia has lost 1.6 million troops in the Ukraine war, defence officials say."),
    (30, "US military engagement against Iran has cost $48.3bn, a Pentagon official says."),
    (31, "Israel seeks a rapid strike on Iran as Trump weighs action."),
    (32, "UK–EU strike agriculture and youth-mobility deals."),
    (33, "South Africa's murder rate falls — but killings still average 60 a day."),
    (34, "Morocco commits €366m for a defence-manufacturing base by 2035."),
    (35, "Potatoes complete a full life cycle in simulated lunar soil (Oregon State)."),
    (36, "Hazlewood hints at rethinking his Test future if Cummins loses the captaincy."),
]
REGIONS = [
    ("EUROPE", (1, 2, 3, 4, 5, 9, 13, 17, 18, 27, 29, 32)[:0] or (2, 3, 4, 5, 9, 13, 17, 18, 27, 29, 32), (34, 74, 140)),
    ("ASIA-PACIFIC", (7, 15, 16, 19, 20, 22, 23), (176, 54, 40)),
    ("MIDDLE EAST", (6, 10, 30, 31), (150, 110, 30)),
    ("AMERICAS", (8, 14, 21, 25, 26, 28), (40, 110, 80)),
    ("AFRICA", (33, 34), (96, 70, 40)),
    ("GLOBAL", (1, 11, 12, 24, 35), (70, 74, 84)),
    ("OCEANIA", (36,), (110, 70, 140)),
]
STATS = [("36", "stories from the\nworld today"), ("1.8°C", "October warming vs the\nmid-1800s (Berkeley Earth)"),
         ("€7.9bn", "EU lump sum\nto Ukraine"), ("900K", "AI chips cleared\nfor China"),
         ("19,000", "YouTube accounts\nremoved"), ("306", "runs: India A's\nwin over Nepal")]
# day-so-far rail: (phase, UTC start, [(story, short label)])
RAIL = [
    ("OVERNIGHT", "00:00", [(2, "Kyiv assault"), (3, "Poland hit"), (29, "Russia troop toll")]),
    ("EARLY", "04:00", [(7, "Akvan landfall"), (6, "Riyadh debris"), (10, "Jurf retaken"), (4, "NATO for land report")]),
    ("MORNING", "08:00", [(1, "COP31 3rd draft due"), (9, "Berlin summit"), (13, "Swiss back ICJ")]),
    ("MIDDAY", "12:00", [(16, "Wellington lunch, Day 3"), (12, "Voyager 1 message")]),
]
# story, lon, lat (checked city by city)
PINS = [
    (1, 30.7, 36.9), (2, 30.5, 50.4), (3, 21.0, 52.2), (4, -77.0, 38.9), (5, 4.35, 50.85), (6, 46.7, 24.7),
    (7, 84.9, 19.3), (8, -74.0, 40.7), (9, 13.4, 52.5), (10, 44.2, 32.9), (11, 116.4, 39.9), (12, -118.1, 34.1),
    (13, 7.45, 46.95), (14, -77.0, 38.9), (15, 106.8, -6.2), (16, 174.8, -41.3), (17, 7.7, 45.07), (18, 6.96, 50.94),
    (19, 85.3, 27.7), (20, 77.2, 28.6), (21, -0.1, 51.5), (22, -118.2, 34.05), (23, 72.9, 19.1), (24, -122.3, 47.6),
    (25, -121.5, 38.6), (26, -77.0, 38.9), (27, 12.57, 55.68), (28, -74.0, 40.7), (29, 37.6, 55.75), (30, -77.0, 38.9),
    (31, 35.2, 31.8), (32, -0.1, 51.5), (33, 28.2, -25.7), (34, -6.85, 34.0), (35, -123.3, 44.56), (36, 151.2, -33.9),
]
MAP_R = 6


def place_pins(pts, w, h, r):
    pos = [[px, py - 9.0] for px, py in pts]
    md = 2 * r + 1.5
    for _ in range(600):
        moved = False
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                dx = pos[j][0] - pos[i][0]
                dy = pos[j][1] - pos[i][1]
                dd = math.hypot(dx, dy)
                if dd < md:
                    if dd < 1e-6:
                        dx, dy, dd = 1.0, 0.3 * (1 if (i + j) % 2 else -1), 1.04
                    push = (md - dd) / 2 + 0.05
                    ux, uy = dx / dd, dy / dd
                    pos[i][0] -= ux * push
                    pos[i][1] -= uy * push
                    pos[j][0] += ux * push
                    pos[j][1] += uy * push
                    moved = True
        for p in pos:
            p[0] = min(max(p[0], r + 2), w - r - 2)
            p[1] = min(max(p[1], r + 2), h - r - 2)
        if not moved:
            break
    return pos


def draw_map(page, x, y, w, h):
    lon0, lon1, lat0, lat1 = -130.0, 180.0, 72.0, -46.0

    def pr(lon, lat):
        return ((lon - lon0) / (lon1 - lon0) * w, (lat0 - lat) / (lat0 - lat1) * h)

    s = SD(w, h, SEA)
    for lon in range(-120, 181, 30):
        s.line([pr(lon, lat0), pr(lon, lat1)], (210, 218, 230), 0.7)
    for lat in range(60, -46, -30):
        s.line([pr(lon0, lat), pr(lon1, lat)], (210, 218, 230), 0.7)
    for pts in MAP.values():
        s.poly([pr(*p) for p in pts], fill=LAND, outline=(120, 126, 138), width=1)
    page.paste(s.out(), (x, y))
    d = ImageDraw.Draw(page)
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=2)
    r = MAP_R
    true = [pr(lon, lat) for n, lon, lat in PINS]
    pos = place_pins(true, w, h, r)
    for (tx, ty), (cx_, cy_) in zip(true, pos):
        d.line([x + tx, y + ty, x + cx_, y + cy_], fill=INK, width=1)
        d.ellipse([x + tx - 1.6, y + ty - 1.6, x + tx + 1.6, y + ty + 1.6], fill=INK)
    nf = F(SANS_B, 9)
    for (n, _, _), (cx_, cy_) in zip(PINS, pos):
        d.ellipse([x + cx_ - r, y + cy_ - r, x + cx_ + r, y + cy_ + r], fill=RED, outline=(255, 255, 255), width=1)
        d.text((x + cx_, y + cy_ + 0.5), str(n), font=nf, fill=(255, 255, 255), anchor="mm")
    return true, pos


# ---------- text layout helpers ----------
def rule(d, x0, x1, y, wd=1):
    d.line([x0, y, x1, y], fill=INK, width=wd)


def badge(d, x, y, num, size=11, h=15):
    nf = F(SANS_B, size)
    bw = int(nf.getlength(str(num))) + 8
    d.rectangle([x, y, x + bw, y + h], fill=RED)
    d.text((x + bw / 2 + 0.5, y + h / 2 + 0.5), str(num), font=nf, fill=(255, 255, 255), anchor="mm")
    return bw


def frame_img(page, img, x, y, num, tag=None):
    page.paste(img, (x, y))
    d = ImageDraw.Draw(page)
    d.rectangle([x, y, x + img.width - 1, y + img.height - 1], outline=INK, width=2)
    badge(d, x, y, num)


def text_block(d, x, y, w, hmax, kicker, head, body, hs=(24, 14), bs=(12, 9), hlines=2, lead=1.22, kcol=RED):
    """Kicker + headline + body, largest sizes that fit hmax. Returns bottom y."""
    for h_sz in range(hs[0], hs[1] - 1, -1):
        hf = F(SANS_B, h_sz)
        hl = wrap(head, hf, w)
        if len(hl) > hlines or any(hf.getlength(l) > w for l in hl):
            continue
        for b_sz in range(bs[0], bs[1] - 1, -1):
            bf = F(SANS, b_sz)
            bl = wrap(body, bf, w)
            if any(bf.getlength(l) > w for l in bl):
                continue
            kh = 13 if kicker else 0
            tot = kh + len(hl) * int(h_sz * 1.12) + 3 + len(bl) * int(b_sz * lead)
            if tot <= hmax:
                yy = y
                if kicker:
                    d.text((x, yy), kicker, font=F(SANS_B, 9), fill=kcol)
                    yy += kh
                for l in hl:
                    d.text((x, yy), l, font=hf, fill=INK)
                    yy += int(h_sz * 1.12)
                yy += 3
                for l in bl:
                    d.text((x, yy), l, font=bf, fill=GREY)
                    yy += int(b_sz * lead)
                return yy, h_sz, b_sz
    raise ValueError("text block does not fit: " + head)


def rich_lines(tokens, maxw):
    lines, cur, cw = [], [], 0.0
    for word, f, col in tokens:
        ww = f.getlength(word + " ")
        if cur and cw + f.getlength(word) > maxw:
            lines.append(cur)
            cur, cw = [], 0.0
        cur.append((word, f, col))
        cw += ww
    lines.append(cur)
    return lines


def main(outdir):
    nums = sorted(n for _, ns, _ in REGIONS for n in ns)
    assert nums == list(range(1, 37)), nums
    assert [len(ns) for _, ns, _ in REGIONS] == [11, 7, 4, 6, 2, 5, 1]
    assert len(LEADS) + len(FEATS) + len(BRIEFS) == 36
    assert [p[0] for p in PINS] == list(range(1, 37))

    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)
    d.rectangle([4, 4, W - 5, H - 5], outline=INK, width=2)
    L, R = 14, W - 14
    MX = 92            # main column start (rail occupies L..86)
    MW = R - MX
    log = []

    # kicker
    kf = F(SANS_B, 11)
    d.rectangle([L, 11, L + 9, 21], fill=RED)
    d.text((L + 15, 10), "SATURDAY 21 NOVEMBER 2026 • 36 STORIES • ONE PAGE", font=kf, fill=INK)
    rt = "VERIFIED FROM THIS MORNING'S REPORTING"
    d.text((R - kf.getlength(rt), 10), rt, font=kf, fill=RED)
    rule(d, L, R, 25, 1)

    # masthead (left) + date block (right)
    mf = fit_line("SATURDAY ATLAS", SANS_B, 640, 54, 40)
    d.text((L - 1, 24), "SATURDAY ATLAS", font=mf, fill=INK)
    bar_y = 24 + int(mf.size * 1.02) + 2
    d.rectangle([L, bar_y, L + 640, bar_y + 5], fill=RED)
    sub = "Saturday 21 November 2026 — the world in one page"
    sf = F(SANS_B, 13)
    d.text((L, bar_y + 9), sub, font=sf, fill=INK)
    bx0 = L + 660
    d.rectangle([bx0, 29, R, bar_y + 5], fill=INK)
    ctext(d, (bx0 + R) / 2, 32, "SATURDAY", F(SANS_B, 12), (255, 120, 100))
    ctext(d, (bx0 + R) / 2, 45, "21 NOV 2026", F(SANS_B, 33), (255, 255, 255))
    sy = bar_y + 9 + 17
    stand = "Russia hits Kyiv and Poland, COP31 runs into overtime, and Trump calls Putin “a friend of mine” — a young day, already full."
    stf = fit_line(stand, SANS, R - L, 13, 9)
    d.text((L, sy), stand, font=stf, fill=GREY)
    log.append(("masthead", mf.size, bar_y, sy))

    # by-the-numbers strip
    ty = sy + 19
    th = 34
    wts = [0.86, 1.5, 1.0, 1.0, 1.08, 1.06]
    tw_ = sum(wts)
    rule(d, L, R, ty, 2)
    xs = L
    for i, (big, lab) in enumerate(STATS):
        cw = (R - L) * wts[i] / tw_
        x0 = xs
        xs += cw
        if i:
            d.line([x0, ty + 5, x0, ty + th - 2], fill=INK, width=1)
        bf = fit_line(big, SANS_B, 64 if len(big) > 5 else 60, 26, 14)
        avail_w = cw - 6 - bf.getlength(big) - 6 - 3
        lf = fit_line(max(lab.split("\n"), key=len), SANS, avail_w, 10, 7)
        d.text((x0 + 6, ty + 5 + (26 - bf.size) / 2 - 1), big, font=bf, fill=RED if i % 2 == 0 else INK)
        tx0 = x0 + 6 + bf.getlength(big) + 6
        for k, ln in enumerate(lab.split("\n")):
            d.text((tx0, ty + 6 + k * 12), ln, font=lf, fill=INK)
        assert tx0 + max(lf.getlength(l) for l in lab.split("\n")) <= x0 + cw - 2, lab
    rule(d, L, R, ty + th, 1)

    # region scoreboard
    ry = ty + th + 3
    rh = 16
    rw = (R - L) / 7.0
    for i, (name, ns, col) in enumerate(REGIONS):
        x0 = L + i * rw
        d.rectangle([x0 + 1, ry, x0 + rw - 2, ry + rh], fill=col)
        t = "%s  %d" % (name, len(ns))
        rf = fit_line(t, SANS_B, rw - 10, 10, 8)
        d.text(((x0 + x0 + rw - 1) / 2, ry + rh / 2 + 0.5), t, font=rf, fill=(255, 255, 255), anchor="mm")
    body_top = ry + rh + 6
    log.append(("body_top", body_top))

    # ---- layout rows ----
    BOT = H - 28                       # content bottom (footer below)
    H_LEAD, H_FEAT, H_MAP = 223, 122, 170
    G = 6
    y_lead = body_top
    y_f1 = y_lead + H_LEAD + G
    y_f2 = y_f1 + H_FEAT + 4
    y_map = y_f2 + H_FEAT + G
    y_br = y_map + H_MAP + G
    H_BR = BOT - y_br
    log.append(("rows", y_lead, y_f1, y_f2, y_map, y_br, H_BR))

    # ---- rail: THE DAY SO FAR ----
    RW = 72
    rail_top, rail_bot = body_top, BOT
    d.rectangle([L, rail_top, L + RW, rail_bot], fill=(247, 247, 247), outline=INK, width=1)
    d.rectangle([L, rail_top, L + RW, rail_top + 40], fill=INK)
    ctext(d, L + RW / 2, rail_top + 4, "THE DAY", F(SANS_B, 12), (255, 255, 255))
    ctext(d, L + RW / 2, rail_top + 17, "SO FAR", F(SANS_B, 12), (255, 120, 100))
    ctext(d, L + RW / 2, rail_top + 30, "SAT 21 NOV • UTC", F(SANS_B, 8), (220, 220, 220))
    lx = L + 11
    yy = rail_top + 52
    d.line([lx, yy, lx, rail_bot - 28], fill=INK, width=2)
    lab_f = F(SANS_B, 9)
    ry_pos = {}
    for phase, t0, items in RAIL:
        d.rectangle([lx - 4, yy, L + RW - 4, yy + 24], fill=RED if phase == "MORNING" else INK)
        d.text((lx + 4, yy + 2), phase, font=F(SANS_B, 10), fill=(255, 255, 255))
        d.text((lx + 4, yy + 13), t0 + " UTC", font=F(SANS, 9), fill=(255, 255, 255))
        yy += 32
        for n, lab in items:
            lines = wrap(lab, lab_f, RW - 30)
            hh = max(15, len(lines) * 11)
            d.ellipse([lx - 7, yy, lx + 7, yy + 14], fill=RED, outline=(255, 255, 255), width=1)
            d.text((lx, yy + 7.5), str(n), font=F(SANS_B, 9 if n < 10 else 8), fill=(255, 255, 255), anchor="mm")
            for k, ln in enumerate(lines):
                d.text((lx + 12, yy + 1 + k * 11), ln, font=lab_f, fill=INK)
            yy += hh + 6
        yy += 6
    # arrow at end of the line
    ay = rail_bot - 28
    d.polygon([(lx - 6, ay), (lx + 6, ay), (lx, ay + 10)], fill=INK)
    ctext(d, L + RW / 2, rail_bot - 15, "more to come", F(SANS, 8), GREY)
    ctext(d, L + RW / 2, rail_bot - 8 - 2, "", F(SANS, 8), GREY)
    log.append(("rail_end", yy, ay))
    assert yy < ay - 2, (yy, ay)

    # ---- leads ----
    LW1 = 452
    k1, h1, b1, ill1 = LEADS[0]
    img = ill1(LW1, 98)
    frame_img(page, img, MX, y_lead, 1)
    bot, hs_, bs_ = text_block(d, MX, y_lead + 104, LW1, H_LEAD - 104, k1.split(" • ", 1)[1], h1, b1, hs=(21, 14), bs=(12, 9), hlines=3)
    log.append(("lead1", bot, y_lead + H_LEAD, hs_, bs_))
    assert bot <= y_lead + H_LEAD
    x2 = MX + LW1 + 10
    W2 = R - x2
    hh = (H_LEAD - 6) // 2
    IW = 146
    for i in (1, 2):
        kk, hh_, bb, ill = LEADS[i]
        y0 = y_lead + (i - 1) * (hh + 6)
        frame_img(page, ill(IW, hh), x2, y0, i + 1)
        bot, hs_, bs_ = text_block(d, x2 + IW + 8, y0 + 1, W2 - IW - 8, hh - 2, kk.split(" • ", 1)[1], hh_, bb, hs=(18, 13), bs=(11, 9), hlines=2)
        log.append(("lead%d" % (i + 1), bot, y0 + hh, hs_, bs_))
        assert bot <= y0 + hh
    rule(d, MX, R, y_f1 - 3, 1)

    # ---- features (5 x 2) ----
    FW = (MW - 4 * 7) // 5
    for i, (kk, hd, bd, ill) in enumerate(FEATS):
        r_, c_ = divmod(i, 5)
        x0 = MX + c_ * (FW + 7)
        y0 = (y_f1, y_f2)[r_]
        frame_img(page, ill(FW, 44), x0, y0, i + 4)
        bot, hs_, bs_ = text_block(d, x0, y0 + 47, FW, H_FEAT - 47, kk.split(" • ", 1)[1], hd, bd, hs=(14, 11), bs=(10, 8), hlines=2, lead=1.17)
        log.append(("feat%d" % (i + 4), bot, y0 + H_FEAT, hs_, bs_))
        assert bot <= y0 + H_FEAT, (i + 4, bot)
    rule(d, MX, R, y_map - 3, 1)

    # ---- map + date check ----
    MWID = 524
    draw_map(page, MX, y_map, MWID, H_MAP)
    dx0 = MX + MWID + 8
    dw = R - dx0
    d.rectangle([dx0, y_map, R, y_map + H_MAP], fill=(255, 244, 242), outline=RED, width=3)
    d.rectangle([dx0, y_map, R, y_map + 20], fill=RED)
    d.text((dx0 + 8, y_map + 3), "DATE CHECK — WHAT IS TODAY, WHAT ISN'T", font=fit_line("DATE CHECK — WHAT IS TODAY, WHAT ISN'T", SANS_B, dw - 16, 12, 9), fill=(255, 255, 255))
    items = [
        ("ICJ MYANMAR VERDICT —", "THU 19 Nov (9–6 vote), NOT today. Today: Switzerland backs it."),
        ("COP31 DRAFT —", "the fossil-fuel-free draft was published THU 19 Nov. The overtime and the 3rd draft are SAT 21 Nov."),
        ("TRUMP'S CHINA TRIP —", "ended FRI 20 Nov. Today: the backlash, and the NATO-for-land report."),
    ]
    avail = H_MAP - 28
    for sz in range(13, 8, -1):
        bf, rf = F(SANS_B, sz), F(SANS, sz)
        blocks = []
        for a, b in items:
            toks = [(w_, bf, RED) for w_ in a.split()] + [(w_, rf, INK) for w_ in b.split()]
            blocks.append(rich_lines(toks, dw - 24))
        tot = sum(len(b) for b in blocks) * int(sz * 1.25) + 8 * len(items)
        if tot <= avail:
            break
    else:
        raise ValueError("date check does not fit")
    yy = y_map + 26
    for blk in blocks:
        d.rectangle([dx0 + 8, yy + 2, dx0 + 12, yy + int(sz * 1.25) * len(blk) - 2], fill=RED)
        for ln in blk:
            xx = dx0 + 18
            for word, f, col in ln:
                d.text((xx, yy), word, font=f, fill=col)
                xx += f.getlength(word + " ")
            yy += int(sz * 1.25)
        yy += 8
    log.append(("datecheck", yy, y_map + H_MAP, sz))
    assert yy - 8 <= y_map + H_MAP - 3
    rule(d, MX, R, y_br - 3, 1)

    # ---- briefs: 4 balanced columns ----
    NC = 4
    CW = (MW - (NC - 1) * 10) // NC
    placed = None
    for bsz in range(11, 8, -1):
        bf = F(SANS, bsz)
        lh = int(bsz * 1.2)
        hts = []
        wr = []
        for n, t in BRIEFS:
            ls = wrap(t, bf, CW - 26)
            wr.append(ls)
            hts.append(len(ls) * lh + 5)
        best = None
        N = len(BRIEFS)
        for a in range(1, N - 2):
            for b in range(a + 1, N - 1):
                for c in range(b + 1, N):
                    mx = max(sum(hts[:a]), sum(hts[a:b]), sum(hts[b:c]), sum(hts[c:]))
                    if best is None or mx < best[0]:
                        best = (mx, (0, a, b, c, N))
        if best[0] <= H_BR:
            placed = (bsz, lh, wr, best)
            break
    assert placed, ("briefs do not fit", H_BR, best[0], log)
    bsz, lh, wr, (mx, cuts) = placed
    bf = F(SANS, bsz)
    for ci in range(NC):
        x0 = MX + ci * (CW + 10)
        yy = y_br
        for k in range(cuts[ci], cuts[ci + 1]):
            n = BRIEFS[k][0]
            badge(d, x0, yy, n, 9, 12)
            for j, ln in enumerate(wr[k]):
                d.text((x0 + 24, yy + j * lh - 1), ln, font=bf, fill=INK)
            yy += len(wr[k]) * lh + 5
        if ci:
            d.line([x0 - 5, y_br + 1, x0 - 5, BOT - 1], fill=(190, 190, 190), width=1)
    log.append(("briefs", bsz, mx, H_BR))

    # footer
    rule(d, L, R, BOT + 3, 1)
    foot = "SOURCES: AP · Reuters · FT · The Times · HRW · UN News · IANS · others.   Saturday 21 November 2026 • pins mark the city each story is about."
    d.text((L, BOT + 7), foot, font=fit_line(foot, SANS_B, R - L, 10, 8), fill=INK)

    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "entry.png")
    page.save(out, optimize=True)
    return out, log


if __name__ == "__main__":
    o, lg = main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
    for l in lg:
        print(l)
    print(o)
