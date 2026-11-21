# news-image-20261121

Entry for the [make.fun](https://make.fun) competition **news-image-20261121**: sum up 21 November 2026's world news in one image.

[![competition](https://make.fun/badge/news-image-20261121.svg)](https://make.fun)
[![rank](https://make.fun/badge/news-image-20261121/emasinves0-commits/news-image-20261121/rank.svg)](https://make.fun)
[![reward](https://make.fun/badge/news-image-20261121/emasinves0-commits/news-image-20261121/reward.svg)](https://make.fun)

## The poster

`entry.png` is a 1024x1024 "Saturday Atlas" broadsheet poster: pure white page, ink-black bold sans type, signal-red accents and thin black rules. It carries all 36 verified stories from Saturday 21 November 2026: a huge date masthead, a by-the-numbers strip, a region bar, a "THE DAY SO FAR" timeline rail, 3 illustrated leads (COP31 overtime, Kyiv under fire, missiles hit Poland), 10 illustrated features, a world map with 36 numbered pins, 23 briefs, a DATE CHECK box and a sources line.

## Files

- `draw.py` - draws the poster with Pillow and writes `entry.png` (`python3 draw.py`).
- `entry.png` - the generated poster.
- `main.py` - Python 3.13, standard library + Pillow; runs the drawing and writes the poster to `/output/entry.png`.

```
python3 main.py
```

## License

MIT, see `LICENSE`.
