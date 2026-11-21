"""make.fun news page, Saturday 21 November 2026: "The Saturday Ledger" R4 (1024x1024).

R3 elements kept: cream broadsheet, category-coloured banner labels, verification chips + date tier chip
(SAT / FRI>SAT) on every story, UTC clock rail with a "now" marker, colour-coded map, waffle chart, DEVELOPING
watch strip, DATE CHECK box.
R4 changes: 40 stories, map pins spread out with zoomed Europe + Middle East insets and leader lines.
R4 fix (vote): all body text >= 11px; 13 full illustrated panels (banner + own art) in 3 rows (4/4/5); the waffle
panel is gone (data lives in the top strip and in story 9's panel as a one-row 61-cell bar); 26 one-line briefs.
Pure PIL, no network, no randomness.  Usage: python3 draw.py [output_dir]
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
FL = "/usr/share/fonts/truetype/liberation/"
F = {
    "sb": FL + "LiberationSans-Bold.ttf",
    "s": FL + "LiberationSans-Regular.ttf",
    "si": FL + "LiberationSans-Italic.ttf",
    "xb": FL + "LiberationSerif-Bold.ttf",
    "x": FL + "LiberationSerif-Regular.ttf",
    "xi": FL + "LiberationSerif-Italic.ttf",
}
_fc = {}


def font(k, s):
    key = (k, s)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(F[k], s)
    return _fc[key]


PAPER = (250, 246, 236)
INK = (22, 22, 26)
GREY = (84, 84, 90)
RULE = (30, 30, 34)
SEA = (216, 228, 236)
LAND = (222, 206, 170)

CAT = {  # category colours (banner labels, map pins)
    "WAR": (190, 38, 30),
    "POL": (30, 78, 160),
    "SCI": (28, 126, 82),
    "ECO": (196, 118, 10),
    "SOC": (118, 60, 150),
    "SPT": (0, 128, 140),
}
CHIP = {  # verification taxonomy
    "C": ("CONFIRMED", (24, 120, 60)),
    "O": ("OFFICIAL", (30, 78, 160)),
    "R": ("REPORTED", (196, 118, 10)),
}

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
WARN = []


def tw(t, f):
    return d.textlength(t, font=f)


def wrap(t, f, w):
    out, cur = [], ""
    for word in t.split():
        trial = (cur + " " + word).strip()
        if tw(trial, f) <= w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def para(x, y, w, t, fk, fs, fill, lh=None, maxlines=None, tag=""):
    f = font(fk, fs)
    lh = lh or int(fs * 1.2)
    lines = wrap(t, f, w)
    if maxlines and len(lines) > maxlines:
        WARN.append(f"{tag}: {len(lines)}>{maxlines} lines: {t[:40]}")
        lines = lines[:maxlines]
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=f, fill=fill)
    return y + len(lines) * lh


def fit_text(x, y, w, t, fk, fs, fill, anchor="la", minsize=6, tag=""):
    s0 = fs
    while tw(t, font(fk, fs)) > w and fs > minsize:
        fs -= 1
    if tag and fs < s0:
        WARN.append(f"{tag}: shrank {s0}->{fs}: {t[:40]}")
    d.text((x, y), t, font=font(fk, fs), fill=fill, anchor=anchor)


def chip(x, y, kind, tier=None):
    """Verification chip + date tier (micro labels, 8px). Returns right edge."""
    name, col = CHIP[kind]
    f = font("sb", 8)
    w = int(tw(name, f)) + 8
    d.rounded_rectangle([x, y, x + w, y + 11], 2, fill=col)
    d.text((x + 4, y + 1), name, font=f, fill=(255, 255, 255))
    x2 = x + w + 3
    if tier:
        t = "SAT" if tier == "S" else "FRI>SAT"
        tc = (30, 30, 34)
        w2 = int(tw(t, f)) + 8
        d.rounded_rectangle([x2, y, x2 + w2, y + 11], 2, outline=tc, width=1)
        d.text((x2 + 4, y + 1), t, font=f, fill=tc)
        x2 += w2 + 3
    return x2


def banner(x, y, w, h, cat, label, num):
    c = CAT[cat]
    d.rectangle([x, y, x + w, y + h], fill=c)
    d.rectangle([x, y, x + h, y + h], fill=INK)
    d.text((x + h / 2, y + h / 2), str(num), font=font("sb", h - 7), fill=(255, 255, 255), anchor="mm")
    fit_text(x + h + 5, y + h / 2, w - h - 8, label, "sb", h - 6, (255, 255, 255), anchor="lm", minsize=10, tag="banner")


# ------------------------------------------------------------------ art (original, drawn in code)
def sky(x, y, w, h, c1, c2):
    for i in range(h):
        t = i / max(1, h - 1)
        col = tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))
        d.line([x, y + i, x + w - 1, y + i], fill=col)


def skyline(x, y, w, h, base, lit=(255, 214, 110), seed=3):
    bw = 12
    cx = x + 2
    k = seed
    while cx < x + w - 6:
        k = (k * 37 + 11) % 97
        bh = 14 + (k % 30) * h // 50
        d.rectangle([cx, y + h - bh, cx + bw, y + h], fill=base)
        for wy in range(y + h - bh + 4, y + h - 3, 6):
            for wx in (cx + 2, cx + 7):
                if (wx + wy + k) % 3:
                    d.rectangle([wx, wy, wx + 2, wy + 2], fill=lit)
        cx += bw + 2


def burst(cx, cy, r, c1=(255, 200, 60), c2=(255, 255, 220)):
    import math
    for i in range(10):
        a = i * math.pi / 5
        d.line([cx, cy, cx + math.cos(a) * r, cy + math.sin(a) * r], fill=c1, width=2)
    d.ellipse([cx - r * .5, cy - r * .5, cx + r * .5, cy + r * .5], fill=c1)
    d.ellipse([cx - r * .28, cy - r * .28, cx + r * .28, cy + r * .28], fill=c2)


def art_cop(x, y, w, h):
    sky(x, y, w, h, (176, 222, 214), (230, 240, 226))
    d.ellipse([x + 10, y + 4, x + 10 + 48, y + 4 + 48], fill=(52, 118, 190))
    d.polygon([(x + 20, y + 14), (x + 34, y + 10), (x + 40, y + 20), (x + 30, y + 32), (x + 18, y + 28)], fill=(70, 150, 90))
    d.polygon([(x + 38, y + 34), (x + 48, y + 30), (x + 50, y + 42), (x + 40, y + 46)], fill=(70, 150, 90))
    # thermometer
    d.rounded_rectangle([x + 72, y + 5, x + 80, y + 40], 4, fill=(255, 255, 255), outline=INK)
    d.rectangle([x + 74, y + 18, x + 78, y + 40], fill=(200, 40, 30))
    d.ellipse([x + 69, y + 36, x + 83, y + 50], fill=(200, 40, 30), outline=INK)
    # clock showing overtime
    cx, cy = x + w - 30, y + 28
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(255, 255, 255), outline=INK, width=2)
    d.line([cx, cy, cx, cy - 15], fill=INK, width=2)
    d.line([cx, cy, cx + 11, cy + 5], fill=(200, 40, 30), width=2)
    d.text((x + 88, y + 18), "DAY 13", font=font("sb", 9), fill=INK)
    d.text((x + 88, y + 30), "NO DEAL", font=font("sb", 9), fill=(200, 40, 30))


def art_saudi(x, y, w, h):
    sky(x, y, w, h, (14, 22, 52), (52, 40, 70))
    skyline(x, y + 12, w, h - 12, (24, 30, 58), seed=7)
    import math
    for i, (sx, sy) in enumerate([(14, 4), (70, 2), (118, 6)]):
        ex, ey = x + sx + 44, y + 30 + i * 3
        d.line([x + sx, y + sy, ex, ey], fill=(255, 200, 90), width=2)
        burst(ex, ey, 9)
    d.text((x + w - 6, y + h - 4), "RIYADH 3 · JAZAN 2", font=font("sb", 8), fill=(255, 255, 255), anchor="rb")


def art_mercury(x, y, w, h):
    sky(x, y, w, h, (8, 10, 26), (20, 22, 48))
    for k in range(18):
        d.point((x + (k * 37) % w, y + (k * 19) % h), fill=(255, 255, 255))
        d.rectangle([x + (k * 53) % w, y + (k * 29) % h, x + (k * 53) % w + 1, y + (k * 29) % h + 1], fill=(200, 200, 230))
    cx, cy = x + w - 46, y + h // 2
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(150, 144, 138))
    for (a, b, r) in [(-9, -6, 5), (6, 8, 4), (-3, 11, 3), (11, -11, 3)]:
        d.ellipse([cx + a - r, cy + b - r, cx + a + r, cy + b + r], outline=(106, 100, 96), width=2)
    d.arc([cx - 44, cy - 36, cx + 44, cy + 36], 120, 330, fill=(255, 220, 120), width=1)
    sx, sy = x + 44, y + 26
    d.rectangle([sx - 7, sy - 5, sx + 7, sy + 5], fill=(220, 190, 70))
    d.rectangle([sx - 28, sy - 3, sx - 11, sy + 3], fill=(70, 120, 210))
    d.rectangle([sx + 11, sy - 3, sx + 28, sy + 3], fill=(70, 120, 210))
    d.polygon([(sx + 7, sy), (sx + 22, sy - 6), (sx + 22, sy + 6)], fill=(255, 150, 40))


def art_quake(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 226, 200))
    d.polygon([(x, y + h), (x, y + h - 14), (x + 40, y + 10), (x + 70, y + h - 16), (x + 110, y + 14), (x + w, y + h - 12), (x + w, y + h)], fill=(160, 132, 104))
    pts = [(x + 2, y + 24), (x + 30, y + 24), (x + 38, y + 8), (x + 48, y + 36), (x + 58, y + 14), (x + 70, y + 30), (x + 90, y + 24), (x + w - 2, y + 24)]
    d.line(pts, fill=(190, 38, 30), width=2)


def art_hormuz(x, y, w, h):
    sky(x, y, w, h, (190, 218, 238), (240, 232, 214))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(52, 100, 150))
    d.polygon([(x + 18, y + h - 14), (x + w - 24, y + h - 14), (x + w - 34, y + h - 26), (x + 30, y + h - 26)], fill=INK)
    d.rectangle([x + 52, y + h - 36, x + 70, y + h - 26], fill=(190, 38, 30))
    d.polygon([(x + w - 40, y + 6), (x + w - 28, y + 12), (x + w - 14, y + 4), (x + w - 28, y + 16)], fill=(70, 70, 80))
    d.line([x + w - 40, y + 6, x + w - 30, y + 14], fill=(190, 38, 30), width=2)


def art_denmark(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(198, 12, 48))
    d.rectangle([x + 24, y, x + 36, y + h], fill=(255, 255, 255))
    d.rectangle([x, y + h // 2 - 6, x + w, y + h // 2 + 6], fill=(255, 255, 255))
    d.rectangle([x + w - 56, y + 6, x + w - 8, y + 24], fill=(255, 255, 255), outline=INK)
    d.line([x + w - 50, y + 15, x + w - 14, y + 15], fill=INK, width=2)
    d.polygon([(x + w - 14, y + 15), (x + w - 22, y + 10), (x + w - 22, y + 20)], fill=INK)


def art_trump_iran(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(34, 40, 60))
    d.polygon([(x + w // 2, y + 4), (x + w // 2 + 16, y + 30), (x + w // 2, y + 38), (x + w // 2 - 16, y + 30)], fill=(255, 205, 60))
    d.text((x + w // 2, y + 22), "!", font=font("sb", 18), fill=(34, 40, 60), anchor="mm")
    d.rectangle([x + 8, y + h - 12, x + 50, y + h - 4], fill=(28, 130, 70))
    d.rectangle([x + 8, y + h - 8, x + 50, y + h - 4], fill=(255, 255, 255))
    d.rectangle([x + w - 50, y + h - 12, x + w - 8, y + h - 4], fill=(30, 78, 160))
    d.text((x + 4, y + 4), "IRAN", font=font("sb", 8), fill=(255, 255, 255))


def art_chip(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(26, 40, 70))
    d.rectangle([x + w // 2 - 20, y + 6, x + w // 2 + 20, y + h - 6], fill=(60, 100, 160), outline=(200, 220, 255))
    d.text((x + w // 2, y + h // 2), "NVDA", font=font("sb", 10), fill=(255, 255, 255), anchor="mm")
    for k in range(5):
        d.line([x + w // 2 - 20 - 8, y + 10 + k * 6, x + w // 2 - 20, y + 10 + k * 6], fill=(200, 220, 255))
        d.line([x + w // 2 + 20, y + 10 + k * 6, x + w // 2 + 28, y + 10 + k * 6], fill=(200, 220, 255))



def art_trial(x, y, w, h):
    sky(x, y, w, h, (214, 236, 222), (240, 248, 240))
    for (a, b, r, c) in [(40, 18, 14, (28, 126, 82)), (70, 26, 10, (14, 80, 52)), (100, 16, 9, (28, 126, 82)),
                         (130, 28, 12, (14, 80, 52))]:
        d.ellipse([x + a - r, y + b - r, x + a + r, y + b + r], fill=c, outline=INK)
        d.ellipse([x + a - r // 3, y + b - r // 3, x + a + r // 3, y + b + r // 3], fill=(240, 248, 240))
    # single-row data strip: 61 cells, 37 shrank (5 of them no detectable tumour)
    cw = (w - 12) / 61.0
    for i in range(61):
        col = (14, 80, 52) if i < 5 else ((28, 126, 82) if i < 37 else (205, 214, 206))
        x0 = x + 6 + i * cw
        d.rectangle([int(x0), y + h - 14, int(x0 + cw) - 1, y + h - 6], fill=col)


def art_plane(x, y, w, h):
    sky(x, y, w, h, (150, 190, 232), (226, 236, 246))
    cx, cy = x + w // 2, y + h // 2
    d.polygon([(cx - 46, cy + 4), (cx + 40, cy - 6), (cx + 54, cy - 2), (cx + 40, cy + 6), (cx - 40, cy + 10)], fill=(250, 250, 252), outline=INK)
    d.polygon([(cx - 6, cy - 2), (cx + 14, cy - 2), (cx - 8, cy - 22)], fill=(200, 205, 216), outline=INK)
    d.polygon([(cx - 6, cy + 6), (cx + 14, cy + 6), (cx - 8, cy + 24)], fill=(200, 205, 216), outline=INK)
    d.polygon([(cx - 46, cy + 4), (cx - 38, cy + 4), (cx - 48, cy - 12)], fill=(196, 118, 10))
    d.text((x + 6, y + 4), "-1,000 JOBS", font=font("sb", 9), fill=(150, 30, 20), anchor="la")


def art_paint(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(86, 52, 40))
    d.rectangle([x + w // 2 - 28, y + 3, x + w // 2 + 28, y + h - 3], fill=(212, 170, 60), outline=INK)
    d.rectangle([x + w // 2 - 23, y + 7, x + w // 2 + 23, y + h - 7], fill=(40, 120, 96))
    cx = x + w // 2
    d.ellipse([cx - 11, y + 12, cx + 11, y + 36], fill=(206, 150, 110), outline=INK)
    d.arc([cx - 10, y + 17, cx - 1, y + 21], 200, 340, fill=INK, width=2)
    d.arc([cx + 1, y + 17, cx + 10, y + 21], 200, 340, fill=INK, width=2)
    for k, px in enumerate((-14, -7, 0, 7, 14)):
        d.ellipse([cx + px - 4, y + 9 - (k % 2) * 2, cx + px + 4, y + 16 - (k % 2) * 2], fill=(200, 40, 50))
    d.text((x + 6, y + h - 4), "PULLED", font=font("sb", 8), fill=(255, 255, 255), anchor="lb")


def art_tennis(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 120, 96))
    d.rectangle([x + 10, y + 5, x + w - 10, y + h - 5], outline=(255, 255, 255), width=2)
    d.line([x + w // 2, y + 5, x + w // 2, y + h - 5], fill=(255, 255, 255), width=2)
    d.line([x + 10, y + h // 2, x + w - 10, y + h // 2], fill=(255, 255, 255), width=1)
    bx, by = x + w // 2 + 22, y + h // 2 - 10
    d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=(226, 236, 70), outline=INK)
    d.arc([bx - 6, by - 6, bx + 6, by + 6], 120, 240, fill=(255, 255, 255), width=1)
    rx, ry = x + 34, y + h // 2 + 2
    d.ellipse([rx - 11, ry - 14, rx + 11, ry + 10], outline=INK, width=3)
    d.line([rx, ry + 10, rx + 8, ry + 22], fill=INK, width=3)


def art_f1(x, y, w, h):
    sky(x, y, w, h, (20, 14, 44), (70, 30, 90))
    skyline(x, y, w, h - 12, (36, 26, 70), lit=(255, 120, 200), seed=11)
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(50, 50, 60))
    for k in range(0, w, 16):
        d.rectangle([x + k, y + h - 7, x + k + 8, y + h - 6], fill=(255, 255, 255))
    cx, cy = x + w // 2 - 6, y + h - 17
    d.polygon([(cx - 36, cy + 4), (cx + 34, cy + 4), (cx + 30, cy - 4), (cx + 6, cy - 8), (cx - 8, cy - 14), (cx - 14, cy - 8), (cx - 30, cy - 4)], fill=(210, 30, 40), outline=(255, 255, 255))
    d.ellipse([cx - 40, cy - 2, cx - 28, cy + 10], fill=INK)
    d.ellipse([cx + 22, cy - 2, cx + 34, cy + 10], fill=INK)
    for k, c in enumerate(((210, 30, 40), (210, 30, 40), (210, 30, 40))):
        d.ellipse([x + 8 + k * 12, y + 6, x + 16 + k * 12, y + 14], fill=c)


ART = {"trial": art_trial, "plane": art_plane, "paint": art_paint, "tennis": art_tennis, "f1": art_f1}

# ------------------------------------------------------------------ content
HEROES = [
    dict(n=1, cat="SCI", label="CLIMATE · ANTALYA", art=art_cop, chip="C", tier="S",
         hl="COP31 runs past its deadline with no deal",
         body="Fossil-fuel deadlock pushed the UN summit into overtime; a final text could land late Friday or early Saturday. Draft reportedly omits fossil fuels. (AJ, Anadolu)"),
    dict(n=2, cat="WAR", label="WAR · RIYADH & JAZAN", art=art_saudi, chip="C", tier="S",
         hl="Five Houthi missiles intercepted over Saudi Arabia",
         body="Coalition says it shot down 3 ballistic missiles aimed at Riyadh and 2 at Jazan early Saturday; no casualties reported. (Al Jazeera, Anadolu)"),
    dict(n=3, cat="SCI", label="SPACE · MERCURY", art=art_mercury, chip="O", tier="S",
         hl="BepiColombo due to enter Mercury orbit tonight",
         body="ESA says thrusters fire at 19:24 CET (18:24 UTC) to brake the probe after 8 years. Second mission to orbit Mercury. (ESA via Anadolu)"),
]

MIDS = [
    dict(n=4, cat="SCI", label="QUAKE · JUNÍN, PERU", art=art_quake, chip="O", tier="S",
         hl="Magnitude 6.7 quake strikes central Peru",
         body="Epicentre near Ondores, Junín region, 00:09 UTC. No tsunami threat; no casualties or major damage reported. (USGS)"),
    dict(n=5, cat="WAR", label="IRAN · STRAIT OF HORMUZ", art=art_hormuz, chip="R", tier="S",
         hl="IRGC claims it downed a US drone",
         body="Guards say they shot it down over Hormuz; no confirmation. Iran also denied a strike on Qeshm Island. (AJ, Anadolu)"),
    dict(n=6, cat="POL", label="US–IRAN · WASHINGTON", art=art_trump_iran, chip="R", tier="F",
         hl="Trump warns Iran: “we're going to fight”",
         body="Over a rumoured plot against Washington: “If they do, we're going to fight.” No public evidence cited. (Anadolu)"),
    dict(n=7, cat="POL", label="DIPLOMACY · COPENHAGEN", art=art_denmark, chip="C", tier="F",
         hl="Denmark expels Russian defence attaché",
         body="Seven days to leave. Two Danes charged over a foiled plot against a Ukrainian rapper; Moscow: “vengeful”. (AJ, Anadolu)"),
    dict(n=8, cat="ECO", label="TECH · NVIDIA / US", art=art_chip, chip="C", tier="F",
         hl="Trump wants Nvidia's Huang back",
         body="Said he'd “love to see Jensen be given a second chance”; the board chair says no reinstatement after his 12 Nov exit. (AJ)"),
]

# row 3 (5 panels): story 9 (data) + four briefs promoted to full panels
EXTRA = [
    dict(n=9, cat="SCI", label="DATA · PANCREATIC CANCER", art="trial", chip="R", tier="S",
         hl="37 of 61 tumours shrank",
         body="Early trial; 5 had no detectable tumour. Larger studies needed. (Anadolu)"),
    dict(n=10, cat="ECO", label="BUSINESS · LUFTHANSA", art="plane", chip="R", tier="S",
         hl="Lufthansa to cut 1,000 jobs",
         body="Cuts planned at its Frankfurt and Munich hubs, reported Saturday."),
    dict(n=15, cat="SOC", label="ART · CHRISTIE'S", art="paint", chip="R", tier="S",
         hl="Christie's pulls Kahlo work",
         body="The work was withdrawn from sale over Mexico's queries about it."),
    dict(n=33, cat="SPT", label="TENNIS · ATP, TURIN", art="tennis", chip="O", tier="S",
         hl="Alcaraz v Shelton in the ATP semis",
         body="Semi-final in Turin; the other tie was unconfirmed at 07:15 UTC."),
    dict(n=35, cat="SPT", label="F1 · LAS VEGAS GP", art="f1", chip="R", tier="S",
         hl="F1 Las Vegas GP lights-out",
         body="Sat 20:00 local, which is 04:00 UTC Sunday."),
]

# briefs, ONE LINE each: (n, cat, chip, tier, bold lead, text, lon, lat)
BRIEFS = [
    (11, "ECO", "R", "S", "Japan–Saudi oil deal:", "8m-barrel reserve buy, 16m storage", 139.7, 35.7),
    (12, "ECO", "R", "S", "Angola's Endiama", "to pay $180m for 10% of De Beers", 13.2, -8.8),
    (13, "SPT", "O", "S", "UEFA fines England's FA €15,000", "over Madrid chants", 6.2, 46.4),
    (14, "SPT", "O", "S", "FIA to hire full-time F1 stewards", "from 2027", 2.3, 48.9),
    (16, "ECO", "R", "S", "Signal limits mobile screenshots", "to block AI assistants", -122.4, 37.8),
    (17, "POL", "R", "S", "Newsom floats AI emergency powers;", "needs lawmakers", -121.5, 38.6),
    (18, "WAR", "R", "S", "UK confirms cyber ops", "vs Russia, China, Iran, N Korea", -0.1, 51.5),
    (19, "ECO", "R", "S", "US offshore minerals sale:", "$6m bids, American Samoa", -170.7, -14.3),
    (20, "SOC", "R", "S", "Seoul: Lee orders exam overhaul", "after AI cheating", 127.0, 37.5),
    (21, "POL", "R", "S", "Araghchi:", "US blockade must lift before oil exports resume", 51.4, 35.7),
    (22, "POL", "R", "F", "Qatar pledges €15bn more", "for Germany; Merz thanks it", 13.4, 52.5),
    (23, "POL", "R", "F", "EU–UK summit, Brussels", "deepens defence, migration ties", 4.35, 50.85),
    (24, "SOC", "C", "F", "Paris: 3 officers get 5 years", "(3–4 suspended), Zecler case", 2.35, 48.85),
    (25, "WAR", "R", "S", "FBI probes apparent breach", "of NCIC records database", -77.0, 38.9),
    (26, "POL", "R", "S", "US lawmakers urge ban", "on Chinese AI in federal systems", -77.05, 38.85),
    (27, "SOC", "O", "S", "Education Cannot Wait $52m", "for 300,000+ children", 35.5, 33.9),
    (28, "WAR", "R", "S", "Sudan army:", "restoring security in Blue Nile state", 34.3, 11.8),
    (29, "ECO", "R", "S", "Airbnb bans chore demands", "from 20 Nov bookings", -122.4, 37.77),
    (30, "SOC", "R", "S", "Manson Wembley petition tops 20,000;", "he denies claims", -0.28, 51.55),
    # --- new in R4 (research 21 Nov ~07:10 UTC)
    (31, "POL", "C", "S", "Ladakh votes:", "first local-body polls since UT formation", 77.6, 34.2),
    (32, "SOC", "R", "S", "S. Korea CSAT:", "111 caught cheating; essay exams start", 127.0, 37.55),
    (34, "SPT", "R", "S", "Premier League:", "Liverpool–Man Utd, Newcastle–Arsenal", -2.99, 53.41),
    (36, "POL", "R", "F", "US Senate passes bill", "to speed energy-project approvals", -77.0, 38.88),
    (37, "POL", "R", "F", "Iraqi forces deploy to Jurf al-Sakhar", "after militia deal", 44.2, 32.9),
    (38, "POL", "R", "F", "Myanmar, China object", "to ICJ Rohingya genocide ruling", 96.1, 19.7),
    (39, "POL", "R", "F", "Villepin announces", "2027 French presidential bid", 2.3, 48.8),
    (40, "WAR", "R", "S", "Coalition strikes Houthi targets", "as rebels hit Saudi Arabia", 44.2, 15.4),
]

# pins for hero/mid stories: n -> (lon, lat)
PINS = {1: (30.7, 36.9), 2: (46.7, 24.7), 4: (-75.5, -11.0), 5: (56.3, 26.6), 6: (-77.0, 38.9),
        7: (12.6, 55.7), 8: (-121.9, 37.4), 10: (8.7, 50.1), 15: (-74.0, 40.7), 33: (7.7, 45.1),
        35: (-115.2, 36.1)}
CATS_BY_N = {h["n"]: h["cat"] for h in HEROES + MIDS + EXTRA}
CATS_BY_N[3] = "SCI"
for b in BRIEFS:
    CATS_BY_N[b[0]] = b[1]
    PINS[b[0]] = (b[6], b[7])
N_STORIES = 40
assert sorted(CATS_BY_N) == list(range(1, N_STORIES + 1))


# ------------------------------------------------------------------ drawing
def rule(x1, y1, x2, y2, w=1, c=RULE):
    d.line([x1, y1, x2, y2], fill=c, width=w)


def draw_header():
    fit_text(10, 4, 700, "THE SATURDAY LEDGER  ·  ONE PAGE, ONE DAY, EVERY ITEM SOURCED", "sb", 10, (170, 30, 20), minsize=10, tag="hdr")
    fit_text(1014, 4, 500, "COMPILED 07:15 UTC · SAT 21 NOV 2026 · 40 STORIES · 6 REGIONS", "sb", 10, INK, anchor="ra", minsize=10, tag="hdr")
    rule(10, 18, 1014, 18, 2)
    fit_text(512, 17, 1004, "Saturday 21 November 2026", "xb", 50, INK, anchor="ma")
    rule(10, 82, 1014, 82, 1)
    fit_text(512, 84, 1004,
             "COP31 runs past its deadline  ·  Five Houthi missiles shot down over Saudi Arabia  ·  BepiColombo due at Mercury tonight",
             "xi", 17, (150, 30, 20), anchor="ma", minsize=14)
    rule(10, 106, 1014, 106, 2)


def draw_legend():
    y = 109
    d.text((10, y + 1), "HOW TO READ:", font=font("sb", 10), fill=INK)
    x = 92
    for k in "COR":
        x = chip(x, y, k) + 3
        expl = {"C": "two+ outlets agree", "O": "agency / institution", "R": "single source / claim"}[k]
        d.text((x, y), expl, font=font("s", 11), fill=GREY)
        x += tw(expl, font("s", 11)) + 10
    f = font("sb", 8)
    for tag, txt in (("SAT", "happened / due 21 Nov"), ("FRI>SAT", "dated Fri 20 Nov, still in Sat roundups")):
        w = int(tw(tag, f)) + 8
        d.rounded_rectangle([x, y, x + w, y + 11], 2, outline=INK)
        d.text((x + 4, y + 1), tag, font=f, fill=INK)
        d.text((x + w + 4, y), txt, font=font("s", 11), fill=GREY)
        x += w + 4 + tw(txt, font("s", 11)) + 10
    if x > 1020:
        WARN.append("legend overflow %d" % x)
    rule(10, 124, 1014, 124, 1)


def draw_kpis():
    cells = [("3 + 2", "missiles intercepted:\nRiyadh + Jazan", CAT["WAR"]),
             ("6.7", "magnitude, Peru quake\nat 00:09 UTC", CAT["SCI"]),
             ("18:24", "UTC: BepiColombo's\nMercury orbit burn", CAT["SCI"]),
             ("37 / 61", "pancreatic cancer patients\nwith shrunken tumours", CAT["SCI"]),
             ("1,000", "Lufthansa hub jobs\nto go", CAT["ECO"]),
             ("€15bn", "Qatar's new pledge\nfor Germany", CAT["POL"])]
    cw = 1004 / 6
    for i, (big, small, col) in enumerate(cells):
        x = 10 + i * cw
        d.rectangle([x + 2, 127, x + 5, 177], fill=col)
        fit_text(x + 10, 125, cw - 14, big, "xb", 28, INK)
        lines = small.split("\n")
        for j, ln in enumerate(lines):
            fit_text(x + 10, 154 + j * 12, cw - 14, ln, "s", 11, GREY, minsize=11, tag="kpi")
    rule(10, 181, 1014, 181, 1)


def region_of(n):
    ll = PINS.get(n)
    if ll is None:
        return "SPACE / GLOBAL"
    lon, lat = ll
    if lon < -150:
        return "ASIA-PACIFIC"
    if lon < -30:
        return "AMERICAS"
    if 34 <= lon <= 62 and 12 <= lat <= 36:
        return "MIDDLE EAST"
    if lon > 62:
        return "ASIA-PACIFIC"
    if lat < 25 and lon < 52:
        return "AFRICA"
    return "EUROPE"


REGCOL = {"MIDDLE EAST": (190, 38, 30), "EUROPE": (30, 78, 160), "AMERICAS": (118, 60, 150),
          "ASIA-PACIFIC": (0, 128, 140), "AFRICA": (28, 126, 82), "SPACE / GLOBAL": (60, 60, 70)}
REG_COUNTS = {}


def draw_region_bar(y):
    counts = {}
    for n in range(1, N_STORIES + 1):
        counts[region_of(n)] = counts.get(region_of(n), 0) + 1
    REG_COUNTS.update(counts)
    order = sorted(counts, key=lambda k: (-counts[k], k))
    tot = sum(counts.values())
    x = 10
    for name in order:
        n = counts[name]
        w = int(1004 * n / tot)
        d.rectangle([x, y, x + w - 2, y + 13], fill=REGCOL[name])
        label = "%s %d" % (name, n)
        if name == "SPACE / GLOBAL":
            label = "SPACE %d" % n
        fit_text(x + w / 2, y + 1, w - 4, label, "sb", 10, (255, 255, 255), anchor="ma", minsize=9, tag="region")
        x += w
    return y + 17


TL_EVENTS = [(0.15, "4", "SCI", "00:09 Peru quake"),
             (2.0, "2", "WAR", "Early: Riyadh, Jazan intercepts"),
             (4.5, "7", "POL", "AM: Denmark, Trump items"),
             (7.25, "NOW", None, "07:15 compiled"),
             (12.0, "1", "SCI", "COP31 text due (expected)"),
             (15.0, "34", "SPT", "15:00 Premier League kick-offs (most)"),
             (18.4, "3", "SCI", "18:24 BepiColombo burn")]


def draw_timeline(y0, y1, x0=10, x1=124):
    d.rectangle([x0, y0, x1, y1], fill=(236, 230, 214), outline=INK)
    d.rectangle([x0, y0, x1, y0 + 16], fill=INK)
    d.text(((x0 + x1) / 2, y0 + 8), "THE DAY · UTC", font=font("sb", 10), fill=(255, 255, 255), anchor="mm")
    ay0, ay1 = y0 + 30, y1 - 38
    ax = x0 + 22

    def ty(h):
        return ay0 + (ay1 - ay0) * h / 24.0

    d.line([ax, ay0, ax, ay1], fill=INK, width=2)
    for h in range(0, 25, 3):
        d.line([ax - 4, ty(h), ax + 4, ty(h)], fill=INK)
        d.text((x0 + 2, ty(h) - 5), "%02d" % h, font=font("sb", 10), fill=INK)
    for h, n, cat, txt in TL_EVENTS:
        y = ty(h)
        if n == "NOW":
            d.polygon([(ax - 7, y), (ax + 1, y - 5), (ax + 1, y + 5)], fill=(190, 38, 30))
            d.line([ax, y, x1 - 3, y], fill=(190, 38, 30), width=1)
            d.text((ax + 6, y - 13), txt, font=font("sb", 11), fill=(190, 38, 30))
            continue
        c = CAT[cat]
        if h > 7.3:
            d.ellipse([ax - 5, y - 5, ax + 5, y + 5], fill=PAPER, outline=c, width=2)
        else:
            d.ellipse([ax - 5, y - 5, ax + 5, y + 5], fill=c)
        para(ax + 9, y - 6, x1 - ax - 11, txt, "s", 11, INK, lh=12, maxlines=4, tag="tl")
    d.text((x0 + 4, y1 - 27), "solid = happened", font=font("s", 11), fill=GREY)
    d.text((x0 + 4, y1 - 14), "ring = scheduled", font=font("s", 11), fill=GREY)


def draw_panel(x, y, w, h, s, ah, hs, hl_lines, body_lines):
    """Full illustrated panel: bold banner label, own art (height ah), chip, serif headline, 11px body."""
    bh = 16
    banner(x, y, w, bh, s["cat"], s["label"], s["n"])
    d.rectangle([x, y + bh, x + w, y + h], fill=(252, 249, 241), outline=INK)
    art = s["art"] if callable(s["art"]) else ART[s["art"]]
    art(x + 1, y + bh + 1, w - 1, ah)
    cy = y + bh + 1 + ah + 3
    chip(x + 4, cy, s["chip"], s["tier"])
    ty = para(x + 4, cy + 14, w - 8, s["hl"], "xb", hs, INK, lh=hs + 1, maxlines=hl_lines, tag="hl" + str(s["n"]))
    end = para(x + 4, ty + 2, w - 8, s["body"], "s", BODY, (40, 40, 46), lh=BODY + 1, maxlines=body_lines, tag="body" + str(s["n"]))
    if end > y + h:
        WARN.append("panel %d body overflows box by %d" % (s["n"], end - (y + h)))
    PANEL_SLACK.append((s["n"], y + h - end))


BODY = 11
PANEL_SLACK = []


# ---- map: world + zoomed insets, pins spread with leader lines
LANDS = [
    [(-168, 66), (-140, 70), (-100, 72), (-80, 70), (-60, 52), (-66, 44), (-80, 32), (-82, 25), (-97, 26), (-105, 22), (-117, 32), (-124, 40), (-125, 49), (-140, 60), (-165, 60)],
    [(-80, 9), (-60, 10), (-35, -6), (-40, -22), (-58, -38), (-68, -54), (-74, -45), (-71, -20), (-81, -5)],
    [(-55, 60), (-20, 70), (-22, 80), (-60, 82), (-70, 76)],
    [(-10, 36), (-9, 44), (-2, 49), (5, 54), (10, 58), (20, 70), (30, 70), (40, 62), (40, 46), (28, 41), (22, 36), (12, 38), (3, 38)],
    [(-17, 15), (-16, 28), (-6, 36), (10, 37), (32, 31), (43, 12), (51, 11), (40, -15), (33, -28), (20, -35), (12, -18), (9, 4), (-8, 5)],
    [(28, 41), (40, 46), (60, 55), (70, 72), (110, 76), (150, 70), (180, 68), (165, 58), (142, 52), (135, 36), (122, 30), (122, 22), (108, 10), (100, 3), (92, 20), (78, 8), (68, 24), (56, 27), (50, 14), (43, 12), (34, 30), (36, 38)],
    [(114, -22), (130, -12), (142, -11), (153, -27), (146, -39), (130, -32), (115, -34)],
    [(95, 5), (105, -6), (120, -9), (108, -6), (98, 3)],
    [(129, 33), (141, 42), (145, 44), (136, 34)],
    # extra detail (visible mostly in the insets)
    [(-5.5, 50), (1.5, 51), (1.7, 53), (-2, 56), (-3, 58.5), (-6, 57), (-5, 54), (-4.5, 52)],      # Great Britain
    [(-10, 52), (-6, 52), (-6, 55), (-9, 54.5)],                                                   # Ireland
    [(5, 58), (5, 62), (14, 67), (25, 70), (30, 69), (28, 60), (18, 59), (12, 56)],               # Scandinavia
    [(26, 40), (36, 41), (42, 41), (44, 38), (36, 36), (28, 36.5)],                                # Anatolia
]
SEAS = [  # carved-out water (Mediterranean, Red Sea, Persian Gulf)
    [(-5.6, 36), (0, 36.8), (10, 37.2), (11, 38), (16, 38.2), (22, 36.5), (28, 36.4), (36, 36), (36, 33), (32, 31), (25, 31.5), (10, 33.5), (0, 35.5)],
    [(32.5, 29.5), (34, 28), (39, 20), (43, 12.5), (42, 12.5), (37, 18), (33, 27)],
    [(48, 30), (50, 28), (52, 26), (56, 26.6), (56.5, 24.5), (51.5, 24), (50.5, 26)],
]
EU_BOX = (-12, 36, 34, 62)   # lon0, lon1, lat0, lat1
ME_BOX = (34, 62, 12, 40)


def in_box(ll, box):
    lon, lat = ll
    return box[0] <= lon <= box[1] and box[2] <= lat <= box[3]


def where(n):
    ll = PINS[n]
    if in_box(ll, EU_BOX):
        return "EU"
    if in_box(ll, ME_BOX):
        return "ME"
    return "WORLD"


def spread(items, w, h, md=13, rad=6, ymin=None):
    """items: [(n, x, y)] -> {n: (px, py)}; deterministic repulsion so pins never overlap."""
    pos = [[x, y] for _, x, y in items]
    orig = [[x, y] for _, x, y in items]
    for _ in range(400):
        moved = False
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                dx, dy = pos[j][0] - pos[i][0], pos[j][1] - pos[i][1]
                dist = math.hypot(dx, dy)
                if dist < md:
                    if dist < 0.01:
                        dx, dy, dist = math.cos(i * 2.4 + j), math.sin(i * 2.4 + j), 1.0
                    push = (md - dist) / 2 + 0.05
                    ux, uy = dx / dist, dy / dist
                    pos[i][0] -= ux * push
                    pos[i][1] -= uy * push
                    pos[j][0] += ux * push
                    pos[j][1] += uy * push
                    moved = True
        for k, p in enumerate(pos):
            p[0] += (orig[k][0] - p[0]) * 0.01
            p[1] += (orig[k][1] - p[1]) * 0.01
            p[0] = min(max(p[0], rad + 1), w - rad - 1)
            p[1] = min(max(p[1], (ymin if ymin is not None else rad + 1)), h - rad - 1)
        if not moved:
            break
    return {n: tuple(p) for (n, _, _), p in zip(items, pos)}


def map_pins(dd, items, w, h, md=13, ymin=None):
    """Draw leader lines, true-location dots and numbered pins on draw context dd."""
    placed = spread(items, w, h, md=md, ymin=ymin)
    for n, x, y in items:
        px, py = placed[n]
        c = CAT[CATS_BY_N[n]]
        if math.hypot(px - x, py - y) > 3:
            dd.line([x, y, px, py], fill=(60, 60, 66), width=1)
        dd.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=(40, 40, 46))
    for n, x, y in items:
        px, py = placed[n]
        c = CAT[CATS_BY_N[n]]
        dd.ellipse([px - 6, py - 6, px + 6, py + 6], fill=c, outline=(255, 255, 255))
        dd.text((px, py), str(n), font=font("sb", 7), fill=(255, 255, 255), anchor="mm")
    return placed


def inset(x, y, w, h, title, box, ids):
    lon0, lon1, lat0, lat1 = box
    sub = Image.new("RGB", (w, h), SEA)
    dd = ImageDraw.Draw(sub)

    def P(lon, lat):
        return ((lon - lon0) / (lon1 - lon0) * w, (lat1 - lat) / (lat1 - lat0) * h)

    for poly in LANDS:
        dd.polygon([P(*p) for p in poly], fill=LAND, outline=(170, 150, 112))
    for poly in SEAS:
        dd.polygon([P(*p) for p in poly], fill=SEA)
    items = [(n,) + P(*PINS[n]) for n in sorted(ids)]
    map_pins(dd, items, w, h, md=13, ymin=21)
    dd.rectangle([0, 0, int(tw(title, font("sb", 10))) + 9, 14], fill=INK)
    dd.text((4, 1), title, font=font("sb", 10), fill=(255, 255, 255))
    img.paste(sub, (x, y))
    d.rectangle([x, y, x + w, y + h], outline=INK)


def draw_map(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=INK)
    d.rectangle([x, y, x + w, y + 14], fill=INK)
    d.text((x + 5, y + 7), "WHERE IT HAPPENED · pin colour = beat · leader line = true spot", font=font("sb", 10), fill=(255, 255, 255), anchor="lm")
    mh = h - 16 - 17
    mw = int(mh * 360 / 140)
    mx, my = x + 2, y + 16

    def P(lon, lat):
        return (mx + (lon + 180) / 360.0 * mw, my + (82 - lat) / 140.0 * mh)

    d.rectangle([mx, my, mx + mw, my + mh], fill=SEA)
    for poly in LANDS:
        d.polygon([P(*p) for p in poly], fill=LAND, outline=(170, 150, 112))
    # inset footprints on the world map
    for box, nm in ((EU_BOX, "EU"), (ME_BOX, "ME")):
        a, b = P(box[0], box[3]), P(box[1], box[2])
        d.rectangle([a[0], a[1], b[0], b[1]], outline=INK, width=1)
    # world pins (Europe + Middle East are in the insets)
    ids = [n for n in sorted(PINS) if where(n) == "WORLD"]
    items = [(n,) + (P(*PINS[n])[0] - mx, P(*PINS[n])[1] - my) for n in ids]
    placed = spread(items, mw, mh, md=12)
    for n, px0, py0 in items:
        px, py = placed[n]
        if math.hypot(px - px0, py - py0) > 3:
            d.line([mx + px0, my + py0, mx + px, my + py], fill=(60, 60, 66), width=1)
        d.ellipse([mx + px0 - 1.5, my + py0 - 1.5, mx + px0 + 1.5, my + py0 + 1.5], fill=(40, 40, 46))
    for n, px0, py0 in items:
        px, py = placed[n]
        c = CAT[CATS_BY_N[n]]
        d.ellipse([mx + px - 6, my + py - 6, mx + px + 6, my + py + 6], fill=c, outline=(255, 255, 255))
        d.text((mx + px, my + py), str(n), font=font("sb", 7), fill=(255, 255, 255), anchor="mm")
    # insets side by side, right of the world map
    ix = mx + mw + 4
    iw = (x + w - 2 - ix - 3) // 2
    inset(ix, my, iw, mh, "EUROPE", EU_BOX, [n for n in PINS if where(n) == "EU"])
    inset(ix + iw + 3, my, iw, mh, "MIDDLE EAST", ME_BOX, [n for n in PINS if where(n) == "ME"])
    # one-row legend under everything
    ly = my + mh + 4
    d.rounded_rectangle([x + 4, ly, x + 4 + 96, ly + 12], 3, fill=(20, 24, 50))
    d.ellipse([x + 6, ly + 1, x + 17, ly + 11], fill=CAT["SCI"])
    d.text((x + 11.5, ly + 6), "3", font=font("sb", 7), fill=(255, 255, 255), anchor="mm")
    d.text((x + 21, ly + 6), "space: Mercury", font=font("sb", 10), fill=(255, 255, 255), anchor="lm")
    short = {"WAR": "conflict", "POL": "politics", "SCI": "science", "ECO": "business", "SOC": "society", "SPT": "sport"}
    cx = x + 108
    for cat in ["WAR", "POL", "SCI", "ECO", "SOC", "SPT"]:
        d.ellipse([cx, ly + 2, cx + 9, ly + 11], fill=CAT[cat])
        d.text((cx + 12, ly), short[cat], font=font("s", 11), fill=INK)
        cx += 12 + int(tw(short[cat], font("s", 11))) + 8


DEV_ITEMS = [
    ("1", "SCI", "COP31 final text: a third draft was promised; adoption not confirmed. No closing report found at 07:15 UTC."),
    ("3", "SCI", "BepiColombo burn at 18:24 UTC: success is not known until after the manoeuvre."),
    ("2", "WAR", "Houthi–Saudi: both sides threaten key ports; counts are the coalition's own."),
    ("40", "WAR", "Coalition strikes on Houthi targets: headline-level report only."),
    ("5", "WAR", "Hormuz: IRGC drone claim not independently confirmed."),
    ("7", "POL", "Denmark–Russia: Moscow promises an “appropriate response”."),
    ("25", "WAR", "FBI breach is only “apparent”; scope unconfirmed."),
]


def draw_dev(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 250, 240), outline=(190, 38, 30), width=2)
    d.rectangle([x, y, x + w, y + 16], fill=(190, 38, 30))
    d.ellipse([x + 5, y + 4, x + 13, y + 12], fill=(255, 255, 255))
    d.text((x + 18, y + 8), "STILL DEVELOPING · WATCH LIST, 07:15 UTC", font=font("sb", 10), fill=(255, 255, 255), anchor="lm")
    f = font("s", 11)
    tx = x + 24
    blocks = [(n, cat, wrap(t, f, w - 30)) for n, cat, t in DEV_ITEMS]
    textual = sum(len(b[2]) * 12 for b in blocks)
    avail = h - 16 - 8
    gap = (avail - textual) / len(blocks)
    if gap < 2:
        WARN.append("dev overflow gap=%.1f" % gap)
    gap = max(gap, 2)
    if gap > 9:
        WARN.append("dev has slack: gap=%.1f" % gap)
    yy = y + 20
    for n, cat, lines in blocks:
        d.ellipse([x + 5, yy, x + 19, yy + 14], fill=CAT[cat])
        d.text((x + 12, yy + 7), n, font=font("sb", 8), fill=(255, 255, 255), anchor="mm")
        for i, ln in enumerate(lines):
            d.text((tx, yy + i * 12), ln, font=f, fill=INK)
        yy += len(lines) * 12 + gap


def draw_briefs(y, h):
    n_b = len(BRIEFS)
    per = -(-n_b // 3)
    d.rectangle([10, y, 1014, y + 14], fill=INK)
    d.text((16, y + 7), "ALSO ON SATURDAY 21 NOVEMBER 2026 · %d MORE STORIES · ONE LINE EACH" % n_b, font=font("sb", 10), fill=(255, 255, 255), anchor="lm")
    cw = 1004 / 3
    rh = (h - 18) / per
    for i, b in enumerate(BRIEFS):
        col, row = divmod(i, per)
        x = 10 + col * cw + 4
        yy = y + 18 + row * rh
        n, cat, ck, tier, lead, txt = b[0], b[1], b[2], b[3], b[4], b[5]
        d.rectangle([x, yy + 1, x + 17, yy + 12], fill=CAT[cat])
        d.text((x + 9, yy + 6.5), str(n), font=font("sb", 9), fill=(255, 255, 255), anchor="mm")
        d.rectangle([x + 20, yy + 1, x + 23, yy + 12], fill=CHIP[ck][1])
        if tier == "F":
            d.rectangle([x + 25, yy + 1, x + 28, yy + 12], fill=INK)
        tx = x + 32
        f_b, f_r = font("sb", 11), font("s", 11)
        wl = tw(lead + " ", f_b)
        d.text((tx, yy), lead, font=f_b, fill=INK)
        d.text((tx + wl, yy), txt, font=f_r, fill=(50, 50, 56))
        if wl + tw(txt, f_r) > cw - 42:
            WARN.append("brief %d too wide by %d px" % (n, wl + tw(txt, f_r) - (cw - 42)))
        if row < per - 1:
            d.line([x + 32, yy + rh - 1, x + cw - 14, yy + rh - 1], fill=(214, 208, 192))


def draw_footer(y):
    d.rectangle([10, y, 1014, y + FOOT_H], fill=(252, 240, 238), outline=(190, 38, 30), width=2)
    d.text((16, y + 4), "DATE CHECK", font=font("sb", 10), fill=(190, 38, 30))
    end = para(92, y + 4, 916, "SAT = dated 21 Nov where it happened (rail times UTC) or due that day. FRI>SAT = dated Fri 20 Nov, still in Saturday's roundups. F1 lights-out: Sat 20:00 local = 04:00 UTC Sun. LEFT OUT as older: Russian missiles in Poland, Kyiv bridge strikes, Cyclone Akvan landfall (all Fri); ICJ Rohingya ruling, Trump–Xi Shenzhen summit (Thu 19); Rwanda return-hub plan (16 Nov); Eisenkot mandate, Task Force Iron Gate (7 Nov); Jericho shooting (~17 Nov); Zelenskyy in Canada (12 Sep). Unverified scores/prices omitted.", "s", 11, INK, lh=12, maxlines=5, tag="date")
    d.text((16, end + 1), "Sources: Al Jazeera, Anadolu Agency, ESA, USGS, Reuters, AFP, Euronews, SBS, Deccan Chronicle, Indian Opinion, ATP/TennisConnected. Claims are attributed. Art and map: original, drawn in code.", font=font("si", 11), fill=GREY)
    if end + 2 + 12 > y + FOOT_H:
        WARN.append("footer overflow")


ROW_H = (169, 143, 132)   # panel row heights (4 / 4 / 5 panels)
ART_H = (50, 38, 36)
FOOT_H = 62


def main(out_dir):
    draw_header()
    draw_legend()
    draw_kpis()
    top = draw_region_bar(184)
    x0, avail = 132, 882
    rows = [(HEROES + MIDS[:1], 4, 8), (MIDS[1:], 4, 8), (EXTRA, 5, 8)]
    # row 1: stories 1-4, row 2: stories 5-8, row 3: story 9 + promoted briefs
    row_y = top
    for ri, (items, cnt, g) in enumerate(rows):
        pw = (avail - (cnt - 1) * g) // cnt
        hs = 15 if ri == 0 else 13
        for i, s_ in enumerate(items):
            draw_panel(x0 + i * (pw + g), row_y, pw, ROW_H[ri], s_, ART_H[ri], hs, 2 if ri < 2 else 3, 4)
        row_y += ROW_H[ri] + 6
    draw_timeline(top, row_y - 6)
    ly = row_y + 2
    per = -(-len(BRIEFS) // 3)
    brief_h = 18 + per * 13 + 2
    foot_y = H - 6 - FOOT_H - 1
    by = foot_y - 6 - brief_h
    lh = by - 6 - ly
    print("layout: top=%d ly=%d lh=%d by=%d brief_h=%d foot_y=%d" % (top, ly, lh, by, brief_h, foot_y))
    draw_map(10, ly, 560, lh)
    draw_dev(578, ly, 436, lh)
    draw_briefs(by, brief_h)
    draw_footer(foot_y)
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, "entry.png"), optimize=True)
    print("regions:", REG_COUNTS)
    print("panel slack:", PANEL_SLACK)
    for w_ in WARN:
        print("WARN", w_)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
