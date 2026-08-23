#!/usr/bin/env python3
"""
data/hapoel.db  ->  public/songs.json

songs.json is what the live site reads and what you edit on GitHub, so it is
written to be read by a human: one object per song, sorted by name.

    python3 scripts/export-db.py
"""
import collections, json, os, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "hapoel.db")
OUT = os.path.join(ROOT, "public", "songs.json")

c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
c.row_factory = sqlite3.Row
links = collections.defaultdict(list)
for r in c.execute("SELECT * FROM links ORDER BY song_id, pos, id"):
    links[r["song_id"]].append(dict(r))

songs = []
for r in c.execute("SELECT * FROM songs ORDER BY name"):
    ls = links[r["id"]]
    if not ls:
        continue
    songs.append({
        "name": r["name"],
        "category": (r["category"] or "").replace("קטגוריה:", ""),
        "artist": r["artist"] or None,
        "wiki": r["wiki_url"] or None,
        "youtube": [l["video_id"] for l in ls],
        "original": bool(any(l["original"] for l in ls)),
    })
c.close()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({"count": len(songs), "songs": songs},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(songs)} songs -> public/songs.json "
      f"({sum(len(s['youtube']) for s in songs)} videos, "
      f"{sum(1 for s in songs if s['original'])} with a source tune)")
