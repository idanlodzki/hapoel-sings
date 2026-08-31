/* ============================================================
   לוויקיפועל — a small labeled button with ויקיפועל's logo that
   links back to the wiki from every page. The lightweight
   alternative to the full drawer menu (branch wiki-menu): one
   affordance, top corner, always in the same place.

   Placement: on the content pages it becomes the first item in
   the header, so it sits at the top inline-start corner just
   before the הפועל שרים brand. On the game it does the same
   inside the game and listen topbars, and a fixed copy covers
   the setup screen — hidden via :has() the moment a topbar
   screen is visible, so it never stacks on one.

   The logo is served locally (public/wikipoel-logo.png), not
   hotlinked — it is the wiki's own mark, used here at their
   request to link back to them.
   ============================================================ */
(function () {
  "use strict";

  var WIKI = "https://wiki.red-fans.com/";

  var css = document.createElement("style");
  css.textContent = [
    ".wb-btn{display:inline-flex;align-items:center;gap:8px;text-decoration:none;",
    "background:none;border:1px solid var(--line,#2C2C34);border-radius:8px;",
    "padding:6px 12px;color:var(--grey,#A8A8B2);font-weight:600;font-size:.88rem;",
    "white-space:nowrap;font-family:inherit}",
    ".wb-btn:hover{color:var(--white,#F6F5F3);border-color:var(--grey,#A8A8B2)}",
    ".wb-btn img{width:26px;height:27px;display:block}",
    /* the fixed copy that covers the setup screen only */
    ".wb-fixed{position:fixed;top:14px;inset-inline-start:14px;z-index:60;",
    "background:rgba(22,22,26,.9);backdrop-filter:blur(4px)}",
    "body:has(#game:not(.hide)) .wb-fixed,body:has(#listen:not(.hide)) .wb-fixed{display:none}",
    /* inside the game/listen topbars it is a regular first item */
    ".topbar .wb-btn{margin-inline-end:2px}",
    "@media (max-width:480px){.wb-btn span{display:none}",
    ".wb-btn{padding:6px 8px}}",   /* phone: logo only, no label */
  ].join("");
  document.head.appendChild(css);

  function makeBtn(extra) {
    var a = document.createElement("a");
    a.className = "wb-btn" + (extra ? " " + extra : "");
    a.href = WIKI;
    a.target = "_blank";
    a.rel = "noopener";
    a.setAttribute("aria-label", "לאתר ויקיפועל");
    a.title = "ויקיפועל";
    a.innerHTML = '<img src="wikipoel-logo.png" alt=""><span>לוויקיפועל</span>';
    a.addEventListener("click", function () { if (window.stat) stat("wiki-back"); });
    return a;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var head = document.querySelector("header.top .top__in");
    if (head) {
      // content pages: first item, at the corner before the brand
      head.insertBefore(makeBtn(), head.firstChild);
      return;
    }
    // the game: one inside each topbar (game + listen screens)…
    document.querySelectorAll(".topbar").forEach(function (bar) {
      bar.insertBefore(makeBtn(), bar.firstChild);
    });
    // …and a fixed one for the setup screen, which has no topbar
    document.body.appendChild(makeBtn("wb-fixed"));
  });
})();
