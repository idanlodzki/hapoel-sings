#!/usr/bin/env python3
"""
Check public/songs.json is well-formed before it reaches the live site.

Run it after hand-editing songs.json (on GitHub or locally). It exits non-zero
on a real problem, so it also works as a CI step.

    python3 scripts/validate.py
    python3 scripts/validate.py --check-videos   # also ask YouTube if each plays
"""
import argparse
import collections
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "public", "songs.json")
BARE = re.compile(r"^[A-Za-z0-9_-]{11}$")
ANY = re.compile(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})")


def as_id(s):
    s = str(s or "").strip()
    if BARE.match(s):
        return s
    m = ANY.search(s)
    return m.group(1) if m else None


def plays(vid):
    url = "https://www.youtube.com/oembed?url=%s&format=json" % urllib.parse.quote(
        f"https://www.youtube.com/watch?v={vid}", safe=""
    )
    try:
        urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "hapoel-songs/2.0"}),
            timeout=20,
        )
        return True
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-videos", action="store_true")
    a = ap.parse_args()

    try:
        data = json.load(open(SONGS, encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"✗ songs.json is not valid JSON — line {e.lineno}, column {e.colno}: {e.msg}")

    songs = data.get("songs")
    if not isinstance(songs, list) or not songs:
        sys.exit("✗ songs.json has no 'songs' list")

    errors, warnings = [], []
    seen_name, seen_vid = {}, {}

    for i, s in enumerate(songs):
        where = f"#{i} {s.get('name', '(no name)')!r}"
        if not str(s.get("name", "")).strip():
            errors.append(f"{where}: missing 'name'")
        ids = [as_id(v) for v in (s.get("youtube") or [])]
        if not any(ids):
            errors.append(f"{where}: no usable YouTube id")
        for raw, vid in zip(s.get("youtube") or [], ids):
            if vid is None:
                errors.append(f"{where}: cannot read a video id from {raw!r}")
        n = str(s.get("name", "")).strip()
        if n in seen_name:
            warnings.append(f"duplicate name: {n!r} (also #{seen_name[n]})")
        seen_name[n] = i
        for vid in filter(None, ids):
            if vid in seen_vid:
                warnings.append(f"video {vid} used by {n!r} and {seen_vid[vid]!r}")
            seen_vid[vid] = n

    if data.get("count") != len(songs):
        warnings.append(f"'count' says {data.get('count')} but there are {len(songs)} songs")

    dead = []
    if a.check_videos:
        ids = sorted(seen_vid)
        print(f"checking {len(ids)} videos on YouTube …")
        with ThreadPoolExecutor(max_workers=6) as ex:
            for vid, ok in zip(ids, ex.map(plays, ids)):
                if not ok:
                    dead.append((vid, seen_vid[vid]))

    print(f"\n{len(songs)} songs · {len(seen_vid)} distinct videos")
    cats = collections.Counter(s.get("category") or "—" for s in songs)
    print("categories: " + ", ".join(f"{k}={v}" for k, v in cats.most_common(6)))

    for w in warnings:
        print(f"  ! {w}")
    for e in errors:
        print(f"  ✗ {e}")
    for vid, name in dead:
        print(f"  ✗ will not play: {vid}  ({name})")

    if errors or dead:
        sys.exit(f"\nFAILED — {len(errors)} error(s), {len(dead)} dead video(s)")
    print("\nOK" + (f" — {len(warnings)} warning(s)" if warnings else ""))


if __name__ == "__main__":
    main()
