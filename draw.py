"""make.fun news page, Saturday 21 November 2026: "The Saturday Ledger" R3 (1024x1024).

Fresh design: cream broadsheet, serif headlines, category-coloured banner labels on every panel,
verification chips (CONFIRMED / OFFICIAL / REPORTED), a date-tier tag on every story
(SAT = happened 21 Nov, FRI>SAT = announced Friday, first carried Saturday), a UTC clock rail,
a colour-coded map, a 61-patient data waffle and a DEVELOPING watch strip.
Pure PIL, no network, no randomness.  Usage: python3 draw.py [output_dir]
"""
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
CATNAME = {"WAR": "Conflict & security", "POL": "Politics & diplomacy", "SCI": "Climate, science & health",
           "ECO": "Business & tech", "SOC": "Society & culture", "SPT": "Sport"}
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


def fit_text(x, y, w, t, fk, fs, fill, anchor="la"):
    while tw(t, font(fk, fs)) > w and fs > 6:
        fs -= 1
    d.text((x, y), t, font=font(fk, fs), fill=fill, anchor=anchor)


def chip(x, y, kind, tier=None):
    """Verification chip + date tier. Returns right edge."""
    name, col = CHIP[kind]
    f = font("sb", 7)
    w = int(tw(name, f)) + 8
    d.rounded_rectangle([x, y, x + w, y + 10], 2, fill=col)
    d.text((x + 4, y + 1), name, font=f, fill=(255, 255, 255))
    x2 = x + w + 3
    if tier:
        t = "SAT" if tier == "S" else "FRI>SAT"
        tc = (30, 30, 34)
        w2 = int(tw(t, f)) + 8
        d.rounded_rectangle([x2, y, x2 + w2, y + 10], 2, outline=tc, width=1)
        d.text((x2 + 4, y + 1), t, font=f, fill=tc)
        x2 += w2 + 3
    return x2


def banner(x, y, w, h, cat, label, num):
    c = CAT[cat]
    d.rectangle([x, y, x + w, y + h], fill=c)
    d.rectangle([x, y, x + h, y + h], fill=INK)
    d.text((x + h / 2, y + h / 2), str(num), font=font("sb", h - 7), fill=(255, 255, 255), anchor="mm")
    fit_text(x + h + 5, y + h / 2, w - h - 8, label, "sb", h - 8, (255, 255, 255), anchor="lm")


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
    d.ellipse([x + 14, y + 8, x + 14 + 62, y + 8 + 62], fill=(52, 118, 190))
    d.polygon([(x + 26, y + 22), (x + 44, y + 16), (x + 52, y + 30), (x + 38, y + 44), (x + 24, y + 38)], fill=(70, 150, 90))
    d.polygon([(x + 50, y + 46), (x + 64, y + 42), (x + 66, y + 56), (x + 54, y + 60)], fill=(70, 150, 90))
    # thermometer
    d.rounded_rectangle([x + 96, y + 8, x + 106, y + 56], 5, fill=(255, 255, 255), outline=INK)
    d.rectangle([x + 99, y + 24, x + 103, y + 56], fill=(200, 40, 30))
    d.ellipse([x + 93, y + 52, x + 109, y + 68], fill=(200, 40, 30), outline=INK)
    # clock showing overtime
    cx, cy = x + w - 52, y + 38
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=(255, 255, 255), outline=INK, width=2)
    d.line([cx, cy, cx, cy - 20], fill=INK, width=2)
    d.line([cx, cy, cx + 14, cy + 6], fill=(200, 40, 30), width=2)
    d.text((x + 120, y + 70), "DAY 13 · NO DEAL", font=font("sb", 9), fill=INK)
    fit_text(x + 120, y + 14, 80, "talks past", "si", 9, GREY)
    fit_text(x + 120, y + 26, 80, "deadline", "si", 9, GREY)


def art_saudi(x, y, w, h):
    sky(x, y, w, h, (14, 22, 52), (52, 40, 70))
    skyline(x, y + 12, w, h - 12, (24, 30, 58), seed=7)
    import math
    for i, (sx, sy) in enumerate([(20, 8), (88, 4), (150, 10)]):
        ex, ey = x + sx + 60, y + 38 + i * 4
        d.line([x + sx, y + sy, ex, ey], fill=(255, 200, 90), width=2)
        burst(ex, ey, 9)
    d.text((x + w - 6, y + h - 4), "RIYADH 3 · JAZAN 2", font=font("sb", 8), fill=(255, 255, 255), anchor="rb")


def art_mercury(x, y, w, h):
    sky(x, y, w, h, (8, 10, 26), (20, 22, 48))
    for k in range(18):
        d.point((x + (k * 37) % w, y + (k * 19) % h), fill=(255, 255, 255))
        d.rectangle([x + (k * 53) % w, y + (k * 29) % h, x + (k * 53) % w + 1, y + (k * 29) % h + 1], fill=(200, 200, 230))
    cx, cy = x + w - 70, y + h // 2 + 6
    d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=(150, 144, 138))
    for (a, b, r) in [(-12, -8, 7), (8, 10, 5), (-4, 14, 4), (14, -14, 4)]:
        d.ellipse([cx + a - r, cy + b - r, cx + a + r, cy + b + r], outline=(106, 100, 96), width=2)
    d.arc([cx - 58, cy - 46, cx + 58, cy + 46], 120, 330, fill=(255, 220, 120), width=1)
    sx, sy = x + 52, y + 36
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


# ------------------------------------------------------------------ content
STORIES = {
    # n: (cat, region, city, lon, lat, chip, tier)
}

HEROES = [
    dict(n=1, cat="SCI", label="CLIMATE · ANTALYA, TÜRKIYE", art=art_cop, chip="C", tier="S",
         hl="COP31 runs past its deadline with no deal",
         body="Fossil-fuel deadlock pushed the UN climate summit into overtime. Portugal's environment minister told Anadolu a final text could land late Friday or early Saturday; the draft was reported to omit fossil-fuel language. (AJ, Anadolu)"),
    dict(n=2, cat="WAR", label="WAR · RIYADH & JAZAN, SAUDI ARABIA", art=art_saudi, chip="C", tier="S",
         hl="Five Houthi missiles intercepted over Saudi Arabia",
         body="The Saudi-led coalition said it shot down three ballistic missiles aimed at Riyadh early Saturday, and two aimed at Jazan; debris fell at Al Shuqaiq, no casualties reported. (Al Jazeera, Anadolu)"),
    dict(n=3, cat="SCI", label="SPACE · MERCURY ORBIT", art=art_mercury, chip="O", tier="S",
         hl="BepiColombo due to enter Mercury orbit tonight",
         body="ESA says its four thrusters fire at 19:24 CET (18:24 UTC) to brake the probe after 8 years and nearly 10 billion km. Only the second mission to orbit Mercury; science starts April 2027. (ESA via Anadolu)"),
]

MIDS = [
    dict(n=4, cat="SCI", label="QUAKE · JUNÍN, PERU", art=art_quake, chip="O", tier="S",
         hl="Magnitude 6.7 quake strikes central Peru",
         body="Epicentre near Ondores, Junín region, at 00:09 UTC. No tsunami threat; no casualties or major damage reported. (USGS data)"),
    dict(n=5, cat="WAR", label="IRAN · STRAIT OF HORMUZ", art=art_hormuz, chip="R", tier="S",
         hl="IRGC claims it downed a US drone",
         body="Revolutionary Guards say they shot it down over Hormuz; no confirmation. Iran also denied a strike on Qeshm Island. (Al Jazeera, Anadolu)"),
    dict(n=6, cat="POL", label="US–IRAN · WASHINGTON", art=art_trump_iran, chip="R", tier="F",
         hl="Trump warns Iran: “we're going to fight”",
         body="Over a rumoured plot against Washington, he said “If they do, we're going to fight.” Cited no evidence in public. (Anadolu)"),
    dict(n=7, cat="POL", label="DIPLOMACY · COPENHAGEN", art=art_denmark, chip="C", tier="F",
         hl="Denmark expels Russian defence attaché",
         body="Given seven days to leave. Two Danes charged over a foiled plot to kill a Ukrainian rapper; Moscow calls it “vengeful”. (AJ, Anadolu)"),
    dict(n=8, cat="ECO", label="TECH · NVIDIA / US", art=art_chip, chip="C", tier="F",
         hl="Trump wants Nvidia's Huang back",
         body="Said he'd “love to see Jensen be given a second chance”; board chair says no reinstatement after his 12 Nov exit. (Al Jazeera)"),
]

# briefs: (n, cat, chip, tier, bold lead, text, city, lon, lat)
BRIEFS = [
    (10, "ECO", "R", "S", "Lufthansa", "to cut 1,000 full-time jobs at its Frankfurt and Munich hubs and trim short-haul capacity.", 8.7, 50.1),
    (11, "ECO", "R", "S", "Japan–Saudi", "oil deal: Japan to buy up to 8m barrels for its reserve; Saudis get use of 16m barrels of storage.", 139.7, 35.7),
    (12, "ECO", "R", "S", "Angola's Endiama", "to pay $180m for a 10% stake in De Beers, its CEO says, despite weak diamond prices.", 13.2, -8.8),
    (13, "SPT", "O", "S", "UEFA fines England's FA €15,000", "over fans' chants at the 3–2 win over Spain in Madrid.", 6.2, 46.4),
    (14, "SPT", "O", "S", "FIA to hire full-time F1 stewards", "from 2027; long-term goal 12–15 stewards.", 2.3, 48.9),
    (15, "SOC", "R", "S", "Christie's pulls Frida Kahlo painting", "(est. $2.5–3.5m) after Mexico queries its provenance.", -74.0, 40.7),
    (16, "ECO", "R", "S", "Signal limits screenshots on mobile", "to stop OS-level AI assistants capturing private chats.", -122.4, 37.8),
    (17, "POL", "R", "S", "Newsom's office floats emergency powers", "to shut down AI models posing an imminent catastrophic threat; needs lawmakers.", -121.5, 38.6),
    (18, "WAR", "R", "S", "UK military confirms", "its National Cyber Force runs offensive cyber operations against Russia, China, Iran, N. Korea.", -0.1, 51.5),
    (19, "ECO", "R", "S", "US holds first offshore minerals lease sale", "off American Samoa: $6m in high bids from one bidder.", -170.7, -14.3),
    (20, "SOC", "R", "S", "Seoul: Lee orders exam overhaul", "after cheating with AI and banned devices.", 127.0, 37.5),
    (21, "POL", "R", "S", "Iran's Araghchi:", "US naval blockade must lift before oil exports resume.", 51.4, 35.7),
    (22, "POL", "R", "F", "Qatar pledges €15bn more", "for Germany; Merz thanks it for mediating in the US–Iran war.", 13.4, 52.5),
    (23, "POL", "R", "F", "EU–UK summit in Brussels", "deepens security, defence, youth-mobility and migration ties.", 4.35, 50.85),
    (24, "SOC", "C", "F", "Paris court sentences 3 officers", "to 5 years each (3–4 suspended) for 2020 beating of Michel Zecler; racism an aggravating factor.", 2.35, 48.85),
    (25, "WAR", "R", "S", "FBI probes apparent breach", "of the national NCIC criminal-records database.", -77.0, 38.9),
    (26, "POL", "R", "S", "US lawmakers urge ban", "on Chinese AI models in federal systems.", -77.05, 38.85),
    (27, "SOC", "O", "S", "Education Cannot Wait: $52m", "for 300,000+ children hit by crises in Lebanon, Myanmar, South Sudan.", 35.5, 33.9),
    (28, "WAR", "R", "S", "Sudan: army says", "it is restoring security in Blue Nile state.", 34.3, 11.8),
    (29, "ECO", "R", "S", "Airbnb bans hosts", "from requiring guests to do chores, for bookings from 20 Nov.", -122.4, 37.77),
    (30, "SOC", "R", "S", "Petition tops 20,000", "to drop Marilyn Manson from a Wembley show; he denies abuse claims.", -0.28, 51.55),
]

# pins for hero/mid stories: n -> (lon, lat)
PINS = {1: (30.7, 36.9), 2: (46.7, 24.7), 3: None, 4: (-75.5, -11.0), 5: (56.3, 26.6), 6: (-77.0, 38.9),
        7: (12.6, 55.7), 8: (-121.9, 37.4), 9: None}
CATS_BY_N = {h["n"]: h["cat"] for h in HEROES + MIDS}
CATS_BY_N[9] = "SCI"
for b in BRIEFS:
    CATS_BY_N[b[0]] = b[1]
    PINS[b[0]] = (b[6], b[7])


# ------------------------------------------------------------------ drawing
def rule(x1, y1, x2, y2, w=1, c=RULE):
    d.line([x1, y1, x2, y2], fill=c, width=w)


def draw_header():
    fit_text(10, 6, 700, "THE SATURDAY LEDGER  ·  ONE PAGE, ONE DAY, EVERY ITEM SOURCED", "sb", 9, (170, 30, 20))
    fit_text(1014, 6, 500, "COMPILED 06:40 UTC · SAT 21 NOV 2026 · 30 STORIES · 6 REGIONS", "sb", 9, INK, anchor="ra")
    rule(10, 19, 1014, 19, 2)
    fit_text(512, 21, 1004, "Saturday 21 November 2026", "xb", 66, INK, anchor="ma")
    rule(10, 92, 1014, 92, 1)
    fit_text(512, 95, 1004,
             "COP31 runs past its deadline  ·  Five Houthi missiles shot down over Saudi Arabia  ·  BepiColombo due at Mercury tonight",
             "xi", 17, (150, 30, 20), anchor="ma")
    rule(10, 118, 1014, 118, 2)


def draw_legend():
    y = 122
    d.text((10, y + 1), "HOW TO READ:", font=font("sb", 8), fill=INK)
    x = 82
    for k in "COR":
        x = chip(x, y, k) + 2
        expl = {"C": "two+ outlets agree", "O": "agency / institution data", "R": "single source or a claim"}[k]
        d.text((x, y + 1), expl, font=font("s", 8), fill=GREY)
        x += tw(expl, font("s", 8)) + 12
    f = font("sb", 7)
    for tag, txt in (("SAT", "happened 21 Nov"), ("FRI>SAT", "announced Fri, first carried Sat")):
        w = int(tw(tag, f)) + 8
        d.rounded_rectangle([x, y, x + w, y + 10], 2, outline=INK)
        d.text((x + 4, y + 1), tag, font=f, fill=INK)
        d.text((x + w + 4, y + 1), txt, font=font("s", 8), fill=GREY)
        x += w + 4 + tw(txt, font("s", 8)) + 10
    rule(10, 136, 1014, 136, 1)


def draw_kpis():
    cells = [("3 + 2", "missiles intercepted:\nRiyadh + Jazan", CAT["WAR"]),
             ("6.7", "magnitude of the\nPeru quake, 00:09 UTC", CAT["SCI"]),
             ("18:24", "UTC: BepiColombo's\nMercury orbit burn", CAT["SCI"]),
             ("37 / 61", "advanced pancreatic\ncancer patients: tumours shrank", CAT["SCI"]),
             ("1,000", "Lufthansa hub jobs\nto go", CAT["ECO"]),
             ("€15bn", "Qatar's new pledge\nfor Germany", CAT["POL"])]
    cw = 1004 / 6
    for i, (big, small, col) in enumerate(cells):
        x = 10 + i * cw
        d.rectangle([x + 2, 141, x + 5, 184], fill=col)
        fit_text(x + 10, 139, cw - 14, big, "xb", 28, INK)
        lines = small.split("\n")
        d.text((x + 10, 170), lines[0], font=font("s", 8), fill=GREY)
        d.text((x + 10, 178), lines[1], font=font("s", 8), fill=GREY)
    rule(10, 190, 1014, 190, 1)


def region_of(n):
    ll = PINS.get(n)
    if n == 3:
        return "SPACE / GLOBAL"
    if ll is None:
        return "SPACE / GLOBAL"
    lon, lat = ll
    if lon < -150:
        return "ASIA-PACIFIC"
    if lon < -30:
        return "AMERICAS"
    if 34 <= lon <= 62 and 12 <= lat <= 36:
        return "MIDDLE EAST"
    if lon > 62 or lon < -150:
        return "ASIA-PACIFIC"
    if lat < 25 and lon < 52:
        return "AFRICA"
    return "EUROPE"


REGCOL = {"MIDDLE EAST": (190, 38, 30), "EUROPE": (30, 78, 160), "AMERICAS": (118, 60, 150),
          "ASIA-PACIFIC": (0, 128, 140), "AFRICA": (28, 126, 82), "SPACE / GLOBAL": (60, 60, 70)}


def draw_region_bar():
    counts = {}
    for n in list(range(1, 31)):
        counts[region_of(n)] = counts.get(region_of(n), 0) + 1
    order = sorted(counts, key=lambda k: -counts[k])
    tot = sum(counts.values())
    x = 10
    for name in order:
        n = counts[name]
        w = int(1004 * n / tot)
        d.rectangle([x, 193, x + w - 2, 205], fill=REGCOL[name])
        fit_text(x + w / 2, 194, w - 6, "%s %d" % (name, n), "sb", 9, (255, 255, 255), anchor="ma")
        x += w
    return 208


def draw_timeline(y0, y1):
    x0, x1 = 10, 112
    d.rectangle([x0, y0, x1, y1], fill=(236, 230, 214), outline=INK)
    d.rectangle([x0, y0, x1, y0 + 16], fill=INK)
    d.text(((x0 + x1) / 2, y0 + 8), "THE DAY · UTC", font=font("sb", 9), fill=(255, 255, 255), anchor="mm")
    # axis 00..24 mapped over y0+30..y1-14
    ay0, ay1 = y0 + 30, y1 - 26
    ax = x0 + 20

    def ty(h):
        return ay0 + (ay1 - ay0) * h / 24.0

    d.line([ax, ay0, ax, ay1], fill=INK, width=2)
    for h in range(0, 25, 3):
        d.line([ax - 4, ty(h), ax + 4, ty(h)], fill=INK)
        d.text((x0 + 2, ty(h) - 4), "%02d" % h, font=font("sb", 8), fill=INK)
    ev = [(0.15, "4", "SCI", "00:09 Peru quake"),
          (2.0, "2", "WAR", "Early: Riyadh + Jazan intercepts"),
          (4.5, "7", "POL", "AM: Denmark, Trump items carried"),
          (6.67, "NOW", None, "06:40 compiled"),
          (12.0, "1", "SCI", "COP31 text due (expected)"),
          (18.4, "3", "SCI", "18:24 BepiColombo burn")]
    for h, n, cat, txt in ev:
        y = ty(h)
        if n == "NOW":
            d.polygon([(ax - 7, y), (ax + 1, y - 5), (ax + 1, y + 5)], fill=(190, 38, 30))
            d.line([ax, y, x1 - 4, y], fill=(190, 38, 30), width=1)
            d.text((ax + 6, y - 11), txt, font=font("sb", 8), fill=(190, 38, 30))
            continue
        c = CAT[cat]
        future = h > 6.7
        if future:
            d.ellipse([ax - 5, y - 5, ax + 5, y + 5], fill=PAPER, outline=c, width=2)
        else:
            d.ellipse([ax - 5, y - 5, ax + 5, y + 5], fill=c)
        para(ax + 9, y - 6, x1 - ax - 12, txt, "s", 8, INK, lh=9, maxlines=3, tag="tl")
    # past/future legend
    d.text((x0 + 4, y1 - 20), "solid = happened", font=font("s", 7), fill=GREY)
    d.text((x0 + 4, y1 - 11), "ring = scheduled", font=font("s", 7), fill=GREY)


def draw_hero(x, y, w, h, s):
    banner(x, y, w, 18, s["cat"], s["label"], s["n"])
    d.rectangle([x, y + 18, x + w, y + h], outline=INK)
    s["art"](x + 1, y + 19, w - 1, 78)
    chip(x + 6, y + 101, s["chip"], s["tier"])
    ty = para(x + 6, y + 114, w - 12, s["hl"], "xb", 18, INK, lh=20, maxlines=3, tag="hero" + str(s["n"]))
    para(x + 6, ty + 3, w - 12, s["body"], "s", 11, (40, 40, 46), lh=13, maxlines=7, tag="herobody" + str(s["n"]))


def draw_mid(x, y, w, h, s):
    banner(x, y, w, 16, s["cat"], s["label"], s["n"])
    d.rectangle([x, y + 16, x + w, y + h], outline=INK)
    s["art"](x + 1, y + 17, w - 1, 42)
    chip(x + 4, y + 62, s["chip"], s["tier"])
    ty = para(x + 4, y + 75, w - 8, s["hl"], "xb", 13, INK, lh=14, maxlines=3, tag="mid" + str(s["n"]))
    para(x + 4, ty + 2, w - 8, s["body"], "s", 9, (40, 40, 46), lh=10, maxlines=6, tag="midbody" + str(s["n"]))


def draw_map(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=INK)
    d.rectangle([x, y, x + w, y + 14], fill=INK)
    d.text((x + 5, y + 7), "WHERE IT HAPPENED · pin colour = beat", font=font("sb", 8), fill=(255, 255, 255), anchor="lm")
    mx, my, mw, mh = x + 2, y + 16, w - 4, h - 32

    def P(lon, lat):
        return (mx + (lon + 180) / 360.0 * mw, my + (82 - lat) / 140.0 * mh)

    land = [
        [(-168, 66), (-140, 70), (-100, 72), (-80, 70), (-60, 52), (-66, 44), (-80, 32), (-82, 25), (-97, 26), (-105, 22), (-117, 32), (-124, 40), (-125, 49), (-140, 60), (-165, 60)],
        [(-80, 9), (-60, 10), (-35, -6), (-40, -22), (-58, -38), (-68, -54), (-74, -45), (-71, -20), (-81, -5)],
        [(-55, 60), (-20, 70), (-22, 80), (-60, 82), (-70, 76)],
        [(-10, 36), (-9, 44), (-2, 49), (5, 54), (10, 58), (20, 70), (30, 70), (40, 62), (40, 46), (28, 41), (22, 36), (12, 38), (3, 38)],
        [(-17, 15), (-16, 28), (-6, 36), (10, 37), (32, 31), (43, 12), (51, 11), (40, -15), (33, -28), (20, -35), (12, -18), (9, 4), (-8, 5)],
        [(28, 41), (40, 46), (60, 55), (70, 72), (110, 76), (150, 70), (180, 68), (165, 58), (142, 52), (135, 36), (122, 30), (122, 22), (108, 10), (100, 3), (92, 20), (78, 8), (68, 24), (56, 27), (50, 14), (43, 12), (34, 30), (36, 38)],
        [(114, -22), (130, -12), (142, -11), (153, -27), (146, -39), (130, -32), (115, -34)],
        [(95, 5), (105, -6), (120, -9), (108, -6), (98, 3)],
        [(129, 33), (141, 42), (145, 44), (136, 34)],
    ]
    for poly in land:
        d.polygon([P(*p) for p in poly], fill=LAND, outline=(170, 150, 112))
    pinsl = []
    for n, ll in PINS.items():
        if ll is None:
            continue
        pinsl.append((n, P(*ll), CAT[CATS_BY_N[n]]))
    # nudge overlaps
    placed = []
    for n, (px, py), c in pinsl:
        for (qx, qy) in placed:
            if abs(px - qx) < 8 and abs(py - qy) < 8:
                px += 7
                py += 5
        placed.append((px, py))
        r = 5
        d.ellipse([px - r, py - r, px + r, py + r], fill=c, outline=(255, 255, 255))
        d.text((px, py), str(n), font=font("sb", 6), fill=(255, 255, 255), anchor="mm")
    # space pins
    d.rounded_rectangle([x + 4, y + h - 15, x + 100, y + h - 3], 3, fill=(20, 24, 50))
    d.ellipse([x + 7, y + h - 14, x + 17, y + h - 4], fill=CAT["SCI"])
    d.text((x + 12, y + h - 9), "3", font=font("sb", 6), fill=(255, 255, 255), anchor="mm")
    d.text((x + 21, y + h - 9), "space: Mercury", font=font("sb", 7), fill=(255, 255, 255), anchor="lm")
    # legend
    lx = x + 106
    for cat in ["WAR", "POL", "SCI", "ECO", "SOC", "SPT"]:
        d.ellipse([lx, y + h - 13, lx + 7, y + h - 6], fill=CAT[cat])
        short = {"WAR": "conflict", "POL": "politics", "SCI": "science", "ECO": "business", "SOC": "society", "SPT": "sport"}[cat]
        d.text((lx + 9, y + h - 9), short, font=font("s", 7), fill=INK, anchor="lm")
        lx += 10 + tw(short, font("s", 7)) + 2


def draw_waffle(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 250, 244), outline=INK)
    banner(x, y, w, 15, "SCI", "DATA · PANCREATIC CANCER PILL TRIAL", 9)
    para(x + 5, y + 19, w - 10, "Daraxonrasib + chemotherapy, early trial of 61 patients with advanced disease.", "xb", 11, INK, lh=12, maxlines=3, tag="wf")
    gx, gy = x + 6, y + 48
    cell = 10
    cols = 10
    green, light = (28, 126, 82), (205, 214, 206)
    for i in range(61):
        r, c = divmod(i, cols)
        if i < 5:
            col = (14, 80, 52)
        elif i < 37:
            col = green
        else:
            col = light
        d.rectangle([gx + c * (cell + 2), gy + r * (cell + 2), gx + c * (cell + 2) + cell, gy + r * (cell + 2) + cell], fill=col)
    lx = gx + cols * 12 + 8
    d.text((lx, gy - 2), "60.7%", font=font("xb", 26), fill=green)
    para(lx, gy + 26, x + w - lx - 4, "tumours shrank (37 of 61)", "sb", 9, INK, lh=10)
    d.rectangle([lx, gy + 50, lx + 8, gy + 58], fill=(14, 80, 52))
    para(lx + 12, gy + 49, x + w - lx - 16, "5 had no detectable tumour", "s", 8, INK, lh=9)
    d.rectangle([lx, gy + 64, lx + 8, gy + 72], fill=light)
    para(lx + 12, gy + 63, x + w - lx - 16, "no shrinkage", "s", 8, INK, lh=9)
    chip(lx, gy + 78, "R", "S")
    d.text((x + 5, y + h - 11), "Researchers: larger studies needed. (Anadolu)", font=font("si", 8), fill=GREY)


def draw_dev(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 250, 240), outline=(190, 38, 30), width=2)
    d.rectangle([x, y, x + w, y + 15], fill=(190, 38, 30))
    d.ellipse([x + 5, y + 4, x + 12, y + 11], fill=(255, 255, 255))
    d.text((x + 17, y + 8), "STILL DEVELOPING AT 06:40 UTC · WHAT WE'RE WATCHING", font=font("sb", 9), fill=(255, 255, 255), anchor="lm")
    items = [("1", "SCI", "COP31 final text: a third draft was promised; adoption not yet confirmed."),
             ("3", "SCI", "BepiColombo burn at 18:24 UTC: success is not known until after the manoeuvre."),
             ("2", "WAR", "Houthi–Saudi exchange: both sides have threatened key ports; coalition counts are its own."),
             ("5", "WAR", "Hormuz: IRGC's drone claim has no independent confirmation yet."),
             ("7", "POL", "Denmark–Russia: Moscow promises an “appropriate response” to the expulsion."),
             ("4", "SCI", "Peru quake: no casualties reported so far; early figures can change."),
             ("25", "WAR", "FBI database breach is only “apparent” so far; scope unconfirmed.")]
    yy = y + 19
    for n, cat, t in items:
        d.ellipse([x + 5, yy, x + 15, yy + 10], fill=CAT[cat])
        d.text((x + 10, yy + 5), n, font=font("sb", 7), fill=(255, 255, 255), anchor="mm")
        yy = para(x + 20, yy - 1, w - 26, t, "s", 9, INK, lh=10, maxlines=2, tag="dev") + 4


def draw_briefs(y, h):
    d.rectangle([10, y, 1014, y + 14], fill=INK)
    d.text((16, y + 7), "ALSO ON SATURDAY 21 NOVEMBER 2026 · 21 MORE STORIES", font=font("sb", 9), fill=(255, 255, 255), anchor="lm")
    cw = 1004 / 3
    per = 7
    for i, b in enumerate(BRIEFS):
        col, row = divmod(i, per)
        x = 10 + col * cw + 4
        yy = y + 18 + row * ((h - 18) / per)
        n, cat, ck, tier, lead, txt = b[0], b[1], b[2], b[3], b[4], b[5]
        c = CAT[cat]
        d.rectangle([x, yy + 1, x + 17, yy + 11], fill=c)
        d.text((x + 9, yy + 6), str(n), font=font("sb", 8), fill=(255, 255, 255), anchor="mm")
        cc = CHIP[ck][1]
        d.rectangle([x + 20, yy + 1, x + 23, yy + 11], fill=cc)  # verification colour tick
        if tier == "F":
            d.rectangle([x + 25, yy + 1, x + 28, yy + 11], fill=INK)
        tx = x + 32
        f_b, f_r = font("sb", 9), font("s", 9)
        mw = cw - 42
        words = [(wd, True) for wd in lead.split()] + [(wd, False) for wd in txt.split()]
        cx, cy = tx, yy
        lines = 1
        for wd, bold in words:
            f = f_b if bold else f_r
            ww = tw(wd + " ", f)
            if cx + ww - tx > mw:
                cx = tx
                cy += 10
                lines += 1
            d.text((cx, cy), wd, font=f, fill=INK if bold else (50, 50, 56))
            cx += ww
        if lines > 2:
            WARN.append(f"brief {n}: {lines} lines")
        if row < per - 1:
            d.line([x + 32, yy + (h - 18) / per - 2, x + cw - 14, yy + (h - 18) / per - 2], fill=(210, 204, 188))


def draw_footer(y):
    d.rectangle([10, y, 1014, y + 40], fill=(252, 240, 238), outline=(190, 38, 30), width=2)
    d.text((16, y + 4), "DATE CHECK", font=font("sb", 9), fill=(190, 38, 30))
    para(76, y + 3, 932, "Tagged SAT: happened on 21 Nov (UTC) or is scheduled for it. Tagged FRI>SAT: announced Friday 20 Nov, first carried by Saturday's morning wires. LEFT OUT as older news: Russian missiles in Poland and the Kyiv bridge strikes (Fri), Cyclone Akvan landfall (Fri), ICJ Myanmar ruling (Thu 19), Israel's Eisenkot mandate (7 Nov), Trump–Xi Shenzhen summit (Thu 19). Unverified sports scores and market prices are omitted rather than guessed.", "s", 8, INK, lh=9, maxlines=4, tag="date")
    d.text((16, y + 30), "Sources: Al Jazeera, Anadolu Agency, ESA, USGS, Reuters, AFP, Climate Action, RTÉ. Claims are attributed, not stated as fact. Art and map: original, drawn in code.", font=font("si", 8), fill=GREY)


def main(out_dir):
    draw_header()
    draw_legend()
    draw_kpis()
    top = draw_region_bar()
    # body
    hero_y, hero_h = top, 224
    mid_y = hero_y + hero_h + 6
    mid_h = 168
    draw_timeline(top, mid_y + mid_h)
    x0, avail = 120, 894
    gap = 9
    hw = (avail - 2 * gap) // 3
    for i, s in enumerate(HEROES):
        draw_hero(x0 + i * (hw + gap), hero_y, hw, hero_h, s)
    gap2 = 8
    mw = (avail - 4 * gap2) // 5
    for i, s in enumerate(MIDS):
        draw_mid(x0 + i * (mw + gap2), mid_y, mw, mid_h, s)
    ly = mid_y + mid_h + 8
    lh = 168
    draw_map(10, ly, 330, lh)
    draw_waffle(348, ly, 270, lh)
    draw_dev(626, ly, 388, lh)
    by = ly + lh + 8
    draw_briefs(by, 1010 - 48 - by - 4)
    draw_footer(1024 - 8 - 41 - 1)
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, "entry.png"), optimize=True)
    for w_ in WARN:
        print("WARN", w_)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
