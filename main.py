"""Entry program: draws the Saturday 21 November 2026 news poster to /output/entry.png (and ./entry.png)."""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import draw  # noqa: E402


def run():
    os.makedirs("/output", exist_ok=True)
    out, _ = draw.main("/output")
    shutil.copyfile(out, os.path.join(HERE, "entry.png"))


if __name__ == "__main__":
    run()
