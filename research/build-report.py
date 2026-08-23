#!/usr/bin/env python3
"""
Build game/found.html — a review page listing every song that now has an
original tune, with clickable links and how each one was identified.

    python3 build-report.py    ->  http://localhost:8790/found.html
"""
import collections
import html
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

HOW = {
    "wiki-field": ("משדה “שיר מקורי” בוויקי", "w"),
    "search": ("נמצא בחיפוש ביוטיוב", "s"),
    "trim": ("היה תקין — צומצם לקישור אחד", "t"),
}

c = sqlite3.connect(f"file:{ROOT}/data/hapoel.db?mode=ro", uri=True)
c.row_factory = sqlite3.Row
songs = {r["id"]: dict(r) for r in c.execute("SELECT * FROM songs")}
links = collections.defaultdict(list)
for r in c.execute("SELECT * FROM links ORDER BY song_id, pos, id"):
    links[r["song_id"]].append(dict(r))
c.close()

how_by_id, conf_by_id = {}, {}
try:
    for a in json.load(open(f"{HERE}/fixes.json", encoding="utf-8"))["actions"]:
        how_by_id[a["id"]] = a["how"]
        if "confidence" in a:
            conf_by_id[a["id"]] = a["confidence"]
except FileNotFoundError:
    pass

rows = []
for sid, s in songs.items():
    orig = [l for l in links[sid] if l["original"]]
    if not orig:
        continue
    rows.append({
        "name": s["name"],
        "cat": (s["category"] or "").replace("קטגוריה:", ""),
        "artist": s["artist"],
        "wiki": s["wiki_url"],
        "vid": orig[0]["video_id"],
        "title": orig[0]["label"] or "",
        "extra": len(links[sid]) - 1,
        "how": how_by_id.get(sid, ""),
        "conf": conf_by_id.get(sid),
    })
rows.sort(key=lambda r: (r["cat"], r["name"]))

counts = collections.Counter(r["how"] for r in rows)
low = [r for r in rows if r["conf"] is not None and r["conf"] < 0.8]

def td(r):
    badge = ""
    if r["how"] in HOW:
        label, cls = HOW[r["how"]]
        badge = f'<span class="tag tag--{cls}">{html.escape(label)}</span>'
    conf = f'<span class="conf">{r["conf"]}</span>' if r["conf"] is not None else ""
    warn = ' class="warn"' if (r["conf"] is not None and r["conf"] < 0.8) else ""
    artist = f'<span class="art">{html.escape(r["artist"])}</span>' if r["artist"] else ""
    extra = f'<span class="extra">+{r["extra"]} קישורים</span>' if r["extra"] > 0 else ""
    return f"""<tr{warn}>
  <td class="n"><b>{html.escape(r['name'])}</b>{artist}{extra}</td>
  <td class="c">{html.escape(r['cat'])}</td>
  <td class="h">{badge}{conf}</td>
  <td class="l">
    <a href="https://www.youtube.com/watch?v={r['vid']}" target="_blank" rel="noopener">▶ יוטיוב</a>
    {f'<a href="{html.escape(r["wiki"])}" target="_blank" rel="noopener">ויקיפועל</a>' if r['wiki'] else ''}
    <span class="ttl">{html.escape(r['title'][:70])}</span>
  </td>
</tr>"""

doc = f"""<!doctype html>
<html lang="he" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>השירים שנמצאו — הפועל שרים</title>
<link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700&family=Heebo:wght@400;700;900&display=swap" rel="stylesheet">
<style>
:root{{--red:#E2001A;--ink:#0C0C0E;--ink2:#16161A;--ink3:#1F1F25;--line:#2C2C34;--white:#F6F5F3;--grey:#9A9AA4;--green:#20A96A}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--ink);color:var(--white);font-family:Assistant,system-ui,sans-serif;padding:clamp(16px,3vw,40px)}}
h1{{font-family:Heebo;font-weight:900;font-size:clamp(1.8rem,5vw,2.8rem);letter-spacing:-.02em}}
.sub{{color:var(--grey);margin:8px 0 22px}}
.stats{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px}}
.stat{{background:var(--ink2);border:1px solid var(--line);border-radius:12px;padding:12px 18px}}
.stat b{{display:block;font-family:Heebo;font-weight:900;font-size:1.7rem;color:var(--red)}}
.stat span{{font-size:.8rem;color:var(--grey)}}
.tools{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}}
.tools input{{flex:1;min-width:200px;background:var(--ink2);border:1.5px solid var(--line);color:var(--white);border-radius:9px;padding:11px 14px}}
.tools input:focus{{border-color:var(--red);outline:none}}
.tools button{{background:none;border:1px solid var(--line);color:var(--grey);border-radius:9px;padding:10px 15px;font:inherit;font-weight:700;cursor:pointer}}
.tools button:hover,.tools button[aria-pressed=true]{{border-color:var(--red);color:var(--white)}}
table{{width:100%;border-collapse:collapse;background:var(--ink2);border:1px solid var(--line);border-radius:12px;overflow:hidden}}
th{{background:var(--ink3);font-family:Heebo;font-size:.7rem;letter-spacing:.12em;color:var(--grey);text-align:start;padding:11px 12px}}
td{{padding:11px 12px;border-top:1px solid var(--line);vertical-align:top;font-size:.92rem}}
tr.warn td{{background:rgba(226,0,26,.07)}}
.n b{{font-weight:700}}
.art{{display:block;font-size:.75rem;color:var(--red);margin-top:2px}}
.extra{{display:block;font-size:.7rem;color:var(--grey);margin-top:2px}}
.c{{color:var(--grey);font-size:.8rem;white-space:nowrap}}
.tag{{display:inline-block;font-size:.65rem;font-family:Heebo;border-radius:999px;padding:2px 8px;white-space:nowrap}}
.tag--w{{color:#7fd6a3;border:1px solid #2c6b48}}
.tag--s{{color:#f0c86a;border:1px solid #6b5423}}
.tag--t{{color:var(--grey);border:1px solid var(--line)}}
.conf{{display:inline-block;margin-inline-start:6px;font-family:Heebo;font-size:.7rem;color:var(--grey)}}
.l a{{color:var(--white);text-decoration:none;font-weight:700;font-size:.85rem;border-bottom:2px solid var(--red);margin-inline-end:10px}}
.l a:hover{{color:var(--red)}}
.ttl{{display:block;color:var(--grey);font-size:.72rem;margin-top:4px}}
.note{{background:#3a2a00;border:1px solid #7a5c00;color:#f0d68a;border-radius:10px;padding:12px 15px;margin-bottom:18px;font-size:.9rem}}
</style></head><body>
<h1>השירים שנמצאו</h1>
<p class="sub">כל שיר שיש לו כעת קישור לשיר המקורי — עם הקישור, המקור, ואיך הוא נמצא.</p>

<div class="stats">
  <div class="stat"><b>{len(rows)}</b><span>שירים עם מקור</span></div>
  <div class="stat"><b>{counts.get('wiki-field',0)}</b><span>משדה הוויקי</span></div>
  <div class="stat"><b>{counts.get('search',0)}</b><span>מחיפוש ביוטיוב</span></div>
  <div class="stat"><b>{counts.get('trim',0)}</b><span>היו תקינים</span></div>
  <div class="stat"><b>{len(songs)-len(rows)}</b><span>עדיין ללא מקור</span></div>
</div>

{'<p class="note">שתי שורות מסומנות באדום נמצאו בחיפוש בביטחון נמוך — כדאי להאזין ולוודא.</p>' if low else ''}

<div class="tools">
  <input id="q" type="search" placeholder="חיפוש שיר, מקור או קטגוריה…">
  <button data-f="all" aria-pressed="true">הכל</button>
  <button data-f="s">רק מחיפוש</button>
  <button data-f="warn">רק לבדיקה</button>
</div>

<table><thead><tr><th>שיר</th><th>קטגוריה</th><th>איך נמצא</th><th>קישורים</th></tr></thead>
<tbody id="tb">
{chr(10).join(td(r) for r in rows)}
</tbody></table>

<script>
const rows=[...document.querySelectorAll('#tb tr')];
let mode='all';
const FIN={{'ך':'כ','ם':'מ','ן':'נ','ף':'פ','ץ':'צ'}};
const norm=s=>s.toLowerCase().replace(/[ךםןףץ]/g,c=>FIN[c]).replace(/["'׳״]/g,'');
function apply(){{
  const q=norm(document.getElementById('q').value.trim());
  rows.forEach(r=>{{
    const okQ=!q||norm(r.textContent).includes(q);
    const okM=mode==='all'||(mode==='warn'&&r.classList.contains('warn'))
             ||(mode==='s'&&r.querySelector('.tag--s'));
    r.style.display=(okQ&&okM)?'':'none';
  }});
}}
document.getElementById('q').addEventListener('input',apply);
document.querySelectorAll('.tools button').forEach(b=>b.addEventListener('click',()=>{{
  document.querySelectorAll('.tools button').forEach(x=>x.setAttribute('aria-pressed','false'));
  b.setAttribute('aria-pressed','true'); mode=b.dataset.f; apply();
}}));
</script>
</body></html>"""

out = os.path.join(ROOT, "public", "found.html")
open(out, "w", encoding="utf-8").write(doc)
print(f"{len(rows)} songs -> {os.path.relpath(out, ROOT)}")
print(f"  wiki-field={counts.get('wiki-field',0)} search={counts.get('search',0)} trim={counts.get('trim',0)}")
print(f"  low-confidence rows flagged: {len(low)}")
