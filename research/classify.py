#!/usr/bin/env python3
"""
Re-parse the cached wikitext, keeping each YouTube link's CAPTION, and mark
which ones are the original tune the terrace chant borrowed.

The first pass collected bare video IDs and threw the captions away, so a fan
recording and the original studio track were indistinguishable. The wiki
labels them consistently, e.g.

    * 🎥 [http://youtube.com/watch?v=... Sung by Hapoel Fans]
    * 🎥 [http://youtube.com/watch?v=... dOriginal tune by Michale Jackson]

Only titles, captions and links are read. Lyrics are never extracted.

    python3 classify.py
"""
import json
import re
from collections import OrderedDict

CACHE = "wikitext-cache.json"
PAGE = "https://wiki.red-fans.com/index.php?title="

YT = re.compile(
    r"(?:youtube\.com/watch\?[^\s\]]*v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/"
    r"|youtube\.com/shorts/)([A-Za-z0-9_-]{11})"
)

# Embed syntaxes carry no caption, so they can never be the labelled original —
# but they are still recordings and must not be dropped from the page's list.
EMBED = [
    re.compile(r"\{\{\s*#ev:\s*youtube\s*\|\s*([A-Za-z0-9_-]{11})", re.I),
    re.compile(r"<youtube[^>]*>\s*([A-Za-z0-9_-]{11})", re.I),
]
LINK = re.compile(r"\[\s*(https?://[^\s\]]+)\s*([^\]]*)\]")

# "מקור" covers מקורי / המקורי / במקור; "origin" survives the typos in the
# wiki ("Origina tune", "dOriginal tune") because they all still contain it.
IS_ORIGINAL = re.compile(r"מקור|origin", re.I)

# a caption that names who performed the original
ARTIST_HE = re.compile(r"(?:מקורי|מקור)\s*(?:של|בביצועו של|בביצוע של)\s+(.+)$")
ARTIST_EN = re.compile(r"origina?l?\s*(?:tune|song)?\s*(?:by|of)\s+(.+)$", re.I)
ARTIST_PAREN = re.compile(r"^origina?l?\s*(?:tune|song)?\s*\((.+)\)\s*$", re.I)


def clean_label(s):
    s = re.sub(r"'{2,}", "", s or "")          # wiki bold/italic markup
    s = re.sub(r"^[\s*#:🎥▶️🎬🎧🔊•\-–]+", "", s)  # bullets and media emoji
    return re.sub(r"\s+", " ", s).strip()


def artist_of(label):
    for pat in (ARTIST_PAREN, ARTIST_EN, ARTIST_HE):
        m = pat.search(label)
        if m:
            a = m.group(1).strip(" .\"'-–—")
            # reject junk like "tune" or a lone article
            if 1 < len(a) <= 60 and not re.fullmatch(r"(tune|song|שיר|השיר)", a, re.I):
                return a
    return None


def parse_page(title, text):
    links, seen = [], set()

    for url, raw in LINK.findall(text):
        m = YT.search(url)
        if not m:
            continue
        vid = m.group(1)
        if vid in seen:
            continue
        seen.add(vid)
        label = clean_label(raw)
        original = bool(label and IS_ORIGINAL.search(label))
        links.append(
            {
                "id": vid,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "label": label or None,
                "original": original,
                "artist": artist_of(label) if original else None,
            }
        )

    # bare URLs / {{#ev:}} embeds carry no caption, so they can never be
    # classified as the original — record them, but never as `original`.
    bare = YT.findall(text)
    for pat in EMBED:
        bare += pat.findall(text)
    for vid in bare:
        if vid not in seen:
            seen.add(vid)
            links.append(
                {
                    "id": vid,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "label": None,
                    "original": False,
                    "artist": None,
                }
            )
    return links


def main():
    cache = json.load(open(CACHE, encoding="utf-8"))
    base = json.load(open("songs.json", encoding="utf-8"))
    cat_of = {s["song"]: s["category"] for s in base["songs"]}

    records = []
    for title, text in cache.items():
        links = parse_page(title, text)
        originals = [l for l in links if l["original"]]
        records.append(
            {
                "song": title,
                "category": cat_of.get(title, ""),
                "wiki_url": PAGE + title.replace(" ", "_"),
                "links": links,
                "original_links": [l["url"] for l in originals],
                "original_artist": next((l["artist"] for l in originals if l["artist"]), None),
                "has_original": bool(originals),
            }
        )
    records.sort(key=lambda r: (r["category"], r["song"]))

    withorig = [r for r in records if r["has_original"]]

    json.dump(
        {
            "source": "https://wiki.red-fans.com",
            "song_count": len(records),
            "songs_with_original": len(withorig),
            "total_links": sum(len(r["links"]) for r in records),
            "original_links": sum(len(r["original_links"]) for r in records),
            "songs": records,
        },
        open("songs.json", "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )

    # ---- originals-only view -------------------------------------------
    json.dump(
        {
            "note": "Only links the wiki captions as the original tune.",
            "song_count": len(withorig),
            "songs": [
                {
                    "song": r["song"],
                    "category": r["category"],
                    "wiki_url": r["wiki_url"],
                    "original_artist": r["original_artist"],
                    "youtube": r["original_links"],
                }
                for r in withorig
            ],
        },
        open("originals.json", "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )

    with open("originals.csv", "w", encoding="utf-8-sig") as f:
        f.write("song,category,original_artist,wiki_url,youtube_url\n")
        for r in withorig:
            for u in r["original_links"]:
                n = r["song"].replace('"', '""')
                a = (r["original_artist"] or "").replace('"', '""')
                f.write(f'"{n}","{r["category"]}","{a}","{r["wiki_url"]}","{u}"\n')

    with open("originals.md", "w", encoding="utf-8") as f:
        f.write("# שירי הפועל — השיר המקורי\n\n")
        f.write("רק הקישורים שוויקיפועל מסמן כשיר/הביצוע המקורי.\n\n")
        f.write(f"**{len(withorig)} שירים** מתוך {len(records)}.\n\n")
        by = OrderedDict()
        for r in withorig:
            by.setdefault(r["category"], []).append(r)
        for cat, rows in by.items():
            f.write(f"\n## {cat}\n\n| שיר | מקור | ויקיפועל | יוטיוב |\n|---|---|---|---|\n")
            for r in rows:
                yt = " · ".join(f"[{i+1}]({u})" for i, u in enumerate(r["original_links"]))
                f.write(
                    f'| {r["song"]} | {r["original_artist"] or "—"} '
                    f'| [דף]({r["wiki_url"]}) | {yt} |\n'
                )

    print(f"songs: {len(records)}")
    print(f"  with an 'original' link: {len(withorig)}")
    print(f"  total links: {sum(len(r['links']) for r in records)}")
    print(f"  original links: {sum(len(r['original_links']) for r in records)}")
    print(f"  original artist named: {sum(1 for r in withorig if r['original_artist'])}")


if __name__ == "__main__":
    main()
