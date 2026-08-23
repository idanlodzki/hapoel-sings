#!/usr/bin/env python3
"""
Snapshot hapoel.db into backups/.

Uses SQLite's own backup API rather than copying the file. server.py may be
mid-write when this runs, and a plain `cp` of a live SQLite database can
capture a torn page or miss the write-ahead log — the result looks fine until
the day you actually need it.

Writes two artefacts:
  backups/hapoel-<stamp>.db     exact, restorable database
  backups/hapoel-<stamp>.json   plain text, readable without SQLite

    python3 backup.py
    python3 backup.py --keep 10     # prune to the newest 10 snapshots
"""
import argparse
import json
import os
import sqlite3
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "data", "hapoel.db")
OUT = os.path.join(ROOT, "backups")


def snapshot(stamp):
    os.makedirs(OUT, exist_ok=True)
    db_path = os.path.join(OUT, f"hapoel-{stamp}.db")

    src = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    dst = sqlite3.connect(db_path)
    with dst:
        src.backup(dst)          # consistent even while the server is writing
    src.close()
    dst.close()
    return db_path


def export_json(db_path, stamp):
    c = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    songs = []
    links_by_song = {}
    for r in c.execute("SELECT * FROM links ORDER BY song_id, pos, id"):
        links_by_song.setdefault(r["song_id"], []).append(
            {"video_id": r["video_id"], "label": r["label"], "original": bool(r["original"])}
        )
    for r in c.execute("SELECT * FROM songs ORDER BY id"):
        songs.append(
            {
                "id": r["id"],
                "name": r["name"],
                "category": r["category"],
                "wiki_url": r["wiki_url"],
                "artist": r["artist"],
                "custom": bool(r["custom"]),
                "created": r["created"],
                "links": links_by_song.get(r["id"], []),
            }
        )
    c.close()

    path = os.path.join(OUT, f"hapoel-{stamp}.json")
    json.dump(
        {"taken": stamp, "song_count": len(songs),
         "link_count": sum(len(s["links"]) for s in songs), "songs": songs},
        open(path, "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )
    return path, songs


def verify(db_path, expected):
    """A backup nobody opened is a backup nobody has."""
    c = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    got = (
        c.execute("SELECT COUNT(*) FROM songs").fetchone()[0],
        c.execute("SELECT COUNT(*) FROM links").fetchone()[0],
    )
    c.execute("PRAGMA integrity_check").fetchone()
    c.close()
    return got == expected, got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", type=int, default=0, help="prune to newest N snapshots")
    a = ap.parse_args()

    if not os.path.exists(DB):
        raise SystemExit(f"database not found at {DB}")

    live = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    expected = (
        live.execute("SELECT COUNT(*) FROM songs").fetchone()[0],
        live.execute("SELECT COUNT(*) FROM links").fetchone()[0],
    )
    live.close()

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    db_path = snapshot(stamp)
    json_path, songs = export_json(db_path, stamp)
    ok, got = verify(db_path, expected)

    custom = [s for s in songs if s["custom"]]
    print(f"backed up -> {os.path.relpath(db_path, ROOT)}  ({os.path.getsize(db_path)//1024} KB)")
    print(f"            {os.path.relpath(json_path, ROOT)}")
    print(f"verified:   {'OK' if ok else 'MISMATCH'}  songs={got[0]} links={got[1]} (live: {expected[0]}/{expected[1]})")
    if custom:
        print(f"includes {len(custom)} hand-added song(s):")
        for s in custom:
            print(f"  · {s['name']} — {s['artist'] or 'ללא אמן'} [{s['category']}] ({len(s['links'])} links)")
    if not ok:
        raise SystemExit("backup does not match the live database — investigate before relying on it")

    if a.keep:
        snaps = sorted(f for f in os.listdir(OUT) if f.endswith(".db"))
        for f in snaps[: max(0, len(snaps) - a.keep)]:
            os.remove(os.path.join(OUT, f))
            j = os.path.join(OUT, f[:-3] + ".json")
            if os.path.exists(j):
                os.remove(j)
            print(f"pruned {f}")


if __name__ == "__main__":
    main()
