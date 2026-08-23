#!/usr/bin/env python3
"""
Cache the raw wikitext of every song page to wikitext-cache.json.

Kept separate from parsing so the link classifier can be re-run and tuned
without hammering the wiki again.

    python3 fetch-wikitext.py
"""
import json
import os
import time
import urllib.parse
import urllib.request

API = "https://wiki.red-fans.com/api.php"
UA = "hapoel-songs-collector/1.1 (personal archive project)"
CACHE = "wikitext-cache.json"


def api(**params):
    params.setdefault("format", "json")
    params.setdefault("formatversion", "2")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            if attempt == 3:
                return {}
            time.sleep(1.5 * (attempt + 1))
    return {}


def main():
    songs = json.load(open("songs.json", encoding="utf-8"))["songs"]
    titles = [s["song"] for s in songs]

    cache = {}
    if os.path.exists(CACHE):
        cache = json.load(open(CACHE, encoding="utf-8"))

    todo = [t for t in titles if t not in cache]
    print(f"{len(titles)} pages, {len(cache)} cached, {len(todo)} to fetch")

    for i in range(0, len(todo), 40):
        chunk = todo[i : i + 40]
        d = api(
            action="query",
            prop="revisions",
            rvprop="content",
            rvslots="main",
            titles="|".join(chunk),
        )
        for p in d.get("query", {}).get("pages", []):
            if "revisions" in p:
                try:
                    cache[p["title"]] = p["revisions"][0]["slots"]["main"]["content"]
                except (KeyError, IndexError):
                    pass
        print(f"  {min(i+40, len(todo))}/{len(todo)}")
        time.sleep(0.35)

    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"cached {len(cache)} pages -> {CACHE}")


if __name__ == "__main__":
    main()
