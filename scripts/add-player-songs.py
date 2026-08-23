#!/usr/bin/env python3
"""
Pull this season's player chants off ויקיפועל and add them to the song list.

Every player page carries |מנגינת שיר שחקן=, the tune their chant borrows.
It comes in two shapes:

    |מנגינת שיר שחקן= איזה יום/דודו טסה                 -> "song/artist" text
    |מנגינת שיר שחקן= [https://youtu.be/xxx  שם השיר]   -> already a link

A link is used as-is once YouTube confirms it plays. Text is searched on
YouTube and the top hit accepted only if its title actually matches the tune
name — otherwise the player is reported and skipped rather than guessed at.

    python3 scripts/add-player-songs.py --season 2026/27           # dry run
    python3 scripts/add-player-songs.py --season 2026/27 --apply   # write
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "public", "songs.json")
API = "https://wiki.red-fans.com/api.php"
PAGE = "https://wiki.red-fans.com/index.php?title="
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")

FIELD = "מנגינת שיר שחקן"
VID = re.compile(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})")
HEB = re.compile(r"[֐-׿]")


def api(**p):
    p.setdefault("format", "json")
    p.setdefault("formatversion", "2")
    u = API + "?" + urllib.parse.urlencode(p)
    for a in range(4):
        try:
            return json.load(urllib.request.urlopen(
                urllib.request.Request(u, headers={"User-Agent": UA}), timeout=45))
        except Exception:
            if a == 3:
                return {}
            time.sleep(1.5 * (a + 1))
    return {}


def field_value(text):
    m = re.search(r"\|\s*" + re.escape(FIELD) + r"\s*=", text)
    if not m:
        return ""
    rest = text[m.end():]
    stop = re.search(r"\n\s*\|\s*[^=\n|]{1,28}=|\n?\}\}", rest)
    return (rest[: stop.start()] if stop else rest[:300]).strip()


def clean(s):
    s = re.sub(r"https?://\S+", " ", s or "")
    s = re.sub(r"\[|\]|\{\{[^}]*\}\}|'{2,}", " ", s)
    return re.sub(r"\s+", " ", s).strip(" -–—,.|")


OEMBED = "https://www.youtube.com/oembed?url=%s&format=json"


def yt_meta(vid):
    u = OEMBED % urllib.parse.quote(f"https://www.youtube.com/watch?v={vid}", safe="")
    try:
        with urllib.request.urlopen(
                urllib.request.Request(u, headers={"User-Agent": UA}), timeout=20) as r:
            d = json.loads(r.read().decode("utf-8"))
            return d.get("title", ""), d.get("author_name", "")
    except Exception:
        return None, None


def yt_search(q, n=4):
    hl = "he" if HEB.search(q) else "en"
    u = "https://www.youtube.com/results?" + urllib.parse.urlencode(
        {"search_query": q, "hl": hl})
    try:
        h = urllib.request.urlopen(urllib.request.Request(
            u, headers={"User-Agent": UA, "Accept-Language": hl}), timeout=30
        ).read().decode("utf-8", "ignore")
    except Exception:
        return []
    out, seen = [], set()
    for m in re.finditer(
        r'"videoRenderer":\{"videoId":"([A-Za-z0-9_-]{11})".*?"title":\{"runs":\[\{"text":"(.*?)"\}', h
    ):
        vid, title = m.group(1), m.group(2)
        try:
            title = json.loads('"' + title + '"')   # JSON escapes, not unicode_escape
        except Exception:
            pass
        if vid in seen:
            continue
        seen.add(vid)
        out.append((vid, title))
        if len(out) >= n:
            break
    return out


def norm(s):
    s = (s or "").lower()
    s = re.sub(r"[֑-ׇ]", "", s)
    return re.sub(r"\s+", " ", re.sub(r"[^\w֐-׿]+", " ", s)).strip()


def score(want, title):
    toks = [w for w in norm(want).split() if len(w) > 2]
    if not toks:
        return 0.0
    hay = norm(title)
    return sum(1 for w in toks if w in hay) / len(toks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", default="2026/27")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--threshold", type=float, default=0.5)
    a = ap.parse_args()

    print(f"reading squad page {a.season} …", file=sys.stderr)
    d = api(action="parse", page=a.season, prop="links")
    titles = [l["title"] for l in d.get("parse", {}).get("links", []) if l.get("ns") == 0]
    print(f"  {len(titles)} linked pages to check", file=sys.stderr)

    # a page is a player iff it carries the chant field
    players = []
    for i in range(0, len(titles), 40):
        chunk = titles[i:i + 40]
        r = api(action="query", prop="revisions", rvprop="content",
                rvslots="main", titles="|".join(chunk))
        for p in r.get("query", {}).get("pages", []):
            if "revisions" not in p:
                continue
            txt = p["revisions"][0]["slots"]["main"]["content"]
            v = field_value(txt)
            if v:
                players.append({"player": p["title"], "raw": v})
        time.sleep(0.3)
    print(f"  {len(players)} player pages carry {FIELD}\n", file=sys.stderr)

    existing = json.load(open(SONGS, encoding="utf-8"))
    have_names = {s["name"].strip() for s in existing["songs"]}
    have_vids = {v for s in existing["songs"] for v in s.get("youtube", [])}

    actions = []
    for p in players:
        raw, name = p["raw"], p["player"]
        tune = clean(raw)
        m = VID.search(raw)

        if m:                                   # the wiki already links it
            vid = m.group(1)
            title, chan = yt_meta(vid)
            if title is None:
                actions.append({**p, "how": "wiki-link-dead", "tune": tune})
                continue
            actions.append({**p, "how": "wiki-link", "vid": vid,
                            "title": title, "tune": tune or title})
            continue

        if not tune:
            actions.append({**p, "how": "no-tune"})
            continue

        # "song/artist" -> search both orderings, keep the best real match
        parts = [x.strip() for x in re.split(r"[/|]", tune) if x.strip()]
        queries = [tune] + ([" ".join(reversed(parts))] if len(parts) == 2 else [])
        best = None
        for q in queries:
            for vid, title in yt_search(q):
                sc = score(parts[0] if parts else tune, title)
                if sc >= a.threshold:
                    t2, _ = yt_meta(vid)
                    if t2 is not None:
                        best = (vid, title, sc)
                        break
            if best:
                break
            time.sleep(0.5)

        if best:
            actions.append({**p, "how": "search", "vid": best[0],
                            "title": best[1], "tune": tune, "conf": round(best[2], 2)})
        else:
            actions.append({**p, "how": "not-found", "tune": tune})

    # ---- decide what is actually new ----
    add, skip = [], []
    for x in actions:
        if x["how"] not in ("wiki-link", "search"):
            continue
        if x["player"].strip() in have_names:
            x["why"] = "already in songs.json"
            skip.append(x)
        elif x["vid"] in have_vids:
            x["why"] = "video already used"
            skip.append(x)
        else:
            add.append(x)

    by = {}
    for x in actions:
        by.setdefault(x["how"], []).append(x)
    print("found:")
    for k in ("wiki-link", "search", "not-found", "no-tune", "wiki-link-dead"):
        if k in by:
            print(f"  {k:16s} {len(by[k])}")
    print(f"\n  new to add      {len(add)}")
    print(f"  already present {len(skip)}")

    if add:
        print("\nwould add:")
        for x in add:
            c = f"  ({x['conf']})" if "conf" in x else ""
            print(f"  {x['player'][:24]:26s} {x['tune'][:32]:34s} -> {x['title'][:40]}{c}")
    for k in ("not-found", "no-tune", "wiki-link-dead"):
        if by.get(k):
            print(f"\n{k} (skipped):")
            for x in by[k]:
                print(f"  {x['player'][:24]:26s} {x.get('tune','')[:44]}")

    json.dump({"actions": actions}, open(os.path.join(ROOT, "player-songs.json"), "w",
              encoding="utf-8"), ensure_ascii=False, indent=1)

    if not a.apply:
        print("\ndry run — nothing written. re-run with --apply")
        return

    for x in add:
        artist = None
        parts = [p.strip() for p in re.split(r"[/|]", x["tune"]) if p.strip()]
        if len(parts) == 2:
            artist = parts[1]
        existing["songs"].append({
            "name": x["player"].strip(),
            "category": "שירי שחקנים",
            "artist": artist,
            "wiki": PAGE + urllib.parse.quote(x["player"].replace(" ", "_")),
            "youtube": [x["vid"]],
            "original": True,
        })
    existing["songs"].sort(key=lambda s: s["name"])
    existing["count"] = len(existing["songs"])
    json.dump(existing, open(SONGS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nadded {len(add)} songs -> {existing['count']} total")


if __name__ == "__main__":
    main()
