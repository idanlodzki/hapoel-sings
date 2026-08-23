#!/usr/bin/env python3
"""
Read-only analysis pass.

For every song in hapoel.db, pull the wiki infobox fields:
    |שיר מקורי=   often a YouTube URL for the original recording
    |מנגינה=      the name of the tune the chant borrowed

then check every candidate link against YouTube's oEmbed endpoint, which tells
us whether a video still exists and is embeddable, and returns its real title.

Writes plan.json. Changes nothing.

    python3 analyse-originals.py
"""
import json
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = __import__("os").path.dirname(__import__("os").path.abspath(__file__))
DB = HERE + "/hapoel.db"
UA = "hapoel-songs/1.2 (personal archive)"

VID = re.compile(
    r"(?:youtube\.com/watch\?[^\s\]|}]*?v=|youtu\.be/|youtube\.com/embed/"
    r"|youtube\.com/v/|youtube\.com/shorts/)([A-Za-z0-9_-]{11})"
)


def field(text, name):
    """Value of |name= inside the infobox, up to the next |field= or }}."""
    m = re.search(r"\|\s*" + re.escape(name) + r"\s*=", text)
    if not m:
        return ""
    rest = text[m.end():]
    stop = re.search(r"\n\s*\|\s*[^=\n|]{1,24}=|\n?\}\}", rest)
    return (rest[: stop.start()] if stop else rest[:400]).strip()


def clean_name(s):
    s = re.sub(r"https?://\S+", " ", s or "")
    s = re.sub(r"\{\{[^}]*\}\}|\[\[[^\]]*\]\]|\[[^\]]*\]", " ", s)
    s = re.sub(r"[''\"\|]+", " ", s)
    return re.sub(r"\s+", " ", s).strip(" -–—,.")


OEMBED = "https://www.youtube.com/oembed?url=%s&format=json"


def check(vid):
    """(status, title, channel). status: ok | gone | blocked | error"""
    url = OEMBED % urllib.parse.quote(f"https://www.youtube.com/watch?v={vid}", safe="")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.loads(r.read().decode("utf-8"))
                return "ok", d.get("title", ""), d.get("author_name", "")
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                return "blocked", "", ""     # exists but embedding disabled
            if e.code in (400, 404):
                return "gone", "", ""        # deleted / private / bad id
            time.sleep(1 + attempt)
        except Exception:
            time.sleep(1 + attempt)
    return "error", "", ""


def main():
    cache = json.load(open(HERE + "/wikitext-cache.json", encoding="utf-8"))
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row

    links = {}
    for r in c.execute("SELECT * FROM links ORDER BY song_id, pos, id"):
        links.setdefault(r["song_id"], []).append(dict(r))

    songs = []
    for r in c.execute("SELECT * FROM songs ORDER BY name"):
        s = dict(r)
        txt = cache.get(s["name"], "")
        raw_orig = field(txt, "שיר מקורי")
        raw_mang = field(txt, "מנגינה")
        s["wiki_original_url"] = (VID.search(raw_orig).group(1) if VID.search(raw_orig) else None)
        s["tune_name"] = clean_name(raw_mang) or clean_name(raw_orig) or None
        s["links"] = links.get(s["id"], [])
        s["has_original"] = any(l["original"] for l in s["links"])
        songs.append(s)
    c.close()

    # every distinct video id we might care about
    ids = set()
    for s in songs:
        for l in s["links"]:
            ids.add(l["video_id"])
        if s["wiki_original_url"]:
            ids.add(s["wiki_original_url"])
    ids = sorted(ids)
    print(f"{len(songs)} songs · checking {len(ids)} distinct videos on YouTube …", file=sys.stderr)

    results = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for i, (vid, res) in enumerate(zip(ids, ex.map(check, ids)), 1):
            results[vid] = {"status": res[0], "title": res[1], "channel": res[2]}
            if i % 50 == 0:
                print(f"  {i}/{len(ids)}", file=sys.stderr)

    for s in songs:
        for l in s["links"]:
            l.update(results.get(l["video_id"], {"status": "error"}))
        if s["wiki_original_url"]:
            s["wiki_original_check"] = results.get(s["wiki_original_url"], {"status": "error"})

    json.dump(
        {"checked": len(ids), "songs": songs},
        open(HERE + "/plan.json", "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )

    # ---- summary ----
    ok = sum(1 for v in results.values() if v["status"] == "ok")
    print(f"\nvideo health: ok={ok} "
          f"blocked={sum(1 for v in results.values() if v['status']=='blocked')} "
          f"gone={sum(1 for v in results.values() if v['status']=='gone')} "
          f"error={sum(1 for v in results.values() if v['status']=='error')}")

    need = [s for s in songs if not s["has_original"]]
    fixable = [s for s in need if s.get("wiki_original_check", {}).get("status") == "ok"]
    named = [s for s in need if s not in fixable and s["tune_name"]]
    nothing = [s for s in need if s not in fixable and not s["tune_name"]]
    print(f"\nsongs without an original link: {len(need)}")
    print(f"  wiki names a WORKING original url : {len(fixable)}   <- can fix automatically")
    print(f"  only a tune NAME, no usable url   : {len(named)}   <- needs a YouTube search")
    print(f"  no tune info at all               : {len(nothing)}   <- leave alone")
    print("\nplan.json written")


if __name__ == "__main__":
    main()
