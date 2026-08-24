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
        '<a href="https://www.linkedin.com/in/idan-lodzki-755939157/" target="_blank" rel="noopener">LinkedIn</a>' +
        '<a href="mailto:idan.lut@gmail.com">idan.lut@gmail.com</a>' +
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
    f.querySelectorAll("a").forEach(function (a) {
      if (!a.style.color) { a.style.color = "inherit"; a.style.textDecoration = "none"; }
    });
    var w = f.querySelector(".wrap");
    if (w && !document.querySelector("link[href='site.css']")) {
      w.setAttribute("style", "max-width:1100px;margin-inline:auto;padding:0 20px");
      f.querySelector(".foot__links").setAttribute("style", "display:flex;gap:8px 18px;flex-wrap:wrap;margin-bottom:10px");
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
