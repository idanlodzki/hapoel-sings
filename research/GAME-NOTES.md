# הפועל שרים — buzzer quiz

A "name that tune" party game built on the 256 songs collected from ויקיפועל.
A Hapoel song plays, whoever recognises it first gets buzzed in, and the host
marks them right or wrong.

## Running it

```bash
python3 server.py               # from the project root -> http://localhost:8790
```

That serves the game *and* a small JSON API backed by SQLite, which is what
makes adding/editing/removing songs possible. A plain `python3 -m http.server`
inside `game/` still works, but the song list becomes read-only.

**Serve it over http — don't open `index.html` from disk.** The YouTube IFrame
player refuses to run from a `file://` origin.

## Editing the song list

With `server.py` running, the picker gains a **+ שיר חדש** button and every row
gets ✎ and ✕:

- **Add** — name, category, original artist, and one or more YouTube links.
- **Edit** — change the name, category, artist, or **swap the YouTube link**.
  Each link has a *מקורי* tick that controls whether it counts as the original
  tune, so you can fix a wrong classification here too.
- **Remove** — deletes the song and its links.

Links accept whatever you paste: a full `youtube.com/watch?v=…`, a `youtu.be/…`
short link, `/embed/`, `/shorts/`, or a bare 11-character video id.

Changes are written to `hapoel.db` and shared by everyone using that server —
unlike the *selection* of songs (the tick boxes), which stays per-browser in
localStorage.

An internet connection is required: the songs stream from YouTube.

## How a round goes

1. **Setup** — type in the players (1–10). Names are remembered for next time.
   Leave **רק השיר המקורי** ticked to play the tune each chant was built on
   (83 songs); untick it to include crowd recordings too (256 songs).
   Open **בחירת שירים** to drop songs you don't want: search, tick rows off,
   or use *סמן הכל* / *נקה הכל* / *היפוך*. Those three act only on whatever
   the search is currently showing, so you can clear a whole category in two
   clicks. Your exclusions are remembered between sessions.
2. **Start** — a random song begins playing. The video is deliberately kept
   off-screen so nobody can read the title; only the audio matters.
3. **Buzz** — tap a player's card, or press their number key (`1`–`9`).
   The music pauses and the song is revealed with links to its wiki page and
   to the recording — plus who performed the original, where the wiki says.
4. **Score** — *צדק* gives **+1**, *טעה* gives **−1**.
5. **Next** — on to the following song. Nothing repeats: the 256 songs are
   shuffled once and dealt out.

Other controls: pause/resume (or `Space`), restart the clip, *אף אחד לא ידע*
to reveal with no score, and *שיר אחר* to skip.

## Search and Hebrew final letters

The picker's search folds final-form letters onto their regular forms
(ך→כ, ם→מ, ן→נ, ף→פ, ץ→צ). Without that, typing `אדום` would never match
`אדומה שלי`, because the two mems are different characters. It also ignores
quotes, geresh and dashes, which the wiki uses inconsistently.

## Two things worth knowing

**A play button sometimes appears.** Browsers block audio that starts without a
click. The game normally starts the song inside your "Start" press, but if a
clip errors and it auto-advances to another one, that new song is outside the
click and gets blocked. When that happens a **▶ להפעלת השיר** button appears —
press it and play continues. This is browser policy, not a bug.

**Dead links are handled.** The links were scraped from a fan wiki, so some
videos are deleted or blocked from embedding. When one fails the game tries
another recording of the same song, and if none work it moves to a different
song and remembers not to try that clip again this session.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole game — markup, styles and logic |
| `songs-data.js` | Generated song list. Rebuild with `python3 ../build-game-data.py` |

The data holds song titles and video IDs only — no lyrics. To see the words,
follow the wiki link shown when a song is revealed.
