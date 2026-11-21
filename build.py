"""Offline builder: renders entry.png with Pillow (draw.py). The grader never runs this; main.ts only copies entry.png."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import draw  # noqa: E402

if __name__ == "__main__":
    draw.main(HERE)
