#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add `sport` and `seasons` to each שירי שחקנים entry in songs.json, read from
the wiki's own roster category tags ([[קטגוריה:סגל הפועל ת"א (כדורגל) 2013/14]]).

Player names are embedded in song names in a few shapes, so candidates are
generated and checked against the set of real wiki page titles rather than
guessed at:
    "אור ישראלוב"                          -> plain
    "I'm Mr Lonely-רמזי ספורי"             -> tune-player
    "Let the sunshine in - אבי כנפו, אורי שלף" -> tune - p1, p2
    "אל-ים קנצפולסקי"                       -> hyphen inside the name itself
"""
import json, os, re, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "public", "songs.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
API = "https://wiki.red-fans.com/api.php"

CAT_RE = re.compile(r"\[\[קטגוריה:\s*סגל\s+(.*?)\s+(\d{4}/\d{2})\s*\]\]")
FINALS = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}


def norm(s):
    s = (s or "").strip().lower()
    s = "".join(FINALS.get(c, c) for c in s)
    s = re.sub(r"[֑-ׇ]", "", s)
    s = re.sub(r"[^\w֐-׿]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def api(**p):
    p.setdefault("format", "json"); p.setdefault("formatversion", "2")
    u = API + "?" + urllib.parse.urlencode(p)
    for a in range(3):
        try:
            return json.load(urllib.request.urlopen(
                urllib.request.Request(u, headers={"User-Agent": UA}), timeout=40))
        except Exception:
            if a == 2: return {}
            time.sleep(1.2)
    return {}


def sport_and_seasons(text):
    """-> (sport, sorted seasons) from roster category tags."""
    per = {}
    for m in CAT_RE.finditer(text):
        kind, season = m.group(1), m.group(2)
        per.setdefault(kind, set()).add(season)
    if not per:
        return None, []
    # prefer an explicitly sport-tagged squad over a reserve one
    for kind in per:
        if "כדורגל" in kind:
            return "כדורגל", sorted(per[kind], key=lambda s: int(s[:4]))
    for kind in per:
        if "כדורסל" in kind:
            return "כדורסל", sorted(per[kind], key=lambda s: int(s[:4]))
    kind = next(iter(per))
    return None, sorted(per[kind], key=lambda s: int(s[:4]))


def candidates(name):
    """Possible player names inside a song title, most specific first."""
    out = []
    tail = name.rsplit("-", 1)[-1] if "-" in name else name
    for chunk in (tail, name):
        for part in re.split(r"[,،]", chunk):
            p = part.strip(" -–—\"'")
            if len(p) >= 3:
                out.append(p)
    # de-dupe, keep order
    seen, uniq = set(), []
    for c in out:
        if c not in seen:
            seen.add(c); uniq.append(c)
    return uniq


def main():
    cache_path = os.environ.get("WIKI_CACHE", "")
    cache = json.load(open(cache_path, encoding="utf-8")) if cache_path and os.path.exists(cache_path) else {}
    by_norm = {}
    for req, d in cache.items():
        by_norm.setdefault(norm(req), d)
        by_norm.setdefault(norm(d["title"]), d)

    data = json.load(open(SONGS, encoding="utf-8"))
    songs = data["songs"]

    players = [s for s in songs if s["category"] == "שירי שחקנים"]
    print(f"player songs: {len(players)}", file=sys.stderr)

    resolved, unresolved = 0, []
    fetch_queue = []

    for s in players:
        hit = None
        matched_name = None
        for c in candidates(s["name"]):
            d = by_norm.get(norm(c))
            if d:
                hit, matched_name = d, c
                break
        if hit:
            sport, seasons = sport_and_seasons(hit["content"])
            s["sport"] = sport
            s["seasons"] = seasons
            s["player"] = hit["title"]
            resolved += 1
        else:
            unresolved.append(s)
            fetch_queue.append(s)

    print(f"resolved from cache: {resolved}", file=sys.stderr)
    print(f"needing a live lookup: {len(fetch_queue)}", file=sys.stderr)

    # try a live fetch for the leftovers, using their candidate names
    if fetch_queue:
        titles = []
        want = {}
        for s in fetch_queue:
            for c in candidates(s["name"])[:2]:
                titles.append(c)
                want.setdefault(norm(c), []).append(s)
        titles = list(dict.fromkeys(titles))
        got = {}
        for i in range(0, len(titles), 40):
            chunk = titles[i:i + 40]
            r = api(action="query", prop="revisions", rvprop="content",
                    rvslots="main", titles="|".join(chunk), redirects=1)
            q = r.get("query", {})
            norm_map = {d["from"]: d["to"] for d in q.get("normalized", [])}
            redir = {d["from"]: d["to"] for d in q.get("redirects", [])}
            pages = {p["title"]: p for p in q.get("pages", []) if "revisions" in p}
            for orig in chunk:
                t = norm_map.get(orig, orig)
                t = redir.get(t, t)
                if t in pages:
                    got[norm(orig)] = {"title": t,
                                       "content": pages[t]["revisions"][0]["slots"]["main"]["content"]}
            time.sleep(0.2)

        still = []
        for s in fetch_queue:
            found = None
            for c in candidates(s["name"])[:2]:
                if norm(c) in got:
                    found = got[norm(c)]; break
            if found:
                sport, seasons = sport_and_seasons(found["content"])
                s["sport"] = sport
                s["seasons"] = seasons
                s["player"] = found["title"]
                resolved += 1
            else:
                still.append(s)
        unresolved = still

    # terrace / other songs carry no sport or seasons
    for s in songs:
        if s["category"] != "שירי שחקנים":
            s["sport"] = None
            s["seasons"] = []

    json.dump(data, open(SONGS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    from collections import Counter
    print(f"\nresolved total: {resolved} / {len(players)}", file=sys.stderr)
    print("sport split:", Counter(s.get("sport") for s in players), file=sys.stderr)
    if unresolved:
        print(f"\nunresolved ({len(unresolved)}):", file=sys.stderr)
        for s in unresolved:
            print("   ", s["name"], file=sys.stderr)


if __name__ == "__main__":
    main()
