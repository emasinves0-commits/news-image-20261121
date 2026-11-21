# news-image-20261121

Entry for the [make.fun](https://make.fun) competition **news-image-20261121**: sum up 21 November 2026's world news in one image.

[![competition](https://make.fun/badge/news-image-20261121.svg)](https://make.fun)
[![rank](https://make.fun/badge/news-image-20261121/emasinves0-commits/news-image-20261121/rank.svg)](https://make.fun)
[![reward](https://make.fun/badge/news-image-20261121/emasinves0-commits/news-image-20261121/reward.svg)](https://make.fun)

## The page

`entry.png` is a 1024x1024 broadsheet, "The Saturday Ledger" (R4): serif headlines on cream, a category-coloured banner label on every panel, verification chips (CONFIRMED / OFFICIAL / REPORTED) plus a date tier on every story (SAT = dated 21 Nov where it happened or due that day, FRI>SAT = dated Friday, still carried Saturday), a UTC clock rail with a "now" marker, a colour-coded world map with zoomed Europe and Middle East insets, 13 full illustrated panels, a "still developing" watch list, 27 one-line briefs and a DATE CHECK box listing older news left out. **40 stories** (R3: 30), compiled 07:15 UTC from Al Jazeera, Anadolu, ESA, USGS, Euronews, SBS, Deccan Chronicle, Indian Opinion and ATP/TennisConnected reporting.

### R4 vote fix (21 Nov, 2 GO vs 3 NO-GO)

- Body text: every hero/mid panel, brief, watch item, rail label, legend, KPI caption and the DATE CHECK box is now **>= 11px** (was 10px). Only chips (8px), pin numbers, art captions, banner/section header bars (10px bold) stay small.
- Panels: **13 full illustrated panels**, each with a bold category banner and its own art, in three rows (4 / 4 / 5). Story 9 (pancreatic cancer trial) became an illustrated panel whose data is one 61-cell row, replacing the big waffle panel; four briefs were promoted to panels: 10 Lufthansa (plane), 15 Christie's/Kahlo (painting), 33 ATP Turin (court), 35 F1 Las Vegas (street circuit). Briefs: 27 remain; total still **40 stories** (13 + 27).
- Text trimmed (not shrunk) where 11px did not fit; the map is now a single row (world + Europe and Middle East insets side by side) and the watch list is wider.
- Unchanged: SAT vs FRI>SAT chip on every panel, DATE CHECK box with the left-out list, UTC rail, numbered map pins with leader lines, 7-item watch strip, top data strip, region counts, deterministic build (two renders byte-identical), `main.ts` only copies `entry.png`.

### R4 notes (vs R3)

- Stories 30 -> 40: ten new briefs (31-40). Saturday-dated: Ladakh local polls, S. Korea CSAT cheating count (111), ATP Finals semi (Alcaraz v Shelton), Premier League matchday 11 fixtures, F1 Las Vegas GP (Sat 20:00 local = 04:00 UTC Sun), coalition strikes on Houthi targets (headline-level only). FRI>SAT chips: US Senate energy-permitting bill, Iraqi forces at Jurf al-Sakhar, Myanmar/China objection to the ICJ ruling, Villepin's 2027 bid.
- Map: Europe and Middle East pins moved into zoomed insets; every pin is pushed apart by a deterministic repulsion step with a leader line to the true location (no overlaps).
- Text: body copy raised to >= 10px here, then >= 11px in the vote fix above.
- Watch list: one more item and justified spacing, so no empty block.
- Verification: items that could not be dated to Saturday (Arab News homepage listing mixed old stories; Nikhil Gupta sentence, KL Rahul century, Wall Street close, Rwanda hub, Task Force Iron Gate) were dropped or moved to DATE CHECK.

## Files

- `draw.py` - draws the page with Pillow (offline; `python3 draw.py`).
- `build.py` - runs draw.py and writes `entry.png` into this directory.
- `main.ts` - Node 22, standard library only; copies `entry.png` to `$MAKEFUN_OUTPUT_DIR` (default `/output`).
