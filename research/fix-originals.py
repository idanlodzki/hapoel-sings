#!/usr/bin/env python3
"""
Give each song a single, working link to its ORIGINAL tune.

For every song that has no usable original, in this order:
  1. use the URL in the wiki's |שיר מקורי= field, if YouTube says it still plays
  2. otherwise search YouTube for the |מנגינה= tune name, and accept the top
     hit only if its title actually matches that name
  3. otherwise leave the song exactly as it is

Songs we do fix are reduced to that one link. Songs we cannot identify are not
touched at all — deleting their links would destroy data for no gain.

    python3 fix-originals.py            # dry run, writes fixes.json
    python3 fix-originals.py --apply    # write to hapoel.db
"""
import argparse
import json
import os
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "hapoel.db")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")

# tune fields that name nothing usable
JUNK = re.compile(r"^\s*(\?+|-+|מנגינה|ביצוע.*|)\s*$")


def meaningful(name):
    if not name or JUNK.match(name):
        return False
    return len(re.sub(r"\W+", "", name)) >= 4


HEB = re.compile(r"[֐-׿]")


def yt_search(q, n=4):
    # ask YouTube in the language the tune name is written in
    hl = "he" if HEB.search(q) else "en"
    url = "https://www.youtube.com/results?" + urllib.parse.urlencode(
        {"search_query": q, "hl": hl}
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": hl})
    try:
        h = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    except Exception:
        return []
    out, seen = [], set()
    for m in re.finditer(
        r'"videoRenderer":\{"videoId":"([A-Za-z0-9_-]{11})".*?"title":\{"runs":\[\{"text":"(.*?)"\}',
        h,
    ):
        vid, title = m.group(1), m.group(2)
        # the page embeds JSON, so decode the \uXXXX escapes as JSON.
        # unicode_escape mangles anything non-Latin into mojibake, which
        # silently zeroed the match score for every Hebrew tune.
        try:
            title = json.loads('"' + title + '"')
        except Exception:
            pass
        if vid in seen:
            continue
        seen.add(vid)
        out.append((vid, title))
        if len(out) >= n:
            break
    return out


OEMBED = "https://www.youtube.com/oembed?url=%s&format=json"


def playable(vid):
    url = OEMBED % urllib.parse.quote(f"https://www.youtube.com/watch?v={vid}", safe="")
    try:
        urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20
        )
        return True
    except Exception:
        return False


def norm(s):
    s = (s or "").lower()
    s = re.sub(r"[֑-ׇ]", "", s)          # niqqud
    s = re.sub(r"[^\w֐-׿]+", " ", s)      # keep latin + hebrew
    return re.sub(r"\s+", " ", s).strip()


def score(tune, title):
    """How much of the tune name shows up in the video title (0..1)."""
    t = [w for w in norm(tune).split() if len(w) > 2]
    if not t:
        return 0.0
    hay = norm(title)
    return sum(1 for w in t if w in hay) / len(t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--threshold", type=float, default=0.5)
    a = ap.parse_args()

    plan = json.load(open(os.path.join(HERE, "plan.json"), encoding="utf-8"))
    actions = []

    for s in plan["songs"]:
        good = [l for l in s["links"] if l["original"] and l["status"] == "ok"]
        if good:
            keep = good[0]["video_id"]
            extra = [l for l in s["links"] if l["video_id"] != keep]
            if extra:
                actions.append({"song": s["name"], "id": s["id"], "how": "trim",
                                "video": keep, "title": good[0].get("title", ""),
                                "removed": len(extra)})
            continue

        # 1. the wiki's own original url, if it still plays
        w = s.get("wiki_original_check")
        if w and w.get("status") == "ok":
            actions.append({"song": s["name"], "id": s["id"], "how": "wiki-field",
                            "video": s["wiki_original_url"], "title": w.get("title", ""),
                            "removed": len(s["links"])})
            continue

        # 2. search for the named tune
        tune = s.get("tune_name")
        if meaningful(tune):
            hits = yt_search(tune)
            time.sleep(0.6)
            best = None
            for vid, title in hits:
                sc = score(tune, title)
                if sc >= a.threshold and playable(vid):
                    best = (vid, title, sc)
                    break
            if best:
                actions.append({"song": s["name"], "id": s["id"], "how": "search",
                                "video": best[0], "title": best[1],
                                "tune": tune, "confidence": round(best[2], 2),
                                "removed": len(s["links"])})
                continue
            actions.append({"song": s["name"], "id": s["id"], "how": "search-failed",
                            "tune": tune,
                            "candidates": [f"{t} ({v})" for v, t in hits[:3]]})
            continue

        actions.append({"song": s["name"], "id": s["id"], "how": "skip",
                        "why": "no tune named on the wiki page"})

    json.dump({"actions": actions}, open(os.path.join(HERE, "fixes.json"), "w",
              encoding="utf-8"), ensure_ascii=False, indent=2)

    by = {}
    for x in actions:
        by.setdefault(x["how"], []).append(x)
    print("plan:")
    for k in ("wiki-field", "search", "trim", "search-failed", "skip"):
        if k in by:
            print(f"  {k:14s} {len(by[k])}")
    print(f"  links removed  {sum(x.get('removed', 0) for x in actions)}")

    if by.get("search"):
        print("\nfound by search:")
        for x in by["search"]:
            print(f"  {x['song'][:32]:34s} {x['tune'][:30]:32s} -> {x['title'][:42]}  ({x['confidence']})")
    if by.get("search-failed"):
        print("\nsearch found nothing convincing (left untouched):")
        for x in by["search-failed"]:
            print(f"  {x['song'][:32]:34s} tune: {x['tune'][:40]}")

    if not a.apply:
        print("\ndry run — nothing written. re-run with --apply")
        return

    c = sqlite3.connect(DB)
    n = 0
    for x in actions:
        if x["how"] not in ("wiki-field", "search", "trim"):
            continue
        c.execute("DELETE FROM links WHERE song_id=?", (x["id"],))
        c.execute(
            "INSERT INTO links (song_id, video_id, label, original, pos) VALUES (?,?,?,1,0)",
            (x["id"], x["video"], (x.get("title") or "")[:120] or None),
        )
        n += 1
    c.commit()
    songs = c.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
    links = c.execute("SELECT COUNT(*) FROM links").fetchone()[0]
    orig = c.execute("SELECT COUNT(*) FROM links WHERE original=1").fetchone()[0]
    c.close()
    print(f"\napplied to {n} songs. db now: {songs} songs, {links} links, {orig} originals")


if __name__ == "__main__":
    main()
