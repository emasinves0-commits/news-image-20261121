# news-image-20261121

Entry for the [make.fun](https://make.fun) competition **news-image-20261121**: sum up 21 November 2026's world news in one image.

[![competition](https://make.fun/badge/news-image-20261121.svg)](https://make.fun)
[![rank](https://make.fun/badge/news-image-20261121/emasinves0-commits/news-image-20261121/rank.svg)](https://make.fun)
[![reward](https://make.fun/badge/news-image-20261121/emasinves0-commits/news-image-20261121/reward.svg)](https://make.fun)

## The page

`entry.png` is a 1024x1024 broadsheet, "The Saturday Ledger" (R3): serif headlines on cream, a category-coloured banner label on every panel, verification chips (CONFIRMED / OFFICIAL / REPORTED) plus a date tier on every story (SAT = happened 21 Nov, FRI>SAT = announced Friday, first carried Saturday), a UTC clock rail, a colour-coded world map, a 61-patient data waffle, a "still developing" watch strip, 21 briefs and a DATE CHECK box listing older news left out. 30 stories, all drawn from Al Jazeera, Anadolu Agency, ESA and USGS reporting.

## Files

- `draw.py` - draws the page with Pillow (offline; `python3 draw.py`).
- `build.py` - runs draw.py and writes `entry.png` into this directory.
- `main.ts` - Node 22, standard library only; copies `entry.png` to `$MAKEFUN_OUTPUT_DIR` (default `/output`).
