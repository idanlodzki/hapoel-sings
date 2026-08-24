/* ============================================================
   Usage measurement — GoatCounter.

   Cookieless and anonymous by design. We count *actions*, never people:
   no cookies, no identifiers, no localStorage of our own, and player
   names are never sent — they are other people's real names, typed by
   the host, and none of our business.

   GoatCounter's model is pageview-shaped: `path` doubles as the event
   name, so any dimension has to be baked into the name itself
   (players-4, video-error-<id>) rather than passed as properties.
   ============================================================ */
(function () {
  "use strict";

  // The site code from goatcounter.com — the "xxx" in xxx.goatcounter.com.
  var CODE = "hapoel-sings";

  window.stat = function () {};   // no-op unless everything below checks out

  // never measure local development or a file:// open
  if (location.protocol === "file:" ||
      /^(localhost$|127\.|0\.0\.0\.0$|\[?::1\]?$|.*\.local$)/.test(location.hostname)) {
    return;
  }

  // honour an explicit "do not track" rather than ignoring it
  if (navigator.doNotTrack === "1" || window.doNotTrack === "1") return;

  var queue = [];

  function flush() {
    if (!(window.goatcounter && window.goatcounter.count)) return;
    while (queue.length) {
      var e = queue.shift();
      try {
        window.goatcounter.count({ path: e[0], title: e[1] || e[0], event: true });
      } catch (err) { /* measurement must never break the game */ }
    }
  }

  /* Queue rather than drop: the script is async, and the most interesting
     event (game-start) fires seconds after load, sometimes before it lands. */
  window.stat = function (name, title) {
    if (!name) return;
    queue.push([String(name).slice(0, 100), title]);
    flush();
  };

  var s = document.createElement("script");
  s.async = true;
  s.src = "//gc.zgo.at/count.js";                       // also counts the pageview
  s.setAttribute("data-goatcounter", "https://" + CODE + ".goatcounter.com/count");
  s.onload = flush;
  document.head.appendChild(s);
})();
