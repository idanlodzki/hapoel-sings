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
    /* on the setup screen the button IS the tagline, centered under the brand */
    ".wb-tagline{padding:9px 18px;font-size:.95rem}",
    /* inside the game/listen topbars it is a regular first item */
    ".topbar .wb-btn{margin-inline-end:2px}",
    /* phones: corner copies shrink to the logo alone; the tagline one keeps its label */
    "@media (max-width:480px){.topbar .wb-btn span,header.top .wb-btn span{display:none}",
    ".topbar .wb-btn,header.top .wb-btn{padding:6px 8px}}",
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
    return a;
  }

  /* one delegated counter covers the injected copies and the static
     tagline button on the setup screen alike */
  document.addEventListener("click", function (e) {
    if (e.target.closest(".wb-btn") && window.stat) stat("wiki-back");
  });

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
  });
})();
