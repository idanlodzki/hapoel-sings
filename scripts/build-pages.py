#!/usr/bin/env python3
"""
Generate the site's content pages from one shared shell, so the header,
footer, metadata and styling stay identical across them.

    python3 scripts/build-pages.py

Writes public/{rules,accessibility,terms,privacy}.html and public/site.css.

NOTE: the legal and accessibility text here is a working draft written to be
accurate about what this site actually does. It is not legal advice — have it
reviewed before relying on it.
"""
import datetime
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "public")

# ---------------------------------------------------------------------------
# Site-wide constants. CONTACT is shown in the footer as an invitation to send
# in missing songs, and on the legal pages as the address for enquiries.
CONTACT = "idan.lut@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/idan-lodzki-755939157/"
OWNER = "הפועל שרים"
UPDATED = "אוגוסט 2026"
REPO = "https://github.com/idanlodzki/hapoel-sings"
SITE = "https://hapoel-sings.vercel.app"

NAV = [
    ("index.html", "המשחק"),
    ("rules.html", "כללי המשחק"),
    ("accessibility.html", "נגישות"),
    ("terms.html", "תנאי שימוש"),
    ("privacy.html", "פרטיות"),
]

CSS = """/* Shared shell for the content pages. The game keeps its own styles. */
:root{
  --red:#E2001A;--red-lite:#FF5A6E;--ink:#0C0C0E;--ink2:#16161A;--ink3:#1F1F25;
  --line:#2C2C34;--white:#F6F5F3;--grey:#A8A8B2;
  --f-d:"Heebo","Arial Hebrew",system-ui,sans-serif;
  --f-b:"Assistant","Arial Hebrew",system-ui,sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{animation:none!important;transition:none!important}}
body{background:var(--ink);color:var(--white);font-family:var(--f-b);font-size:17px;line-height:1.75;
  display:flex;flex-direction:column;min-height:100vh;-webkit-font-smoothing:antialiased}
h1,h2,h3{font-family:var(--f-d);font-weight:900;line-height:1.15;letter-spacing:-.02em}
a{color:var(--white)}
a:hover{color:var(--red-lite)}
:focus-visible{outline:3px solid var(--red-lite);outline-offset:3px;border-radius:4px}
.skip{position:absolute;inset-inline-start:-9999px;top:0;background:var(--white);color:var(--ink);
  padding:12px 20px;z-index:99;font-weight:700}
.skip:focus{inset-inline-start:0}
.wrap{width:100%;max-width:820px;margin-inline:auto;padding:0 20px}

header.top{border-bottom:1px solid var(--line);background:var(--ink2)}
.top__in{display:flex;align-items:center;gap:14px;flex-wrap:wrap;padding:14px 0}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;font-family:var(--f-d);font-weight:900;font-size:1.2rem}
.brand img{width:34px;height:34px}
.top__in{position:relative}
.top__actions{display:flex;gap:8px;align-items:center;margin-inline-start:auto}
.btn-play{
  display:inline-flex;align-items:center;gap:7px;background:var(--red);color:#fff;
  text-decoration:none;font-weight:700;font-size:.92rem;padding:9px 16px;border-radius:8px;
  white-space:nowrap;transition:background .15s
}
.btn-play:hover{background:#b30015;color:#fff}
.menu-btn{
  display:inline-flex;align-items:center;gap:8px;background:none;color:var(--grey);
  border:1px solid var(--line);border-radius:8px;padding:9px 14px;font:inherit;
  font-size:.9rem;font-weight:600;cursor:pointer;white-space:nowrap
}
.menu-btn:hover,.menu-btn[aria-expanded=true]{color:var(--white);border-color:var(--grey)}
.menu-btn__ico{width:15px;height:11px;position:relative;display:inline-block}
.menu-btn__ico::before,.menu-btn__ico::after,.menu-btn__ico span{content:"";position:absolute;
  inset-inline:0;height:2px;background:currentColor;border-radius:2px}
.menu-btn__ico::before{top:0}
.menu-btn__ico::after{bottom:0}
.menu-btn[aria-expanded=true] .menu-btn__ico::before{top:4.5px}
.menu-btn[aria-expanded=true] .menu-btn__ico::after{bottom:4.5px}
.menu{
  position:absolute;top:calc(100% + 8px);inset-inline-end:0;z-index:40;min-width:210px;
  background:var(--ink3);border:1px solid var(--line);border-radius:12px;padding:6px;
  display:flex;flex-direction:column;box-shadow:0 14px 40px rgba(0,0,0,.55)
}
.menu[hidden]{display:none}
.menu a{text-decoration:none;color:var(--grey);font-size:.94rem;font-weight:600;
  padding:10px 13px;border-radius:8px}
.menu a:hover{color:var(--white);background:var(--ink2)}
.menu a[aria-current=page]{color:var(--white);background:var(--ink2)}
.menu a[aria-current=page]::after{content:" ●";color:var(--red);font-size:.7em}
@media (max-width:520px){
  .btn-play span[aria-hidden]{display:none}
  .top__in{padding:11px 0}
  .brand{font-size:1.05rem}
}

main{flex:1;padding:clamp(28px,5vw,56px) 0}
main h1{font-size:clamp(1.9rem,5vw,2.7rem);margin-bottom:10px}
main .lede{color:var(--grey);font-size:1.05rem;margin-bottom:34px}
main h2{font-size:1.3rem;margin:34px 0 10px}
main h3{font-size:1.05rem;margin:22px 0 6px;font-weight:700}
main p{margin-bottom:14px}
main ul,main ol{margin:0 0 16px;padding-inline-start:22px}
main li{margin-bottom:7px}
main strong{font-weight:700}
code{background:var(--ink3);border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-size:.88em}
.box{background:var(--ink2);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:20px 0}
.box--warn{background:#3a2a00;border-color:#7a5c00;color:#f0d68a}
.updated{color:var(--grey);font-size:.85rem;border-top:1px solid var(--line);padding-top:16px;margin-top:36px}
.steps{counter-reset:s;list-style:none;padding:0}
.steps li{counter-increment:s;position:relative;padding-inline-start:42px;margin-bottom:14px}
.steps li::before{content:counter(s);position:absolute;inset-inline-start:0;top:2px;width:28px;height:28px;
  border-radius:50%;background:var(--red);color:#fff;font-family:var(--f-d);font-weight:900;font-size:.85rem;
  display:grid;place-items:center}

footer.site{border-top:1px solid var(--line);background:var(--ink2);padding:26px 0;font-size:.88rem;color:var(--grey)}
.foot__links{display:flex;gap:8px 18px;flex-wrap:wrap;margin-bottom:14px}
.foot__links a{color:var(--grey);text-decoration:none}
.foot__links a:hover{color:var(--red-lite);text-decoration:underline}
.foot__links .foot__icon{display:inline-flex;align-items:center;color:var(--grey)}
.foot__links .foot__icon:hover{color:var(--red-lite)}
.foot__help{margin-bottom:14px;color:var(--white)}
.foot__help a{color:var(--red-lite);text-decoration:underline;text-underline-offset:3px}
.foot__help a:hover{color:var(--white)}
.btn-consent{background:var(--red);color:#fff;border:0;border-radius:9px;padding:11px 22px;
  font:inherit;font-weight:700;cursor:pointer}
.btn-consent:hover{background:#b30015}
.foot__legal{display:flex;gap:10px 20px;flex-wrap:wrap;align-items:center;justify-content:space-between}
"""

FOOT_JS = """/* One footer, injected everywhere — including into the game, which has its
   own stylesheet and so gets inline styles here rather than the shared CSS. */
(function () {
  var LINKS = %LINKS%;
  var here = location.pathname.split("/").pop() || "index.html";
  var html =
    '<div class="wrap">' +
      '<div class="foot__links">' +
        LINKS.map(function (l) {
          return '<a href="' + l[0] + '"' + (l[0] === here ? ' aria-current="page"' : '') + '>' + l[1] + '</a>';
        }).join('') +
        '<a href="%REPO%" target="_blank" rel="noopener">קוד המקור</a>' +
        '<a class="foot__icon" href="%LINKEDIN%" target="_blank" rel="noopener"' +
          ' aria-label="LinkedIn" title="LinkedIn">' +
          '<svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true">' +
          '<path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3.2 9h3.6v12H3.2zM9.4 9H13v1.7h.05c.5-.95 1.75-1.95 3.6-1.95 3.85 0 4.56 2.5 4.56 5.77V21h-3.8v-5.5c0-1.31-.03-3-1.85-3-1.85 0-2.13 1.43-2.13 2.9V21H9.4z"/>' +
          '</svg>' +
        '</a>' +
      '</div>' +
      '<div class="foot__help">' +
        'שכחתי שיר? <a href="mailto:%EMAIL%?subject=%SUBJ%&amp;body=%BODY%">' +
        'עזרו לי להוסיף אותו</a>' +
      '</div>' +
      '<div class="foot__legal">' +
        '<span>© %OWNER% · אתר לא רשמי, ללא קשר למועדון הפועל תל אביב</span>' +
        '<span>השירים והסרטונים שייכים לבעליהם — כאן יש קישורים בלבד</span>' +
      '</div>' +
    '</div>';
  document.addEventListener("DOMContentLoaded", function () {
    var f = document.createElement("footer");
    f.className = "site";
    f.innerHTML = html;
    if (!document.querySelector("link[href='site.css']")) {
      // inside the game: borrow its palette instead of the shared sheet
      f.setAttribute("style",
        "border-top:1px solid #2C2C34;background:#16161A;padding:22px 0;" +
        "font-size:.85rem;color:#A8A8B2;font-family:Assistant,system-ui,sans-serif");
      f.querySelectorAll = f.querySelectorAll || function(){return []};
    }
    document.body.appendChild(f);
    f.querySelectorAll(".foot__links a").forEach(function (a) {
      if (!a.style.color) { a.style.color = "inherit"; a.style.textDecoration = "none"; }
    });
    var w = f.querySelector(".wrap");
    if (w && !document.querySelector("link[href='site.css']")) {
      w.setAttribute("style", "max-width:1100px;margin-inline:auto;padding:0 20px");
      f.querySelector(".foot__links").setAttribute("style", "display:flex;gap:8px 18px;flex-wrap:wrap;align-items:center;margin-bottom:10px");
      f.querySelector(".foot__help").setAttribute("style", "margin-bottom:12px;color:#F6F5F3");
      var hl = f.querySelector(".foot__help a");
      if (hl) { hl.style.color = "#FF5A5A"; hl.style.textDecoration = "underline"; hl.style.textUnderlineOffset = "3px"; }
      var ic = f.querySelector(".foot__icon");
      // set properties, not the whole attribute: the colour pass above already
      // wrote to this element and setAttribute would wipe it back to link-blue
      if (ic) { ic.style.display = "inline-flex"; ic.style.alignItems = "center"; }
      f.querySelector(".foot__legal").setAttribute("style", "display:flex;gap:8px 20px;flex-wrap:wrap;justify-content:space-between");
    }
  });

  /* Small page menu. Closes on Escape, on outside click, and moves focus back
     to the button so keyboard users are not stranded inside it. */
  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("menuBtn");
    var menu = document.getElementById("pagemenu");
    if (!btn || !menu) return;
    function set(open) {
      btn.setAttribute("aria-expanded", String(open));
      menu.hidden = !open;
    }
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      set(menu.hidden);
    });
    document.addEventListener("click", function (e) {
      if (!menu.hidden && !menu.contains(e.target) && e.target !== btn) set(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !menu.hidden) { set(false); btn.focus(); }
    });
  });
})();
"""


def shell(slug, title, desc, body):
    nav = "".join(
        '<a href="%s"%s role="menuitem">%s</a>' % (h, ' aria-current="page"' if h == slug else "", t)
        for h, t in NAV
    )
    # the game is the point of the site; on every other page it gets a real
    # button rather than being one link among six
    play = "" if slug == "index.html" else (
        '<a class="btn-play" href="index.html">'
        '<span aria-hidden="true">▶</span> חזרה למשחק</a>'
    )
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — הפועל שרים</title>
<meta name="description" content="{desc}">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="canonical" href="{SITE}/{slug}">

<!-- Link preview. og:image must be an absolute URL to a raster file:
     WhatsApp, Facebook and X all refuse to render SVG previews. -->
<meta property="og:site_name" content="הפועל שרים">
<meta property="og:locale" content="he_IL">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}/{slug}">
<meta property="og:title" content="{title} — הפועל שרים">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/og.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="הפועל שרים — משחק ניחוש שירים">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title} — הפועל שרים">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}/og.png">
<meta name="theme-color" content="#0C0C0E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700&family=Heebo:wght@400;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="site.css">
<script defer src="/_vercel/insights/script.js"></script>
</head>
<body>
<a class="skip" href="#main">דילוג לתוכן</a>
<header class="top">
  <div class="wrap top__in">
    <a class="brand" href="index.html"><img src="logo.svg" alt="" width="34" height="34">הפועל שרים</a>
    <div class="top__actions">
      {play}
      <button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="pagemenu" aria-haspopup="true">
        <span class="menu-btn__ico" aria-hidden="true"></span> תפריט
      </button>
    </div>
    <nav class="menu" id="pagemenu" aria-label="ניווט באתר" role="menu" hidden>{nav}</nav>
  </div>
</header>
<main id="main"><div class="wrap">
{body}
<p class="updated">עודכן לאחרונה: {UPDATED}</p>
</div></main>
<script src="stats.js"></script>
<script src="clarity.js"></script>
<script src="site.js"></script>
<script src="a11y.js"></script>
</body>
</html>
"""


PAGES = {}

PAGES["rules.html"] = ("כללי המשחק", "איך משחקים בהפועל שרים — חוקי המשחק, הניקוד והכפתורים.", f"""
<h1>כללי המשחק</h1>
<p class="lede">שיר של הפועל מתנגן. מי שמזהה אותו ראשון — מנקד.</p>

<h2>לפני שמתחילים</h2>
<ol class="steps">
  <li>מזינים את שמות המשתתפים — בין אחד לעשרה. השמות נשמרים לפעם הבאה.</li>
  <li>אפשר לפתוח את <strong>בחירת שירים</strong> ולבטל סימון של שירים שלא רוצים הערב. הבחירה נשמרת בדפדפן שלכם בלבד.</li>
  <li>לוחצים <strong>התחלה</strong>.</li>
</ol>

<h2>מהלך סיבוב</h2>
<ol class="steps">
  <li>שיר אקראי מתחיל להתנגן. הסרטון מוסתר בכוונה — שומעים בלבד, אי אפשר לקרוא את השם.</li>
  <li>מי שמזהה לוחץ על הכרטיס עם שמו, או מקיש על הספרה שלו במקלדת (<code>1</code>–<code>9</code>).</li>
  <li>המוזיקה נעצרת והשיר נחשף, יחד עם קישור לדף שלו בוויקיפועל ולסרטון.</li>
  <li>המנחה מכריע: <strong>צדק</strong> או <strong>טעה</strong>.</li>
</ol>

<h2>ניקוד</h2>
<ul>
  <li><strong>צדק — נקודה אחת (+1).</strong></li>
  <li><strong>טעה — נקודה פחות (−1).</strong> זה מה שהופך לחיצה מוקדמת להימור אמיתי.</li>
  <li>מי שלא לחץ — לא מרוויח ולא מפסיד.</li>
</ul>

<h2>כפתורים נוספים</h2>
<ul>
  <li><strong>השהיה</strong> — עצירה והמשך. אפשר גם עם מקש הרווח.</li>
  <li><strong>מהתחלה</strong> — משמיע את הקטע שוב מתחילתו.</li>
  <li><strong>אף אחד לא ידע</strong> — חושף את השיר בלי לתת או להוריד נקודות.</li>
  <li><strong>שיר אחר</strong> — מדלג לשיר הבא.</li>
</ul>

<h2>דברים ששווה לדעת</h2>
<ul>
  <li>שירים לא חוזרים על עצמם: הרשימה מעורבבת פעם אחת ומחולקת עד שנגמרת.</li>
  <li>לרוב השירים הקישור הוא ל<strong>לחן המקורי</strong> שממנו נולד השיר ביציע — ולא להקלטה מהמגרש.</li>
  <li>אם סרטון נמחק מיוטיוב, המשחק מדלג אליו הלאה מעצמו.</li>
  <li>לפעמים יופיע כפתור <strong>להפעלת השיר</strong> — הדפדפן חוסם ניגון שלא התחיל מלחיצה. לחיצה אחת פותרת.</li>
</ul>
""")

PAGES["accessibility.html"] = ("הצהרת נגישות", "הצהרת הנגישות של אתר הפועל שרים — מה נעשה, מה המגבלות הידועות, ואיך לפנות אלינו.", f"""
<h1>הצהרת נגישות</h1>
<p class="lede">אנחנו רוצים שכל אחד יוכל להשתמש באתר. זה מה שעשינו, וזה מה שעדיין לא מושלם.</p>

<h2>כלי הנגישות באתר</h2>
<p>
  בכל עמוד, בפינה התחתונה, יש כפתור נגישות (הסמל הכחול). לחיצה עליו פותחת תפריט שמאפשר:
</p>
<ul>
  <li><strong>הגדלה והקטנה של הטקסט</strong> — בין 80% ל-150%.</li>
  <li><strong>ניגודיות גבוהה</strong> — רקע שחור, טקסט לבן וקישורים בצהוב.</li>
  <li><strong>גווני אפור</strong> — למי שצבעים מקשים עליו.</li>
  <li><strong>הדגשת קישורים</strong> — קו תחתון ומסגרת סביב כל קישור.</li>
  <li><strong>גופן קריא</strong> — מעבר לגופן פשוט עם ריווח אותיות מוגדל.</li>
  <li><strong>עצירת אנימציות</strong> — לכל התנועה באתר.</li>
</ul>
<p>ההגדרות נשמרות בדפדפן שלכם ונשארות גם בביקור הבא. אפשר לאפס אותן בכל רגע מאותו תפריט.</p>

<h2>מה נעשה באתר</h2>
<ul>
  <li>האתר בנוי בעברית עם כיווניות <code>rtl</code> מלאה.</li>
  <li>אפשר להפעיל את כל המשחק <strong>מהמקלדת בלבד</strong>: מעבר בין רכיבים ב-Tab, ניקוד לשחקנים בספרות <code>1</code>–<code>9</code>, השהיה ברווח.</li>
  <li>לכל רכיב אינטראקטיבי יש סימון מיקוד (focus) ברור ובניגודיות גבוהה.</li>
  <li>לכפתורים ולשדות יש תוויות טקסט או <code>aria-label</code> לקוראי מסך.</li>
  <li>יש קישור "דילוג לתוכן" בתחילת כל עמוד.</li>
  <li>מי שהגדיר במערכת ההפעלה שלו העדפה לצמצום תנועה — לא יקבל אנימציות.</li>
  <li>כפתור הנגישות עצמו נגיש מהמקלדת, נסגר במקש Escape ומחזיר את המיקוד למקומו.</li>
  <li>הטקסט ניתן להגדלה בדפדפן בלי שהתוכן יישבר.</li>
</ul>

<h2>מגבלות ידועות</h2>
<p>חשוב לנו לומר את זה בכנות ולא להצהיר על יותר ממה שיש:</p>
<ul>
  <li><strong>נגן היוטיוב</strong> מוטמע מגורם שלישי. אין לנו שליטה על הנגישות שלו, ולא על קיומן של כתוביות בסרטונים.</li>
  <li><strong>לסרטונים אין תמלול או כתוביות</strong> מטעמנו. המשחק מבוסס על האזנה, ולכן אינו מתאים במתכונתו הנוכחית למי שאינו שומע.</li>
  <li>האתר לא נבדק בביקורת נגישות חיצונית ולא נבדק מול כל קוראי המסך הקיימים.</li>
</ul>

<h2>נתקלתם בבעיה?</h2>
<p>
  אם משהו באתר לא נגיש עבורכם — נשמח לדעת ונתקן. אפשר לפנות לכתובת:
  <strong>{CONTACT}</strong>
</p>
<p>אפשר גם לפתוח פנייה ישירות ב<a href="{REPO}/issues" target="_blank" rel="noopener">מאגר הקוד</a>.</p>
""")

PAGES["terms.html"] = ("תנאי שימוש", "תנאי השימוש באתר הפועל שרים.", f"""
<h1>תנאי שימוש</h1>
<p class="lede">אתר חובבים, בחינם, ללא מטרות רווח.</p>

<h2>מה האתר הזה</h2>
<p>
  "הפועל שרים" הוא משחק ניחוש שירים לחובבי הפועל תל אביב. השימוש בו חופשי וללא תשלום.
</p>
<div class="box">
  <strong>אתר עצמאי.</strong> האתר אינו רשמי, ואין לו שום קשר, שיוך או חסות מטעם מועדון
  הפועל תל אביב, ויקיפועל, יוטיוב או כל גורם אחר.
</div>

<h2>תכנים וזכויות</h2>
<ul>
  <li>האתר <strong>אינו מארח מוזיקה, סרטונים או מילות שירים</strong>.</li>
  <li>כל שנשמר כאן הוא <strong>שמות שירים וקישורים</strong>. הסרטונים מתנגנים ישירות מיוטיוב, בנגן שלהם.</li>
  <li>הזכויות בשירים, בהקלטות ובסרטונים שייכות לבעליהן. אין לנו כל טענה לבעלות עליהם.</li>
  <li>המידע על השירים נאסף מוויקיפועל, אתר חובבים פתוח.</li>
  <li>אם אתם בעלי זכויות ומשהו כאן מפריע לכם — פנו אלינו וזה יוסר.</li>
</ul>

<h2>שימוש הוגן</h2>
<ul>
  <li>מותר להשתמש באתר לשימוש אישי ולמשחק עם חברים.</li>
  <li>אין להשתמש באתר בדרך שפוגעת בו, בשרתיו או במשתמשים אחרים.</li>
  <li>קוד האתר פתוח וזמין ב<a href="{REPO}" target="_blank" rel="noopener">GitHub</a>.</li>
</ul>

<h2>ללא אחריות</h2>
<p>
  האתר ניתן כמות שהוא. איננו מתחייבים שיהיה זמין תמיד, שכל הקישורים יעבדו, או שהמידע
  על כל שיר מדויק — חלק מהמידע נאסף אוטומטית מוויקי פתוח ועשוי להכיל טעויות. סרטונים
  ביוטיוב עשויים להימחק בכל רגע ללא התראה.
</p>

<h2>שינויים</h2>
<p>ייתכן שנעדכן את התנאים מעת לעת. הגרסה העדכנית תופיע תמיד בעמוד הזה.</p>

<h2>יצירת קשר</h2>
<p>{CONTACT}</p>
""")

PAGES["privacy.html"] = ("מדיניות פרטיות", "איזה מידע נאסף באתר הפועל שרים, למה, ומה נשמר במכשיר שלכם.", f"""
<h1>מדיניות פרטיות</h1>
<p class="lede">בקצרה: אנחנו לא מבקשים מכם להירשם, לא אוספים שמות ולא שומרים כלום בשרת שלנו.</p>

<h2>עוגיות</h2>
<p>
  <strong>כל עוד לא אישרתם — האתר לא שומר אף עוגייה.</strong> אין עוגיות פרסום ואין
  רשתות מודעות, בשום מצב.
</p>
<p>
  אם <strong>אישרתם הקלטת סשנים</strong> (ראו למטה), שירות Microsoft Clarity שומר עוגיות
  משלו. זה קורה רק אחרי אישור מפורש, ואפשר לחזור מזה בכל רגע.
</p>
<p>
  בנוסף, נגן היוטיוב המוטמע: הטענו אותו במצב הפרטיות המוגבר
  (<code>youtube-nocookie.com</code>), אבל כששיר מתנגן בפועל <strong>גוגל עשויה לשמור
  עוגיות משלה</strong>. זה קורה מול גוגל ולא מולנו.
</p>

<h2>הקלטת סשנים — רק באישורכם</h2>
<p>
  כדי להבין איפה אנשים נתקעים במשחק, אנחנו רוצים להקליט את השימוש באתר באמצעות
  <strong>Microsoft Clarity</strong>: תנועות עכבר, לחיצות וגלילה. זה נעשה
  <strong>רק אם אישרתם</strong>, ואפשר לשחק במשחק במלואו בלי לאשר — שום דבר לא נחסם.
</p>
<p>
  <strong>שמות המשתתפים מוסתרים ואינם נשלחים.</strong> הסתרנו אותם בכל מקום שבו הם מופיעים
  על המסך — בשדות ההזנה, בכפתורי הניחוש, ברצועת הניקוד, בשורת "ניחש", בהודעות הקופצות
  ובטבלת הסיום. ההסתרה מתבצעת בדפדפן שלכם, כך שהשמות לא יוצאים מהמכשיר מלכתחילה.
</p>
<p>
  שימו לב: נגן היוטיוב עצמו אינו מוקלט כלל — הוא מוצג כמלבן ריק בהקלטה, ואין הקלטת קול.
</p>
<div class="box" id="consentBox"></div>
<p>
  Clarity הוא שירות של Microsoft, וחלים עליו
  <a href="https://privacy.microsoft.com/privacystatement" target="_blank" rel="noopener">תנאי הפרטיות של Microsoft</a>.
  אנחנו מתכוונים להשתמש בו לתקופה מוגבלת ולהסיר אותו לאחר מכן.
</p>
<h2>מה אנחנו מודדים</h2>
<p>
  אנחנו רוצים לדעת אם המשחק בכלל עובד בשביל אנשים — כמה משחקים מתחילים, כמה סיבובים
  שוחקו, ואילו סרטונים ביוטיוב הפסיקו לעבוד. לשם כך נספרות <strong>פעולות</strong>
  באתר: התחלת משחק, סיבוב שנוגן, תשובה נכונה או שגויה, דילוג על שיר ותקלה בנגן.
</p>
<p>
  <strong>מה שלא נשלח:</strong> שמות המשתתפים שהזנתם לא נשלחים לשום מקום — לעולם.
  הם נשארים בדפדפן שלכם בלבד. נשלח רק <em>מספר</em> המשתתפים, בלי השמות.
  אין מזהה אישי, אין עוגייה, ואי אפשר לקשר בין פעולה לאדם או בין ביקור לביקור.
</p>
<p>
  אם הגדרתם בדפדפן <code>Do Not Track</code>, לא נמדוד אתכם כלל.
</p>

<h2>מה נשמר במכשיר שלכם</h2>
<p>
  האתר משתמש ב-<code>localStorage</code> של הדפדפן. המידע הזה נשאר <strong>אצלכם</strong>,
  לא נשלח לשום מקום, ואפשר למחוק אותו בכל רגע דרך הגדרות הדפדפן:
</p>
<ul>
  <li><strong>שמות המשתתפים</strong> שהזנתם, כדי לא להקליד אותם מחדש בכל משחק.</li>
  <li><strong>רשימת השירים שביטלתם</strong>, כדי שהבחירה תישמר בין משחקים.</li>
  <li><strong>הגדרות הנגישות</strong> שבחרתם, ו<strong>הבחירה שלכם לגבי הקלטת סשנים</strong>.</li>
</ul>
<p>זה אחסון מקומי (<code>localStorage</code>), לא עוגיות — הוא לא נשלח לשרת בשום שלב.</p>

<h2>מדידת שימוש</h2>
<p>
  אנחנו משתמשים ב-<strong>Vercel Web Analytics</strong> כדי לדעת כמה אנשים נכנסו ואילו
  עמודים נצפו. השירות הזה נבחר בין היתר משום שהוא <strong>אינו משתמש בעוגיות</strong>
  ואינו בונה פרופיל אישי או מעקב חוצה-אתרים. נאסף מידע מצטבר בלבד, כמו מספר צפיות,
  סוג מכשיר ומדינה. איננו יכולים לזהות אתכם דרכו.
</p>

<h2>שירותים חיצוניים</h2>
<ul>
  <li><strong>יוטיוב</strong> — משמיע את השירים. חלים
    <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">תנאי הפרטיות של גוגל</a>.</li>
  <li><strong>Google Fonts</strong> — הגופנים של האתר נטענים משרתי גוגל, שרואים את כתובת ה-IP שלכם.</li>
  <li><strong>Vercel</strong> — מארחת את האתר ומודדת שימוש מצטבר, ללא עוגיות.</li>
  <li><strong>GoatCounter</strong> — סופר כמה אנשים נכנסו ואילו פעולות בוצעו באתר,
    <strong>ללא עוגיות וללא מזהים אישיים</strong>. שירות בקוד פתוח שנבחר בדיוק מהסיבה הזו.
    מכיוון שהוא אינו שומר דבר במכשיר שלכם, הוא פועל גם בלי אישור מיוחד.</li>
  <li><strong>Microsoft Clarity</strong> — מקליט סשנים, <strong>רק אם אישרתם</strong>.
    משתמש בעוגיות. ראו את הפרק על הקלטת סשנים למעלה.</li>
</ul>

<h2>מה איננו עושים</h2>
<ul>
  <li>אין הרשמה, אין חשבונות, אין סיסמאות.</li>
  <li>איננו מבקשים ואיננו שומרים אימייל, טלפון או כל פרט מזהה.</li>
  <li><strong>איננו מוכרים מידע לאף אחד</strong>, ואיננו משתפים מידע עם צד שלישי
    מלבד השירותים המפורטים בעמוד הזה.</li>
  <li>איננו שולחים את שמות המשתתפים לשום מקום.</li>
  <li>אין באתר עוגיות פרסום ואין רשתות מודעות.</li>
</ul>

<h2>יצירת קשר</h2>
<p>שאלה בנושא פרטיות? {CONTACT}</p>
""")


def write_seo():
    """robots.txt and sitemap.xml, built from NAV so they cannot drift.

    URLs carry .html to match the canonical tags exactly — a sitemap that
    lists URLs which redirect is a wasted crawl and a mixed signal."""
    today = datetime.date.today().isoformat()
    urls = []
    for slug, _ in NAV:
        loc = SITE + "/" + ("" if slug == "index.html" else slug)
        pri = "1.0" if slug == "index.html" else "0.6"
        urls.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today}</lastmod>\n"
            f"    <priority>{pri}</priority>\n  </url>"
        )
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "\n".join(urls) + "\n</urlset>\n")
    open(os.path.join(PUB, "sitemap.xml"), "w", encoding="utf-8").write(sitemap)

    robots = ("User-agent: *\n"
              "Allow: /\n\n"
              "# nothing here is private, but these are noise for a crawler\n"
              "Disallow: /songs.json\n\n"
              f"Sitemap: {SITE}/sitemap.xml\n")
    open(os.path.join(PUB, "robots.txt"), "w", encoding="utf-8").write(robots)
    print("wrote public/sitemap.xml, public/robots.txt")


def main():
    open(os.path.join(PUB, "site.css"), "w", encoding="utf-8").write(CSS)
    js = (FOOT_JS
          .replace("%LINKS%", repr([[h, t] for h, t in NAV]).replace("'", '"'))
          .replace("%REPO%", REPO)
          .replace("%LINKEDIN%", LINKEDIN)
          .replace("%EMAIL%", CONTACT)
          .replace("%SUBJ%", "%D7%94%D7%A4%D7%95%D7%A2%D7%9C%20%D7%A9%D7%A8%D7%99%D7%9D%20%E2%80%94%20%D7%A9%D7%99%D7%A8%20%D7%A9%D7%97%D7%A1%D7%A8%20%D7%91%D7%A8%D7%A9%D7%99%D7%9E%D7%94")
          .replace("%BODY%", "%D7%A9%D7%9D%20%D7%94%D7%A9%D7%99%D7%A8%3A%0A%D7%A7%D7%99%D7%A9%D7%95%D7%A8%20%D7%9C%D7%99%D7%95%D7%98%D7%99%D7%95%D7%91%3A%0A%0A%D7%AA%D7%95%D7%93%D7%94%21")
          .replace("%OWNER%", OWNER))
    open(os.path.join(PUB, "site.js"), "w", encoding="utf-8").write(js)

    for slug, (title, desc, body) in PAGES.items():
        open(os.path.join(PUB, slug), "w", encoding="utf-8").write(shell(slug, title, desc, body))
        print(f"wrote public/{slug}")
    print("wrote public/site.css, public/site.js")
    write_seo()


if __name__ == "__main__":
    main()
