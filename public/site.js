/* One footer, injected everywhere — including into the game, which has its
   own stylesheet and so gets inline styles here rather than the shared CSS. */
(function () {
  var LINKS = [["index.html", "המשחק"], ["rules.html", "כללי המשחק"], ["accessibility.html", "נגישות"], ["terms.html", "תנאי שימוש"], ["privacy.html", "פרטיות"]];
  var here = location.pathname.split("/").pop() || "index.html";
  var html =
    '<div class="wrap">' +
      '<div class="foot__links">' +
        LINKS.map(function (l) {
          return '<a href="' + l[0] + '"' + (l[0] === here ? ' aria-current="page"' : '') + '>' + l[1] + '</a>';
        }).join('') +
        '<a href="https://github.com/idanlodzki/hapoel-sings" target="_blank" rel="noopener">קוד המקור</a>' +
        '<a class="foot__icon" href="https://www.linkedin.com/in/idan-lodzki-755939157/" target="_blank" rel="noopener"' +
          ' aria-label="LinkedIn" title="LinkedIn">' +
          '<svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true">' +
          '<path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3.2 9h3.6v12H3.2zM9.4 9H13v1.7h.05c.5-.95 1.75-1.95 3.6-1.95 3.85 0 4.56 2.5 4.56 5.77V21h-3.8v-5.5c0-1.31-.03-3-1.85-3-1.85 0-2.13 1.43-2.13 2.9V21H9.4z"/>' +
          '</svg>' +
        '</a>' +
      '</div>' +
      '<div class="foot__help">' +
        'שכחתי שיר? <a href="mailto:idan.lut@gmail.com?subject=%D7%94%D7%A4%D7%95%D7%A2%D7%9C%20%D7%A9%D7%A8%D7%99%D7%9D%20%E2%80%94%20%D7%A9%D7%99%D7%A8%20%D7%A9%D7%97%D7%A1%D7%A8%20%D7%91%D7%A8%D7%A9%D7%99%D7%9E%D7%94&amp;body=%D7%A9%D7%9D%20%D7%94%D7%A9%D7%99%D7%A8%3A%0A%D7%A7%D7%99%D7%A9%D7%95%D7%A8%20%D7%9C%D7%99%D7%95%D7%98%D7%99%D7%95%D7%91%3A%0A%0A%D7%AA%D7%95%D7%93%D7%94%21">' +
        'עזרו לי להוסיף אותו</a>' +
      '</div>' +
      '<div class="foot__legal">' +
        '<span>© הפועל שרים · אתר לא רשמי, ללא קשר למועדון הפועל תל אביב</span>' +
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
