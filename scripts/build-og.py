#!/usr/bin/env python3
"""
Render the link-preview image (public/og.png) from scripts/og/card.html.

The card is plain HTML so it can use the site's real fonts and colours;
headless Chrome screenshots it at exactly 1200x630, the size Facebook,
WhatsApp, Slack, X and iMessage all expect.

    python3 scripts/build-og.py

Only needed when the card design changes — the image is committed, so a
normal deploy never runs this. Deliberately carries no song count: the
number would be wrong the next time a song is added or removed.
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARD = os.path.join(ROOT, "scripts", "og", "card.html")
LOGO = os.path.join(ROOT, "public", "logo.svg")
OUT = os.path.join(ROOT, "public", "og.png")

CHROMES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]


def main():
    chrome = next((c for c in CHROMES if c and os.path.exists(c)), None)
    if not chrome:
        sys.exit("no Chrome found — install it or render scripts/og/card.html by hand at 1200x630")

    # the card references logo.svg relatively, so render from a dir holding both
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(CARD, os.path.join(tmp, "card.html"))
        shutil.copy(LOGO, os.path.join(tmp, "logo.svg"))
        shot = os.path.join(tmp, "og.png")
        subprocess.run([
            chrome, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
            "--force-device-scale-factor=1", "--window-size=1200,630",
            "--virtual-time-budget=6000",          # let Google Fonts arrive
            f"--screenshot={shot}", "file://" + os.path.join(tmp, "card.html"),
        ], check=True, capture_output=True)

        if not os.path.exists(shot):
            sys.exit("Chrome produced no screenshot")

        try:
            from PIL import Image
            im = Image.open(shot).convert("RGB")
            if im.size != (1200, 630):
                sys.exit(f"expected 1200x630, got {im.size}")
            im.save(OUT, optimize=True)
        except ImportError:
            shutil.copy(shot, OUT)

    print(f"wrote public/og.png ({os.path.getsize(OUT) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
