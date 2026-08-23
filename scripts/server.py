#!/usr/bin/env python3
"""
Serves the game and a small JSON API backed by SQLite, so songs can be added,
edited and removed and the changes survive a reload — and are shared by
everyone hitting this server, which localStorage could never do.

Standard library only.

    python3 server.py            # http://localhost:8790
    python3 server.py --port 9000
    python3 server.py --reseed   # wipe and re-import from songs.json

The database (hapoel.db) is seeded once from songs.json. After that it is the
source of truth: re-running the scrapers will not clobber your edits unless
you pass --reseed.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "hapoel.db")
WEB = os.path.join(HERE, "game")

VIDEO_ID = re.compile(
    r"(?:youtube\.com/watch\?[^\s]*?v=|youtu\.be/|youtube\.com/embed/|"
    r"youtube\.com/v/|youtube\.com/shorts/)([A-Za-z0-9_-]{11})"
)
BARE_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


def video_id(text):
    """Accept a full YouTube URL in any of its shapes, or a bare 11-char id."""
    t = (text or "").strip()
    if BARE_ID.match(t):
        return t
    m = VIDEO_ID.search(t)
    return m.group(1) if m else None


# ---------------------------------------------------------------- database
def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c


SCHEMA = """
CREATE TABLE IF NOT EXISTS songs (
  id       INTEGER PRIMARY KEY,
  name     TEXT NOT NULL,
  category TEXT DEFAULT '',
  wiki_url TEXT DEFAULT '',
  artist   TEXT,
  custom   INTEGER NOT NULL DEFAULT 0,
  created  TEXT
);
CREATE TABLE IF NOT EXISTS links (
  id       INTEGER PRIMARY KEY,
  song_id  INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
  video_id TEXT NOT NULL,
  label    TEXT,
  original INTEGER NOT NULL DEFAULT 0,
  pos      INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_links_song ON links(song_id);
"""


def init_db(reseed=False):
    fresh = not os.path.exists(DB)
    c = connect()
    c.executescript(SCHEMA)
    if reseed:
        c.execute("DELETE FROM links")
        c.execute("DELETE FROM songs")
        c.commit()
        fresh = True
    n = c.execute("SELECT COUNT(*) n FROM songs").fetchone()["n"]
    if n == 0:
        seed(c)
    c.commit()
    c.close()
    return fresh


def seed(c):
    path = os.path.join(HERE, "songs.json")
    if not os.path.exists(path):
        print("songs.json not found — starting with an empty database")
        return
    data = json.load(open(path, encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for s in data["songs"]:
        cur = c.execute(
            "INSERT INTO songs (name, category, wiki_url, artist, custom, created)"
            " VALUES (?,?,?,?,0,?)",
            (s["song"], s.get("category", ""), s.get("wiki_url", ""),
             s.get("original_artist"), now),
        )
        sid = cur.lastrowid
        for i, l in enumerate(s.get("links", [])):
            c.execute(
                "INSERT INTO links (song_id, video_id, label, original, pos)"
                " VALUES (?,?,?,?,?)",
                (sid, l["id"], l.get("label"), 1 if l.get("original") else 0, i),
            )
    print(f"seeded {len(data['songs'])} songs from songs.json")


def all_songs(c):
    songs = {}
    for r in c.execute("SELECT * FROM songs ORDER BY name"):
        songs[r["id"]] = {
            "id": r["id"],
            "n": r["name"],
            "c": r["category"] or "",
            "w": r["wiki_url"] or "",
            "a": r["artist"],
            "custom": bool(r["custom"]),
            "links": [],
            "o": [],
            "y": [],
        }
    for r in c.execute("SELECT * FROM links ORDER BY song_id, pos, id"):
        s = songs.get(r["song_id"])
        if not s:
            continue
        s["links"].append(
            {"id": r["id"], "v": r["video_id"], "label": r["label"],
             "original": bool(r["original"])}
        )
        s["y"].append(r["video_id"])
        if r["original"]:
            s["o"].append(r["video_id"])
    return list(songs.values())


def replace_links(c, sid, links):
    c.execute("DELETE FROM links WHERE song_id = ?", (sid,))
    for i, l in enumerate(links or []):
        vid = video_id(l.get("v") or l.get("url") or "")
        if not vid:
            continue
        c.execute(
            "INSERT INTO links (song_id, video_id, label, original, pos) VALUES (?,?,?,?,?)",
            (sid, vid, (l.get("label") or "").strip() or None,
             1 if l.get("original") else 0, i),
        )


# ---------------------------------------------------------------- http
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=WEB, **kw)

    def log_message(self, fmt, *args):
        if "/api/" in (self.path or ""):
            sys.stderr.write("  %s %s\n" % (self.command, self.path))

    # ---- helpers
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    def _song_id(self):
        m = re.match(r"^/api/songs/(\d+)$", urlparse(self.path).path)
        return int(m.group(1)) if m else None

    # ---- routes
    def do_GET(self):
        if urlparse(self.path).path == "/api/songs":
            c = connect()
            try:
                self._json({"songs": all_songs(c)})
            finally:
                c.close()
            return
        super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/songs":
            return self._json({"error": "not found"}, 404)
        d = self._body()
        name = (d.get("n") or "").strip()
        if not name:
            return self._json({"error": "שם השיר חסר"}, 400)

        links = d.get("links")
        if links is None:  # convenience: a single pasted url
            vid = video_id(d.get("url") or "")
            links = [{"v": vid, "label": d.get("label"), "original": d.get("original", True)}] if vid else []
        if not any(video_id(l.get("v") or l.get("url") or "") for l in links):
            return self._json({"error": "צריך קישור יוטיוב תקין"}, 400)

        c = connect()
        try:
            cur = c.execute(
                "INSERT INTO songs (name, category, wiki_url, artist, custom, created)"
                " VALUES (?,?,?,?,1,?)",
                (name, (d.get("c") or "").strip(), (d.get("w") or "").strip(),
                 (d.get("a") or "").strip() or None,
                 datetime.now(timezone.utc).isoformat(timespec="seconds")),
            )
            sid = cur.lastrowid
            replace_links(c, sid, links)
            c.commit()
            song = next((s for s in all_songs(c) if s["id"] == sid), None)
        finally:
            c.close()
        return self._json({"song": song}, 201)

    def do_PATCH(self):
        sid = self._song_id()
        if sid is None:
            return self._json({"error": "not found"}, 404)
        d = self._body()
        c = connect()
        try:
            if not c.execute("SELECT 1 FROM songs WHERE id=?", (sid,)).fetchone():
                return self._json({"error": "not found"}, 404)
            sets, vals = [], []
            for key, col in (("n", "name"), ("c", "category"), ("w", "wiki_url"), ("a", "artist")):
                if key in d:
                    sets.append(f"{col}=?")
                    v = (d[key] or "").strip()
                    vals.append(v or (None if col == "artist" else ""))
            if sets:
                vals.append(sid)
                c.execute(f"UPDATE songs SET {','.join(sets)} WHERE id=?", vals)
            if "links" in d:
                if not any(video_id(l.get("v") or l.get("url") or "") for l in d["links"]):
                    return self._json({"error": "צריך לפחות קישור יוטיוב אחד תקין"}, 400)
                replace_links(c, sid, d["links"])
            c.commit()
            song = next((s for s in all_songs(c) if s["id"] == sid), None)
        finally:
            c.close()
        return self._json({"song": song})

    def do_DELETE(self):
        sid = self._song_id()
        if sid is None:
            return self._json({"error": "not found"}, 404)
        c = connect()
        try:
            cur = c.execute("DELETE FROM songs WHERE id=?", (sid,))
            c.commit()
            if not cur.rowcount:
                return self._json({"error": "not found"}, 404)
        finally:
            c.close()
        return self._json({"ok": True})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8790)
    ap.add_argument("--reseed", action="store_true", help="wipe and re-import songs.json")
    a = ap.parse_args()

    init_db(reseed=a.reseed)
    c = connect()
    n = c.execute("SELECT COUNT(*) n FROM songs").fetchone()["n"]
    l = c.execute("SELECT COUNT(*) n FROM links").fetchone()["n"]
    c.close()

    print(f"database: {DB}  ({n} songs, {l} links)")
    print(f"game:     http://localhost:{a.port}")
    ThreadingHTTPServer(("", a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
