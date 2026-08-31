# הפועל שרים — Hapoel Sings

A "name that tune" party game built on the songs of Hapoel Tel Aviv. A song
plays, players buzz in by name, the host marks them right or wrong.

Song titles and links only — for the words, follow
the wiki link shown when a song is revealed.

## Play

The site is static. Anything that serves a folder will do:

```bash
cd public && python3 -m http.server 8791     # http://localhost:8791
```

Needs an internet connection: the songs stream from YouTube. It must be served
over http — the YouTube player refuses to run from a `file://` page.

### A round

1. Enter the players (1–10). Names are remembered between sessions.
2. Optionally open **בחירת שירים** and untick songs you don't want tonight.
   Your selection is remembered per-browser.
3. Press **התחלה** — a random song plays, hidden so nobody can read the title.
4. Whoever recognises it: tap their card, or press their number key `1`–`9`.
   The music pauses and the song is revealed.
5. **צדק** = +1, **טעה** = −1. Then on to the next.

Also: pause/resume (`Space`), restart the clip, *אף אחד לא ידע* to reveal with
no score, *שיר אחר* to skip.

Songs never repeat — the list is shuffled once and dealt out.

## Adding a song

`public/songs.json` is the whole database. Three ways in, easiest first:

**1. On GitHub, in the browser.** Open `public/songs.json`, hit edit, add an
entry, commit. Vercel redeploys automatically.

```json
{
 "name": "שם השיר",
 "category": "שירים מהיציע",
 "artist": "מי מבצע את הלחן המקורי",
 "wiki": null,
 "youtube": ["dQw4w9WgXcQ"],
 "original": true
}
```

`youtube` accepts a bare video id *or* a full URL you pasted — the site reads
either.

**2. With the helper script**, which checks the video actually plays and
refuses duplicates:

```bash
python3 scripts/add-song.py "שם השיר" "https://youtu.be/VIDEOID" --artist "שם האמן"
git add -A && git commit -m "add song" && git push
```

**3. Check your work** before pushing:

```bash
python3 scripts/validate.py                 # structure, duplicates, ids
python3 scripts/validate.py --check-videos  # also asks YouTube if each still plays
```

## Layout

```
public/            the site Vercel serves
  index.html       the game
  songs.json       the song database — this is the file you edit
  a11y.js          נגישות widget + privacy notice, on every page
  wikimenu.js      ויקיפועל's mobile (Minerva) drawer menu, added at the
                   wiki's request when they linked the site — an exact copy
                   of their drawer, in their styling, on every page
  site.js          shared header/footer, generated — edit build-pages.py instead
scripts/           add-song, validate, export-db, server (local editor), backup
research/          how the list was built: scrapers, classifiers, reports
data/hapoel.db     SQLite copy used during curation, kept for provenance
```

`public/songs.json` is the source of truth. `data/hapoel.db` is an archive of
the curation work — if you ever edit it, re-export with
`python3 scripts/export-db.py`.

## Where the songs came from

Scraped from [ויקיפועל](https://wiki.red-fans.com) — every page under
`קטגוריה:שירים` and its subcategories — then filtered down by hand.

For 131 of the 143, the link is the **original tune** the terrace chant was
built on, not a crowd recording. Those were found by reading the wiki's
`|שיר מקורי=` and `|מנגינה=` infobox fields, and where the wiki only named a
tune, by searching YouTube and accepting a match only when the video title
matched that name. Every link was checked against YouTube before being kept.

`research/build-report.py` regenerates a local review page listing every song
with its source tune, flagging any matched at low confidence. It is not part
of the published site.

## Accessibility and privacy

Every page carries a floating **נגישות** button (`public/a11y.js`) offering text
scaling, high contrast, greyscale, link highlighting, a readable font and an
animation stop. Choices persist per-browser and the widget is fully keyboard
operable.

The site **sets no cookies of its own**. Player names, song exclusions and
accessibility settings live in `localStorage`, and Vercel Web Analytics is
cookieless. The one third party that can set cookies is the YouTube player, so
it is loaded from `youtube-nocookie.com` and a one-time notice bar says so
plainly rather than pretending to gate consent we don't need.

The four content pages are generated:

```bash
python3 scripts/build-pages.py      # rewrites site.css, site.js and the 4 pages
```

Edit `scripts/build-pages.py`, never the generated HTML — it will be overwritten.

## Link previews

`public/og.png` is the card shown when the URL is pasted into WhatsApp, Slack,
X or iMessage. It is committed, so a normal deploy never rebuilds it. If the
design changes:

```bash
python3 scripts/build-og.py     # renders scripts/og/card.html at 1200x630
```

Two things that silently break previews and are easy to reintroduce: `og:image`
must be an **absolute** URL (relative paths are ignored by every scraper), and
it must be a **raster** file — WhatsApp, Facebook and X all refuse SVG. The
card carries no song count on purpose, so it does not go stale when the list
changes.

Scrapers cache aggressively. After changing the image, re-scrape at
<https://developers.facebook.com/tools/debug/> to see it update.

## URLs and indexing

`cleanUrls` is deliberately **off** in `vercel.json`. Every internal link,
canonical and `og:url` in this site uses `.html`, so turning it on only put a
308 hop in front of each one and left every canonical pointing at a URL that
redirects. It also broke two things concretely: Google Search Console
verification, which fetches the exact `.html` path, and the footer's
current-page marker, which matches on the `.html` filename. Extensionless
URLs redirect to `.html` so old links keep working.

Note that `vercel.json` takes **no unknown keys** — its schema sets
`additionalProperties: false`, so a `"//"` comment key makes the whole file
invalid and the deployment silently fails. That is why this explanation lives
here and not in the file.

`robots.txt` and `sitemap.xml` are generated by `build-pages.py` from the same
`NAV` list as the pages, so they cannot drift out of sync.

## Deploying

Hosted on Vercel as a static site — no build step, no server.

1. Import the repo at [vercel.com/new](https://vercel.com/new)
2. Framework preset: **Other**. `vercel.json` already sets the output directory
   to `public`.
3. Deploy. Every push to `main` redeploys.

`main` is protected against **force pushes and deletion**, including for
admins. Ordinary pushes straight to `main` still work — no pull request and no
status checks are required, because the thing worth guarding here is the
history, not the workflow.

If you ever genuinely need to force push, lift the rule, push, then put it
back:

```bash
gh api -X DELETE repos/idanlodzki/hapoel-sings/branches/main/protection
# ... force push ...
gh api -X PUT repos/idanlodzki/hapoel-sings/branches/main/protection --input .github/branch-protection.json
```

## Note on content

This repository holds song **titles and links only**. Lyrics are not included
and are not republished — `wikitext-cache.json`, the local scrape of full wiki
page source, is deliberately excluded via `.gitignore`.
