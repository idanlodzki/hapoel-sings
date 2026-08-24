/* ============================================================
   נגישות — accessibility widget + privacy notice.

   Loaded on every page, including the game, which has its own
   stylesheet. All styling is injected from here so both share it.

   Settings persist in localStorage. Nothing here sets a cookie.
   ============================================================ */
(function () {
  "use strict";

  var KEY = "hapoel-sings-a11y";
  var NOTICE_KEY = "hapoel-sings-notice";
  var STATEMENT = "accessibility.html";

  var state = { zoom: 100, contrast: 0, gray: 0, links: 0, font: 0, still: 0 };
  try {
    var saved = JSON.parse(localStorage.getItem(KEY) || "null");
    if (saved) for (var k in state) if (k in saved) state[k] = saved[k];
  } catch (e) {}

  /* ---------- styles ---------- */
  var css = document.createElement("style");
  css.textContent = [
    /* the widget itself */
    ".a11y-fab{position:fixed;bottom:calc(18px + var(--a11y-lift,0px));inset-inline-start:18px;",
    "z-index:9000;width:52px;height:52px;zoom:var(--a11y-unzoom,1);",
    "border-radius:50%;background:#1B4DB8;color:#fff;border:2px solid #fff;cursor:pointer;",
    "display:grid;place-items:center;box-shadow:0 4px 18px rgba(0,0,0,.45);padding:0}",
    ".a11y-fab:hover{background:#123790}",
    ".a11y-fab svg{width:28px;height:28px;display:block}",
    ".a11y-panel{position:fixed;bottom:calc(80px + var(--a11y-lift,0px));inset-inline-start:18px;",
    "z-index:9001;width:270px;max-width:calc(100vw - 36px);zoom:var(--a11y-unzoom,1);",
    "background:#14141A;color:#F6F5F3;border:1px solid #3A3A44;border-radius:14px;padding:14px;",
    "box-shadow:0 18px 50px rgba(0,0,0,.6);font-family:Assistant,system-ui,sans-serif;font-size:15px;",
    "max-height:calc(100vh - 110px);overflow:auto}",
    ".a11y-panel[hidden]{display:none}",
    ".a11y-panel h2{font-size:1.05rem;margin:0 0 10px;font-family:Heebo,system-ui,sans-serif;font-weight:900}",
    ".a11y-row{display:flex;gap:8px;margin-bottom:8px}",
    ".a11y-panel button.opt{flex:1;background:#20202A;color:#F6F5F3;border:1px solid #3A3A44;border-radius:9px;",
    "padding:10px 8px;font:inherit;font-weight:700;cursor:pointer;text-align:center}",
    ".a11y-panel button.opt:hover{border-color:#8FA6FF}",
    ".a11y-panel button.opt[aria-pressed=true]{background:#1B4DB8;border-color:#1B4DB8;color:#fff}",
    ".a11y-panel .reset{width:100%;background:none;border:1px solid #3A3A44;color:#A8A8B2;border-radius:9px;",
    "padding:9px;font:inherit;cursor:pointer;margin-top:4px}",
    ".a11y-panel .reset:hover{color:#fff;border-color:#A8A8B2}",
    ".a11y-panel .stmt{display:block;margin-top:10px;color:#8FA6FF;font-size:.86rem;text-align:center}",
    ".a11y-panel :focus-visible,.a11y-fab:focus-visible{outline:3px solid #FFD400;outline-offset:2px}",

    /* the adjustments themselves */
    "html[data-a11y-contrast='1'] body{background:#000!important;color:#fff!important}",
    "html[data-a11y-contrast='1'] a{color:#FFD400!important}",
    "html[data-a11y-contrast='1'] p,html[data-a11y-contrast='1'] li,html[data-a11y-contrast='1'] span,",
    "html[data-a11y-contrast='1'] h1,html[data-a11y-contrast='1'] h2,html[data-a11y-contrast='1'] h3{color:#fff!important}",
    "html[data-a11y-gray='1'] body{filter:grayscale(1)}",
    "html[data-a11y-links='1'] a{text-decoration:underline!important;text-underline-offset:3px;",
    "outline:1px dashed currentColor;outline-offset:2px}",
    "html[data-a11y-font='1'] body,html[data-a11y-font='1'] body *{font-family:Arial,'Arial Hebrew',sans-serif!important;",
    "letter-spacing:.02em!important}",
    "html[data-a11y-still='1'] *{animation:none!important;transition:none!important;scroll-behavior:auto!important}",
  ].join("");
  document.head.appendChild(css);

  function apply() {
    var h = document.documentElement;
    h.setAttribute("data-a11y-contrast", state.contrast ? "1" : "0");
    h.setAttribute("data-a11y-gray", state.gray ? "1" : "0");
    h.setAttribute("data-a11y-links", state.links ? "1" : "0");
    h.setAttribute("data-a11y-font", state.font ? "1" : "0");
    h.setAttribute("data-a11y-still", state.still ? "1" : "0");
    // zoom rather than font-size: the game sizes in px, so rem scaling alone
    // would leave most of it untouched
    document.body.style.zoom = state.zoom === 100 ? "" : state.zoom / 100;
    // body zoom scales fixed children too, so cancel it on our own chrome
    h.style.setProperty("--a11y-unzoom", String(100 / state.zoom));
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
    sync();
  }

  var panel, fab;
  function sync() {
    if (!panel) return;
    panel.querySelectorAll("[data-toggle]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(!!state[b.dataset.toggle]));
    });
    var z = panel.querySelector("[data-zoomlabel]");
    if (z) z.textContent = state.zoom + "%";
  }

  function build() {
    fab = document.createElement("button");
    fab.className = "a11y-fab";
    fab.setAttribute("aria-label", "אפשרויות נגישות");
    fab.setAttribute("aria-expanded", "false");
    fab.setAttribute("aria-controls", "a11yPanel");
    fab.innerHTML =
      '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
      '<circle cx="12" cy="3.6" r="2.1"/>' +
      '<path d="M21 7.5c-2.6.9-5.6 1.4-9 1.4S5.6 8.4 3 7.5l.6-1.9c2.4.8 5.2 1.2 8.4 1.2s6-.4 8.4-1.2z"/>' +
      '<path d="M10.8 10.6v3.1l-2 7.2-2-.6 2-7V10.6zM13.2 10.6v2.7l2 7-2 .6-2-7.2v-3.1z"/></svg>';

    panel = document.createElement("div");
    panel.className = "a11y-panel";
    panel.id = "a11yPanel";
    panel.hidden = true;
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "אפשרויות נגישות");
    panel.innerHTML =
      "<h2>נגישות</h2>" +
      '<div class="a11y-row">' +
        '<button class="opt" data-zoom="-1" aria-label="הקטנת טקסט">א−</button>' +
        '<button class="opt" data-zoomlabel style="flex:.9;cursor:default" tabindex="-1" aria-live="polite">100%</button>' +
        '<button class="opt" data-zoom="1" aria-label="הגדלת טקסט">א+</button>' +
      "</div>" +
      '<div class="a11y-row"><button class="opt" data-toggle="contrast">ניגודיות גבוהה</button></div>' +
      '<div class="a11y-row"><button class="opt" data-toggle="gray">גווני אפור</button></div>' +
      '<div class="a11y-row"><button class="opt" data-toggle="links">הדגשת קישורים</button></div>' +
      '<div class="a11y-row"><button class="opt" data-toggle="font">גופן קריא</button></div>' +
      '<div class="a11y-row"><button class="opt" data-toggle="still">עצירת אנימציות</button></div>' +
      '<button class="reset">איפוס הגדרות</button>' +
      '<a class="stmt" href="' + STATEMENT + '">להצהרת הנגישות</a>';

    document.body.appendChild(fab);
    document.body.appendChild(panel);

    function open(v) {
      panel.hidden = !v;
      fab.setAttribute("aria-expanded", String(v));
      if (v) panel.querySelector("button").focus();
    }
    fab.addEventListener("click", function (e) { e.stopPropagation(); open(panel.hidden); });
    document.addEventListener("click", function (e) {
      if (!panel.hidden && !panel.contains(e.target) && e.target !== fab) open(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !panel.hidden) { open(false); fab.focus(); }
    });
    panel.addEventListener("click", function (e) {
      var t = e.target.closest("[data-toggle],[data-zoom],.reset");
      if (!t) return;
      if (t.dataset.toggle) state[t.dataset.toggle] = state[t.dataset.toggle] ? 0 : 1;
      else if (t.dataset.zoom) {
        var steps = [80, 90, 100, 110, 125, 150];
        var i = steps.indexOf(state.zoom);
        if (i < 0) i = 2;
        i = Math.min(steps.length - 1, Math.max(0, i + Number(t.dataset.zoom)));
        state.zoom = steps[i];
      } else state = { zoom: 100, contrast: 0, gray: 0, links: 0, font: 0, still: 0 };
      apply();
    });
    sync();
  }

  /* ---------- privacy notice ----------
     We set no cookies of our own. The YouTube player does once a song
     plays, so this informs rather than pretending to gate consent. */
  function notice() {
    try { if (localStorage.getItem(NOTICE_KEY)) return; } catch (e) { return; }
    var bar = document.createElement("div");
    bar.setAttribute("role", "region");
    bar.setAttribute("aria-label", "הודעת פרטיות");
    bar.setAttribute("style",
      "position:fixed;inset-inline:0;bottom:0;z-index:8000;background:#14141A;color:#F6F5F3;" +
      "border-top:1px solid #3A3A44;padding:14px 18px;font-family:Assistant,system-ui,sans-serif;" +
      "font-size:14px;line-height:1.6;display:flex;gap:14px;flex-wrap:wrap;align-items:center;justify-content:center");
    bar.innerHTML =
      "<span style='max-width:70ch'>האתר לא שומר עוגיות משלו. נגן היוטיוב המוטמע עשוי לשמור עוגיות של גוגל " +
      "כששיר מתנגן. <a href='privacy.html' style='color:#8FA6FF'>מדיניות הפרטיות</a></span>" +
      "<button style='background:#E2001A;color:#fff;border:0;border-radius:8px;padding:9px 20px;" +
      "font:inherit;font-weight:700;cursor:pointer'>הבנתי</button>";
    bar.querySelector("button").addEventListener("click", function () {
      try { localStorage.setItem(NOTICE_KEY, "1"); } catch (e) {}
      document.documentElement.style.setProperty("--a11y-lift", "0px");
      bar.remove();
      if (fab) fab.focus();
    });
    document.body.appendChild(bar);
    var lift = function () {
      document.documentElement.style.setProperty("--a11y-lift", bar.offsetHeight + "px");
    };
    lift();
    addEventListener("resize", lift);
  }

  document.addEventListener("DOMContentLoaded", function () {
    build();
    apply();
    notice();
  });
})();
