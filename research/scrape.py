#!/usr/bin/env python3
"""
Collect Hapoel Tel Aviv songs from ויקיפועל (wiki.red-fans.com).

Walks קטגוריה:שירים and every subcategory under it, then for each song page
pulls the raw wikitext and extracts YouTube links.

We read the wikitext rather than the rendered HTML because the wiki embeds
videos several different ways — plain links, {{#ev:youtube|ID}}, <youtube>
tags — and only some of those surface in the API's `extlinks` list.

Only titles and links are stored. Lyrics are never extracted.

    python3 scrape.py
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import OrderedDict

API = "https://wiki.red-fans.com/api.php"
PAGE = "https://wiki.red-fans.com/index.php?title="
ROOT = "קטגוריה:שירים"
UA = "hapoel-songs-collector/1.0 (personal archive project)"

session_delay = 0.35


def api(**params):
    params.setdefault("format", "json")
    params.setdefault("formatversion", "2")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if attempt == 3:
                print(f"  ! api failed: {e}", file=sys.stderr)
                return {}
            time.sleep(1.5 * (attempt + 1))
    return {}


def category_members(title):
    """All members of a category, following continuation."""
    out, cont = [], {}
    while True:
        d = api(
            action="query",
            list="categorymembers",
            cmtitle=title,
            cmlimit="500",
            **cont,
        )
        out += d.get("query", {}).get("categorymembers", [])
        if "continue" in d:
            cont = d["continue"]
            time.sleep(session_delay)
        else:
            return out


def walk(root):
    """Recursively gather article titles under a category tree."""
    pages, seen_cats, queue = OrderedDict(), set(), [root]
    tree = []
    while queue:
        cat = queue.pop(0)
        if cat in seen_cats:
            continue
        seen_cats.add(cat)
        members = category_members(cat)
        n_pages = 0
        for m in members:
            if m["ns"] == 14:  # subcategory
                queue.append(m["title"])
            elif m["ns"] == 0:  # article
                pages.setdefault(m["title"], cat)
                n_pages += 1
        tree.append((cat, n_pages, sum(1 for m in members if m["ns"] == 14)))
        print(f"  {cat}: {n_pages} songs, {tree[-1][2]} subcategories")
        time.sleep(session_delay)
    return pages, tree


def wikitext(titles):
    """Raw wikitext for up to 50 titles at a time."""
    d = api(
        action="query",
        prop="revisions",
        rvprop="content",
        rvslots="main",
        titles="|".join(titles),
    )
    out = {}
    for p in d.get("query", {}).get("pages", []):
        if "revisions" not in p:
            continue
        try:
            out[p["title"]] = p["revisions"][0]["slots"]["main"]["content"]
        except (KeyError, IndexError):
            pass
    return out


# youtube ids are 11 chars of [A-Za-z0-9_-]
ID = r"[A-Za-z0-9_-]{11}"
PATTERNS = [
    re.compile(r"youtube\.com/watch\?[^\s\]|}<]*v=(" + ID + r")"),
    re.compile(r"youtu\.be/(" + ID + r")"),
    re.compile(r"youtube\.com/embed/(" + ID + r")"),
    re.compile(r"youtube\.com/v/(" + ID + r")"),
    re.compile(r"\{\{\s*#ev:\s*youtube\s*\|\s*(" + ID + r")", re.I),
    re.compile(r"<youtube[^>]*>\s*(" + ID + r")", re.I),
    re.compile(r"youtube\.com/shorts/(" + ID + r")"),
]


def youtube_ids(text):
    found = []
    for pat in PATTERNS:
        for vid in pat.findall(text or ""):
            if vid not in found:
                found.append(vid)
    return found


def page_url(title):
    return PAGE + urllib.parse.quote(title.replace(" ", "_"))


def main():
    print(f"Walking category tree from {ROOT} …")
    pages, tree = walk(ROOT)
    print(f"\n{len(pages)} unique song pages found. Fetching wikitext …")

    titles = list(pages)
    records = []
    for i in range(0, len(titles), 40):
        chunk = titles[i : i + 40]
        texts = wikitext(chunk)
        for t in chunk:
            ids = youtube_ids(texts.get(t, ""))
            records.append(
                {
                    "song": t,
                    "category": pages[t],
                    "wiki_url": page_url(t),
                    "youtube": [f"https://www.youtube.com/watch?v={v}" for v in ids],
                    "youtube_count": len(ids),
                    "has_wikitext": t in texts,
                }
            )
        print(f"  {min(i+40, len(titles))}/{len(titles)}")
        time.sleep(session_delay)

    records.sort(key=lambda r: (r["category"], r["song"]))
    with_yt = [r for r in records if r["youtube"]]

    # ---- outputs -------------------------------------------------------
    with open("songs.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "source": "https://wiki.red-fans.com",
                "root_category": ROOT,
                "categories": [{"category": c, "songs": n, "subcategories": s} for c, n, s in tree],
                "song_count": len(records),
                "songs_with_youtube": len(with_yt),
                "songs": records,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    with open("songs.csv", "w", encoding="utf-8-sig") as f:
        f.write("song,category,wiki_url,youtube_url\n")
        for r in records:
            links = r["youtube"] or [""]
            for link in links:
                name = r["song"].replace('"', '""')
                f.write(f'"{name}","{r["category"]}","{r["wiki_url"]}","{link}"\n')

    with open("songs.md", "w", encoding="utf-8") as f:
        f.write("# שירי הפועל תל אביב — ויקיפועל\n\n")
        f.write(f"נאסף מתוך [{ROOT}](" + page_url(ROOT) + ") וכל תתי-הקטגוריות.\n\n")
        f.write(f"**{len(records)} שירים**, מתוכם **{len(with_yt)}** עם קישור ליוטיוב.\n\n")
        by_cat = OrderedDict()
        for r in records:
            by_cat.setdefault(r["category"], []).append(r)
        for cat, rows in by_cat.items():
            f.write(f"\n## {cat}\n\n")
            f.write("| שיר | ויקיפועל | יוטיוב |\n|---|---|---|\n")
            for r in rows:
                yt = " · ".join(f"[{i+1}]({u})" for i, u in enumerate(r["youtube"])) or "—"
                f.write(f'| {r["song"]} | [דף]({r["wiki_url"]}) | {yt} |\n')

    print(f"\nDone. {len(records)} songs, {len(with_yt)} with YouTube links.")
    print(f"Total YouTube links: {sum(r['youtube_count'] for r in records)}")
    missing = [r["song"] for r in records if not r["has_wikitext"]]
    if missing:
        print(f"No wikitext for {len(missing)}: {missing[:5]}")


if __name__ == "__main__":
    main()
