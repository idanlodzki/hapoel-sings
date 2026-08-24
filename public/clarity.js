/* ============================================================
   Microsoft Clarity — session replay and heatmaps.

   TEMPORARY. This is here to answer specific UX questions by watching
   real sessions; the intent is to remove it once they are answered.
   Unlike stats.js this is NOT cookieless — Clarity sets its own cookies
   and sends data to Microsoft, which is why privacy.html has to say so
   and why the notice bar has to actually gate it.

   Player names are masked at the six places they reach the DOM, via
   data-clarity-mask="true" in index.html. Project masking mode is left
   on Balanced deliberately: Strict would mask song names and buttons
   too and make the recordings useless.

   To remove: delete this file and the two <script src="clarity.js">
   tags (index.html, and the shell in scripts/build-pages.py).
   ============================================================ */
(function () {
  "use strict";

  var PROJECT = "y7lr1bbdnl";

  // honour an explicit opt-out, same as stats.js
  if (navigator.doNotTrack === "1" || window.doNotTrack === "1") return;

  // Set to false to include localhost while testing the integration.
  var SKIP_LOCAL = true;
  if (SKIP_LOCAL &&
      (location.protocol === "file:" ||
       /^(localhost$|127\.|0\.0\.0\.0$|\[?::1\]?$|.*\.local$)/.test(location.hostname))) {
    return;
  }

  (function (c, l, a, r, i, t, y) {
    c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
    t = l.createElement(r); t.async = 1; t.src = "https://www.clarity.ms/tag/" + i;
    y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
  })(window, document, "clarity", "script", PROJECT);
})();
