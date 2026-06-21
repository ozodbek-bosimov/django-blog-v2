// Project description "more / less" toggle.
//
// Goals:
//   • Preserve the author's own line breaks (rendered via white-space: pre-line).
//   • Show at most 3 lines collapsed, with "... more" sitting INLINE at the end
//     of the 3rd line (never dropping onto its own line).
//   • When expanded, "less" sits INLINE right after the last word.
//   • The "more" button only appears when the text is actually longer than
//     3 lines.
(function () {
  "use strict";

  function lineHeightOf(el) {
    var cs = getComputedStyle(el);
    var lh = parseFloat(cs.lineHeight);
    if (isNaN(lh)) {
      lh = parseFloat(cs.fontSize) * 1.625;
    }
    return lh;
  }

  function buildToggle(label, withEllipsis) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "project-desc-toggle";
    if (withEllipsis) {
      var ell = document.createElement("span");
      ell.className = "project-desc-ellipsis";
      ell.textContent = "\u2026 "; // "… "
      btn.appendChild(ell);
    } else {
      // No leading ellipsis (the "less" button) — give it a small gap
      // so it doesn't butt right up against the final word.
      btn.classList.add("project-desc-toggle--gap");
    }
    btn.appendChild(document.createTextNode(label));
    return btn;
  }

  function setupCard(desc) {
    var full = desc.getAttribute("data-fulltext");
    if (full === null) {
      full = desc.textContent;
      desc.setAttribute("data-fulltext", full);
    }

    // Reset the element to a single text span we control.
    desc.classList.remove("is-clamped");
    desc.textContent = "";
    var textSpan = document.createElement("span");
    textSpan.className = "project-desc-text";
    desc.appendChild(textSpan);

    var maxH = lineHeightOf(desc) * 3 + 1;

    // Does the full text already fit within 3 lines? Then no toggle needed.
    textSpan.textContent = full;
    if (desc.scrollHeight <= maxH) {
      return;
    }

    // Word-boundary cut points (char index just after each word).
    var wordEnds = [];
    var re = /\S+/g;
    var m;
    while ((m = re.exec(full)) !== null) {
      wordEnds.push(m.index + m[0].length);
    }
    if (wordEnds.length === 0) return;

    var moreBtn = buildToggle("more", true);
    var lessBtn = buildToggle("less", false);

    function measureFits(len) {
      textSpan.textContent = full.slice(0, len).replace(/\s+$/, "");
      return desc.scrollHeight <= maxH;
    }

    // Binary search for the largest prefix that still fits in 3 lines
    // WITH the "more" button present at the end.
    function computeCut() {
      desc.appendChild(moreBtn); // present while measuring
      var lo = 0;
      var hi = wordEnds.length - 1;
      var best = wordEnds[0];
      while (lo <= hi) {
        var mid = (lo + hi) >> 1;
        if (measureFits(wordEnds[mid])) {
          best = wordEnds[mid];
          lo = mid + 1;
        } else {
          hi = mid - 1;
        }
      }
      return best;
    }

    var cutLen = computeCut();

    function collapse() {
      desc.classList.remove("is-expanded");
      textSpan.textContent = full.slice(0, cutLen).replace(/\s+$/, "");
      if (lessBtn.parentNode) lessBtn.remove();
      desc.appendChild(moreBtn);
    }

    function expand() {
      desc.classList.add("is-expanded");
      textSpan.textContent = full;
      if (moreBtn.parentNode) moreBtn.remove();
      desc.appendChild(lessBtn);
    }

    moreBtn.addEventListener("click", expand);
    lessBtn.addEventListener("click", collapse);

    // Start collapsed.
    collapse();
    // Remember expanded state across resizes.
    desc._collapse = collapse;
    desc._expand = expand;
    desc._recompute = function () {
      var wasExpanded = desc.classList.contains("is-expanded");
      maxH = lineHeightOf(desc) * 3 + 1;
      cutLen = computeCut();
      if (wasExpanded) {
        expand();
      } else {
        collapse();
      }
    };
  }

  function setupAll() {
    document.querySelectorAll(".project-desc").forEach(setupCard);
  }

  let _projectsInitTimer = null;
  function debouncedSetupAll() {
    if (_projectsInitTimer) clearTimeout(_projectsInitTimer);
    _projectsInitTimer = setTimeout(setupAll, 50);
  }

  // Run immediately for initial page load
  setTimeout(debouncedSetupAll, 10);

  if (!window._projectsListenerAdded) {
    document.body.addEventListener("htmx:afterSettle", function () {
      if (window.location.pathname.includes('/projects')) {
        debouncedSetupAll();
      }
    });
    document.body.addEventListener("htmx:restored", function () {
      if (window.location.pathname.includes('/projects')) {
        debouncedSetupAll();
      }
    });
    window._projectsListenerAdded = true;
  }

  var resizeTimer = null;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      document.querySelectorAll(".project-desc").forEach(function (desc) {
        if (typeof desc._recompute === "function") {
          desc._recompute();
        } else {
          setupCard(desc);
        }
      });
    }, 150);
  });
})();
