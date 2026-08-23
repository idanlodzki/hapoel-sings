#!/usr/bin/env python3
"""
Add a song to public/songs.json — the file the live site reads.

    python3 scripts/add-song.py "שם השיר" "https://youtu.be/VIDEOID"
    python3 scripts/add-song.py "שם השיר" VIDEOID --artist "שם האמן" --category "שירים מהיציע"

Checks the video actually plays before writing, and refuses duplicates.
After it succeeds:  git commit -am "add song"  &&  git push   → Vercel redeploys.
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "public", "songs.json")
UA = "hapoel-songs/2.0"

ID = re.compile(
    r"(?:youtube\.com/watch\?[^\s]*?v=|youtu\.be/|youtube\.com/embed/"
    r"|youtube\.com/shorts/|youtube\.com/v/)([A-Za-z0-9_-]{11})"
)


def video_id(text):
    t = (text or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", t):
        return t
    m = ID.search(t)
    return m.group(1) if m else None


def youtube_title(vid):
    """Returns the real title, or None if YouTube will not serve the video."""
    url = "https://www.youtube.com/oembed?url=%s&format=json" % urllib.parse.quote(
        f"https://www.youtube.com/watch?v={vid}", safe=""
    )
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20
        ) as r:
            return json.loads(r.read().decode("utf-8")).get("title", "")
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description="Add a song to public/songs.json")
    ap.add_argument("name", help="song name, in Hebrew")
    ap.add_argument("youtube", help="YouTube URL or 11-character video id")
    ap.add_argument("--artist", default=None, help="who performs the original tune")
    ap.add_argument("--category", default="נוספו ידנית")
    ap.add_argument("--wiki", default=None, help="wikipoel page url, if there is one")
    ap.add_argument("--force", action="store_true", help="add even if the video will not play")
    a = ap.parse_args()

    vid = video_id(a.youtube)
    if not vid:
        sys.exit(f"✗ could not read a YouTube video id from: {a.youtube}")

    data = json.load(open(SONGS, encoding="utf-8"))
    songs = data["songs"]

    for s in songs:
        if vid in s.get("youtube", []):
            sys.exit(f"✗ that video is already used by: {s['name']}")
        if s["name"].strip() == a.name.strip():
            sys.exit(f"✗ a song called “{a.name}” already exists")

    title = youtube_title(vid)
    if title is None and not a.force:
        sys.exit("✗ YouTube will not play that video (deleted, private, or embedding is off).\n"
                 "  Check the link, or pass --force to add it anyway.")

    songs.append({
        "name": a.name.strip(),
        "category": a.category.strip(),
        "artist": (a.artist or "").strip() or None,
        "wiki": (a.wiki or "").strip() or None,
        "youtube": [vid],
        "original": True,
    })
    songs.sort(key=lambda s: s["name"])
    data["count"] = len(songs)
    json.dump(data, open(SONGS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"✓ added “{a.name}”  ({len(songs)} songs now)")
    if title:
        print(f"  youtube: {title}")
    print("\nnext:  git add -A && git commit -m \"add song\" && git push")


if __name__ == "__main__":
    main()
