/* ============================================================
   תפריט ויקיפועל — an exact copy of wiki.red-fans.com's mobile
   (Minerva) drawer, added at the wiki's request as part of adding
   הפועל שרים as a page there.

   Deliberately styled like THEIR site, not ours: light panel,
   their metrics, their system font — so wiki readers recognise
   it instantly. Measured live from the wiki with ?useskin=minerva:
   320px panel, #eaecf0 ground, white link groups, 16px #54595d
   rows at 12px 15px padding, 12px #3366cc footer links, .25s
   slide, rgba(0,0,0,.35) -1px 0 8px shadow.

   Self-contained like a11y.js: injects its own CSS, builds its
   own DOM. Links open in a new tab so mid-game music survives.
   ============================================================ */
(function () {
  "use strict";

  var WIKI = "https://wiki.red-fans.com/index.php?title=";

  /* The drawer as it renders on their mobile site, verbatim. */
  var GROUPS = [
    [
      ["דף הבית", "עמוד_ראשי", "home"],
      ["אקראי", "מיוחד:אקראי", "die"],
    ],
    [
      ["שינויים אחרונים", "מיוחד:שינויים_אחרונים", "changes"],
      ["דפים מיוחדים", "מיוחד:דפים_מיוחדים", "pages"],
      ["שער הקהילה", "ויקיפועל:שער_הקהילה", "speech"],
    ],
    [
      ["העדפות", "מיוחד:העדפות", "gear"],
    ],
  ];
  var FOOT = [
    ["אודות ויקיפועל", "ויקיפועל:אודות"],
    ["הבהרות משפטיות", "ויקיפועל:הבהרות_משפטיות"],
  ];

  /* Monochrome recreations of Minerva's OOUI glyphs — inline, so
     nothing is hotlinked from their server. */
  var ICONS = {
    home:    '<path d="M10 1.5 1.5 9H4v9h4v-5h4v5h4V9h2.5z"/>',
    die:     '<path d="M3 3h14v14H3zm3.2 2A1.2 1.2 0 1 0 6.2 7.4 1.2 1.2 0 0 0 6.2 5zm7.6 0a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4zM10 8.8a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4zm-3.8 3.8a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4zm7.6 0a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4z" fill-rule="evenodd"/>',
    changes: '<path d="M3 4h14v2H3zm0 5h10v2H3zm0 5h14v2H3z"/>',
    pages:   '<path d="M5 1h7l4 4v13H5zm7 1v4h4zM7 9h6v1.5H7zm0 3h6v1.5H7z"/>',
    speech:  '<path d="M2 3h16v10H8l-4 4v-4H2z"/>',
    gear:    '<path d="M10 6.5A3.5 3.5 0 1 0 13.5 10 3.5 3.5 0 0 0 10 6.5zm8 4.9-2.1.6a6 6 0 0 1-.6 1.4l1.1 1.9-2.1 2.1-1.9-1.1a6 6 0 0 1-1.4.6L10.4 19H7.6L7 16.9a6 6 0 0 1-1.4-.6l-1.9 1.1-2.1-2.1 1.1-1.9a6 6 0 0 1-.6-1.4L0 11.4V8.6L2.1 8a6 6 0 0 1 .6-1.4L1.6 4.7l2.1-2.1 1.9 1.1A6 6 0 0 1 7 3.1L7.6 1h2.8l.6 2.1a6 6 0 0 1 1.4.6l1.9-1.1 2.1 2.1-1.1 1.9a6 6 0 0 1 .6 1.4l2.1.6z" transform="translate(1 -0.5) scale(0.9)"/>',
  };

  function svg(name) {
    return '<svg viewBox="0 0 20 20" width="20" height="20" fill="currentColor" aria-hidden="true">' +
           (ICONS[name] || "") + "</svg>";
  }

  /* ---------- styles: theirs, not ours ---------- */
  var FONT = '-apple-system,"system-ui","Segoe UI",Roboto,Lato,Helvetica,Arial,sans-serif';
  var css = document.createElement("style");
  css.textContent = [
    ".wm-burger{display:inline-flex;align-items:center;justify-content:center;cursor:pointer;",
    "background:none;border:0;padding:0;color:#54595d}",
    ".wm-burger svg{display:block}",
    /* in the content-page header it sits flush at the inline-start edge */
    ".wm-burger--head{width:38px;height:38px;border:1px solid var(--line,#2C2C34);border-radius:8px;",
    "color:var(--grey,#A8A8B2);margin-inline-end:2px}",
    ".wm-burger--head:hover{color:var(--white,#F6F5F3);border-color:var(--grey,#A8A8B2)}",
    /* on the game it floats as a light chip so it reads on the dark ground */
    ".wm-burger--float{position:fixed;top:14px;inset-inline-start:14px;z-index:8900;width:42px;height:42px;",
    "background:#eaecf0;border-radius:9px;color:#54595d;box-shadow:0 2px 10px rgba(0,0,0,.45)}",
    ".wm-burger--float:hover{background:#fff}",
    ".wm-scrim{position:fixed;inset:0;z-index:9400;background:rgba(0,0,0,.5);opacity:0;",
    "visibility:hidden;transition:opacity .25s ease-in-out,visibility .25s ease-in-out}",
    ".wm-scrim[data-open='true']{opacity:1;visibility:visible}",
    ".wm-drawer{position:fixed;top:0;bottom:0;inset-inline-start:0;z-index:9500;",
    "width:min(320px,90vw);background:#eaecf0;overflow-y:auto;overscroll-behavior:contain;",
    "box-shadow:rgba(0,0,0,.35) -1px 0 8px;font-family:" + FONT + ";",
    "transform:translateX(100%);visibility:hidden;",
    "transition:transform .25s ease-in-out,visibility .25s ease-in-out}",
    "[dir='ltr'] .wm-drawer{transform:translateX(-100%)}",
    ".wm-drawer[data-open='true']{transform:translateX(0);visibility:visible}",
    "@media (prefers-reduced-motion:reduce){.wm-drawer,.wm-scrim{transition:none}}",
    ".wm-drawer ul{list-style:none;margin:0 0 12px;padding:0;background:#fff}",
    ".wm-drawer ul:first-child{margin-top:0}",
    ".wm-drawer a.wm-item{display:flex;align-items:center;gap:12px;padding:12px 15px;",
    "font-size:16px;font-weight:400;color:#54595d;text-decoration:none}",
    ".wm-drawer a.wm-item:hover{background:#f8f9fa}",
    ".wm-drawer a.wm-item svg{flex:none;opacity:.85}",
    ".wm-foot{display:flex;gap:14px;flex-wrap:wrap;padding:10px 15px 20px}",
    ".wm-foot a{font-size:12px;color:#3366cc;text-decoration:none;font-family:" + FONT + "}",
    ".wm-foot a:hover{text-decoration:underline}",
    ".wm-burger:focus-visible,.wm-drawer a:focus-visible{outline:3px solid #36c;outline-offset:-3px}",
  ].join("");
  document.head.appendChild(css);

  /* ---------- DOM ---------- */
  function build() {
    var burger = document.createElement("button");
    burger.className = "wm-burger";
    burger.setAttribute("aria-label", "תפריט ויקיפועל");
    burger.setAttribute("aria-expanded", "false");
    burger.setAttribute("aria-controls", "wmDrawer");
    burger.innerHTML =
      '<svg viewBox="0 0 20 20" width="22" height="22" fill="currentColor" aria-hidden="true">' +
      '<path d="M2 4h16v2H2zm0 5h16v2H2zm0 5h16v2H2z"/></svg>';

    var head = document.querySelector("header.top .top__in");
    if (head) {
      burger.classList.add("wm-burger--head");
      head.insertBefore(burger, head.firstChild);
    } else {
      burger.classList.add("wm-burger--float");
      document.body.appendChild(burger);
    }

    var scrim = document.createElement("div");
    scrim.className = "wm-scrim";

    var drawer = document.createElement("nav");
    drawer.className = "wm-drawer";
    drawer.id = "wmDrawer";
    drawer.setAttribute("role", "dialog");
    drawer.setAttribute("aria-label", "תפריט ויקיפועל");
    drawer.setAttribute("data-open", "false");
    drawer.innerHTML =
      GROUPS.map(function (g) {
        return "<ul>" + g.map(function (it) {
          return '<li><a class="wm-item" href="' + WIKI + encodeURIComponent(it[1]) +
                 '" target="_blank" rel="noopener">' + svg(it[2]) +
                 "<span>" + it[0] + "</span></a></li>";
        }).join("") + "</ul>";
      }).join("") +
      '<div class="wm-foot">' + FOOT.map(function (it) {
        return '<a href="' + WIKI + encodeURIComponent(it[1]) +
               '" target="_blank" rel="noopener">' + it[0] + "</a>";
      }).join("") + "</div>";

    document.body.appendChild(scrim);
    document.body.appendChild(drawer);

    function open(v) {
      drawer.setAttribute("data-open", String(v));
      scrim.setAttribute("data-open", String(v));
      burger.setAttribute("aria-expanded", String(v));
      if (v) {
        // focus must wait for style recalc to flip visibility — a still-hidden
        // element refuses focus. setTimeout rather than rAF: rAF never fires
        // in a backgrounded tab, and timers do.
        setTimeout(function () { drawer.querySelector("a").focus(); }, 50);
        if (window.stat) stat("wiki-menu-open");
      }
    }
    burger.addEventListener("click", function () {
      open(drawer.getAttribute("data-open") !== "true");
    });
    scrim.addEventListener("click", function () { open(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && drawer.getAttribute("data-open") === "true") {
        open(false);
        burger.focus();
      }
    });
  }

  document.addEventListener("DOMContentLoaded", build);
})();
