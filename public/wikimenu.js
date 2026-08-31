/* ============================================================
   תפריט ויקיפועל — an exact copy of wiki.red-fans.com's mobile
   menu, added at the wiki's request as part of adding הפועל שרים
   as a page there.

   Measured from the REAL mobile view (mobileaction=toggle_view_mobile):
   their site JS replaces Minerva's stock drawer with a custom menu —
   red #cc3333 rows, white 16px text at 12px 15px padding (44px rows),
   thin white separators, white sub-rows with red text under two
   collapsible headers (▸ כדורגל / ▸ כדורסל, closed by default),
   a home icon on עמוד ראשי, 275px panel, system font. A static
   scrape misses all of this, which is why v1 got it wrong.

   Self-contained like a11y.js. Links open in a new tab so mid-game
   music survives.
   ============================================================ */
(function () {
  "use strict";

  var WIKI = "https://wiki.red-fans.com/index.php?title=";

  /* Their menu, verbatim. type: link = red row, section = collapsible
     header whose sub-links render as white rows with red text. */
  var MENU = [
    { t: "עמוד ראשי", p: "עמוד_ראשי", home: true },
    { t: "עונת 2026/27", p: "2026/27" },
    { t: "כדורגל", sub: [
      ["שחקנים", "קטגוריה:שחקני_הפועל_תל_אביב_(כדורגל)"],
      ["ראש בראש", "מיוחד:RunQuery/Gamesearchfootball"],
      ["גלריה", "קטגוריה:הפועל_תל_אביב_(כדורגל)/תמונות"],
    ]},
    { t: "כדורסל", sub: [
      ["שחקנים", "קטגוריה:שחקני_הפועל_תל_אביב_(כדורסל)"],
      ["ראש בראש", "מיוחד:RunQuery/Gamesearchbball"],
      ["גלריה", "קטגוריה:הפועל_תל_אביב_(כדורסל)/תמונות"],
    ]},
    { t: "עונות קודמות", p: "קטגוריה:עונות" },
    { t: "שירים", p: "קטגוריה:שירים" },
    { t: "הנצחת אוהדים", p: "פורטל:הנצחה_אדומה" },
    { t: "ארכיון עלי מוהר (חדש)", p: "ארכיון_בשער" },
  ];

  var HOME_SVG =
    '<svg viewBox="0 0 20 20" width="18" height="18" fill="currentColor" aria-hidden="true">' +
    '<path d="M10 1.5 1.5 9H4v9h4v-5h4v5h4V9h2.5z"/></svg>';

  /* ---------- styles: theirs ---------- */
  var RED = "#cc3333";
  var FONT = '-apple-system,"system-ui","Segoe UI",Roboto,Lato,Helvetica,Arial,sans-serif';
  var css = document.createElement("style");
  css.textContent = [
    ".wm-burger{display:inline-flex;align-items:center;justify-content:center;cursor:pointer;",
    "background:none;border:0;padding:0}",
    ".wm-burger svg{display:block}",
    ".wm-burger--head{width:38px;height:38px;border:1px solid var(--line,#2C2C34);border-radius:8px;",
    "color:var(--grey,#A8A8B2);margin-inline-end:2px}",
    ".wm-burger--head:hover{color:var(--white,#F6F5F3);border-color:var(--grey,#A8A8B2)}",
    ".wm-burger--float{position:fixed;top:14px;inset-inline-start:14px;z-index:8900;width:42px;height:42px;",
    "background:" + RED + ";border-radius:9px;color:#fff;box-shadow:0 2px 10px rgba(0,0,0,.45)}",
    ".wm-burger--float:hover{filter:brightness(1.1)}",
    ".wm-scrim{position:fixed;inset:0;z-index:9400;background:rgba(0,0,0,.5);opacity:0;",
    "visibility:hidden;transition:opacity .25s ease-in-out,visibility .25s ease-in-out}",
    ".wm-scrim[data-open='true']{opacity:1;visibility:visible}",
    ".wm-drawer{position:fixed;top:0;bottom:0;inset-inline-start:0;z-index:9500;",
    "width:min(275px,85vw);background:" + RED + ";overflow-y:auto;overscroll-behavior:contain;",
    "box-shadow:rgba(0,0,0,.35) -1px 0 8px;font-family:" + FONT + ";",
    "transform:translateX(100%);visibility:hidden;",
    "transition:transform .25s ease-in-out,visibility .25s ease-in-out}",
    "[dir='ltr'] .wm-drawer{transform:translateX(-100%)}",
    ".wm-drawer[data-open='true']{transform:translateX(0);visibility:visible}",
    "@media (prefers-reduced-motion:reduce){.wm-drawer,.wm-scrim{transition:none}}",
    ".wm-drawer ul{list-style:none;margin:0;padding:0}",
    /* red rows: white 16px text, thin white separator under each */
    ".wm-item,.wm-head{display:flex;align-items:center;gap:10px;width:100%;",
    "padding:12px 15px 12px 10px;font-size:16px;font-weight:400;color:#fff;",
    "background:" + RED + ";text-decoration:none;text-align:start;",
    "border:0;border-bottom:1px solid rgba(255,255,255,.85);cursor:pointer;font-family:inherit}",
    ".wm-item:hover,.wm-head:hover{filter:brightness(1.08)}",
    ".wm-item svg{flex:none}",
    /* collapsible header: their ▸ arrow, flipping when open */
    ".wm-head .wm-arr{display:inline-block;font-size:13px;line-height:1}",
    ".wm-head[aria-expanded='true'] .wm-arr{transform:rotate(90deg)}",
    /* white sub-rows with red text */
    ".wm-sub{display:none}",
    ".wm-sub[data-open='true']{display:block}",
    ".wm-sub a{display:block;padding:12px 15px 12px 10px;padding-inline-start:26px;",
    "font-size:16px;color:" + RED + ";background:#fff;text-decoration:none;",
    "border-bottom:1px solid " + RED + "22}",
    ".wm-sub a:hover{background:#f6eaea}",
    ".wm-burger:focus-visible,.wm-drawer a:focus-visible,.wm-drawer button:focus-visible{",
    "outline:3px solid #fff;outline-offset:-3px}",
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

    drawer.innerHTML = "<ul>" + MENU.map(function (it, i) {
      if (it.sub) {
        return '<li><button type="button" class="wm-head" aria-expanded="false" aria-controls="wmSub' + i + '">' +
               '<span class="wm-arr" aria-hidden="true">▸</span><span>' + it.t + "</span></button>" +
               '<ul class="wm-sub" id="wmSub' + i + '" data-open="false">' +
               it.sub.map(function (s) {
                 return '<li><a href="' + WIKI + encodeURIComponent(s[1]) +
                        '" target="_blank" rel="noopener">' + s[0] + "</a></li>";
               }).join("") + "</ul></li>";
      }
      return '<li><a class="wm-item" href="' + WIKI + encodeURIComponent(it.p) +
             '" target="_blank" rel="noopener">' +
             (it.home ? HOME_SVG : "") + "<span>" + it.t + "</span></a></li>";
    }).join("") + "</ul>";

    document.body.appendChild(scrim);
    document.body.appendChild(drawer);

    /* collapsible sections, closed by default like theirs */
    drawer.addEventListener("click", function (e) {
      var h = e.target.closest(".wm-head");
      if (!h) return;
      var open = h.getAttribute("aria-expanded") !== "true";
      h.setAttribute("aria-expanded", String(open));
      document.getElementById(h.getAttribute("aria-controls")).setAttribute("data-open", String(open));
    });

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
