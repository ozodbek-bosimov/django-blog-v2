document.addEventListener("DOMContentLoaded", function () {
  /* ── Lazy-load iframes (YouTube, Spotify, etc.) ────────────────── */
  /* Prevents all embeds from loading simultaneously on page load,   */
  /* which caused the page to stall/freeze, especially on mobile.    */
  /*                                                                  */
  /* Strategy:                                                        */
  /*   Desktop → IntersectionObserver with queued concurrent loading  */
  /*   Mobile  → click-to-load facades (tap the ▶ to load)           */
  (function lazyLoadIframes() {
    var iframes = document.querySelectorAll(".blog-content iframe, .ck-content iframe");
    if (!iframes.length) return;

    var isMobile = window.matchMedia("(hover: none) and (pointer: coarse)").matches;
    var MAX_CONCURRENT = isMobile ? 1 : 2;
    var MARGIN = isMobile ? "50px 0px" : "200px 0px";
    var activeLoads = 0;
    var loadQueue = [];

    // Extract YouTube video ID from various YouTube URL formats
    function getYouTubeId(url) {
      if (!url) return null;
      var m = url.match(/(?:youtube\.com\/embed\/|youtu\.be\/|youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})/);
      return m ? m[1] : null;
    }

    // Actually start loading one iframe
    function startLoad(iframe) {
      var dataSrc = iframe.getAttribute("data-src");
      if (!dataSrc) return;
      activeLoads++;
      iframe.setAttribute("src", dataSrc);
      iframe.removeAttribute("data-src");
      iframe.addEventListener(
        "load",
        function () {
          iframe.classList.remove("lazy-iframe");
          iframe.classList.add("lazy-iframe--loaded");
          // Remove facade overlay if present
          var facade = iframe.parentElement &&
            iframe.parentElement.querySelector(".lazy-iframe-facade");
          if (facade) facade.remove();
          activeLoads--;
          drainQueue();
          if (typeof window.updateProgressBar === "function") window.updateProgressBar();
        },
        { once: true },
      );
    }

    // Process the next queued iframe if we have capacity
    function drainQueue() {
      while (loadQueue.length > 0 && activeLoads < MAX_CONCURRENT) {
        var next = loadQueue.shift();
        // Only load if it still has data-src (wasn't loaded some other way)
        if (next.getAttribute("data-src")) {
          startLoad(next);
        }
      }
    }

    // Enqueue an iframe for loading (respects concurrency limit)
    function enqueueLoad(iframe) {
      if (activeLoads < MAX_CONCURRENT) {
        startLoad(iframe);
      } else {
        loadQueue.push(iframe);
      }
    }

    // ── Prepare all iframes: strip src, add placeholder styling ──
    iframes.forEach(function (iframe) {
      var src = iframe.getAttribute("src");
      if (!src) return;

      iframe.setAttribute("data-src", src);
      iframe.removeAttribute("src");
      iframe.classList.add("lazy-iframe");
      iframe.setAttribute("loading", "lazy");

      // On mobile: wrap iframe in a facade with a play button
      if (isMobile) {
        var wrapper = iframe.parentElement;
        // Make sure the parent is position-relative for the overlay
        if (wrapper && getComputedStyle(wrapper).position === "static") {
          wrapper.style.position = "relative";
        }

        var facade = document.createElement("div");
        facade.className = "lazy-iframe-facade";

        // For YouTube: show the video thumbnail as background
        var ytId = getYouTubeId(src);
        if (ytId) {
          facade.style.backgroundImage =
            "url(https://img.youtube.com/vi/" + ytId + "/hqdefault.jpg)";
          facade.classList.add("lazy-iframe-facade--yt");
        }

        facade.innerHTML = '<div class="lazy-iframe-facade__play">&#9654;</div>';

        facade.addEventListener("click", function () {
          facade.remove();
          enqueueLoad(iframe);
        });

        // Insert facade right before the iframe
        iframe.parentNode.insertBefore(facade, iframe);
      }
    });

    // ── Desktop: auto-load via IntersectionObserver with queue ──
    if (!isMobile && "IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            observer.unobserve(entry.target);
            enqueueLoad(entry.target);
          });
        },
        { rootMargin: MARGIN },
      );

      iframes.forEach(function (iframe) {
        if (iframe.getAttribute("data-src")) {
          observer.observe(iframe);
        }
      });
    } else if (!isMobile) {
      // Fallback for desktop without IntersectionObserver
      iframes.forEach(function (iframe) {
        enqueueLoad(iframe);
      });
    }
    // Mobile: iframes are loaded only on tap (facade click handler above)
  })();

  /* ── Reading Progress Bar ─────────────────────────────────────── */
  const progressBar = document.getElementById("reading-progress-bar");

  if (progressBar) {
    // Expose updateProgressBar so lazy-loaded iframes can trigger a recalc
    window.updateProgressBar = function updateProgressBar() {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const docHeight =
        document.documentElement.scrollHeight -
        document.documentElement.clientHeight;
      const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      progressBar.style.width = Math.min(progress, 100) + "%";
    };

    window.addEventListener("scroll", window.updateProgressBar, { passive: true });
    window.updateProgressBar();
  }

  /* ── Copy Link Button ─────────────────────────────────────────── */
  const copyLinkBtn = document.getElementById("copy-link-btn");

  if (copyLinkBtn) {
    copyLinkBtn.addEventListener("click", function () {
      const url = copyLinkBtn.dataset.url || window.location.href;
      const icon = copyLinkBtn.querySelector("i");

      navigator.clipboard
        .writeText(url)
        .then(function () {
          copyLinkBtn.classList.add("copied");
          if (icon) {
            icon.className = "bi bi-check2";
          }

          setTimeout(function () {
            copyLinkBtn.classList.remove("copied");
            if (icon) {
              icon.className = "bi bi-link-45deg";
            }
          }, 2000);
        })
        .catch(function () {
          // Fallback for browsers that don't support clipboard API
          const textarea = document.createElement("textarea");
          textarea.value = url;
          textarea.style.position = "fixed";
          textarea.style.opacity = "0";
          document.body.appendChild(textarea);
          textarea.focus();
          textarea.select();
          try {
            document.execCommand("copy");
            copyLinkBtn.classList.add("copied");
            if (icon) icon.className = "bi bi-check2";
            setTimeout(function () {
              copyLinkBtn.classList.remove("copied");
              if (icon) icon.className = "bi bi-link-45deg";
            }, 2000);
          } catch (err) {
            console.error("Failed to copy link:", err);
          }
          document.body.removeChild(textarea);
        });
    });
  }

  /* ── Code Block Enhancements ──────────────────────────────────── */
  const toPrettyLanguage = (lang) => {
    if (!lang) return "Python";
    const normalized = lang.toLowerCase();
    if (normalized === "cpp") return "C++";
    if (normalized === "cs") return "C#";
    return normalized.charAt(0).toUpperCase() + normalized.slice(1);
  };

  const preElements = document.querySelectorAll("pre");

  preElements.forEach((pre) => {
    const code = pre.querySelector("code");
    if (!code) return;

    const languageClass = [...code.classList, ...pre.classList].find((cls) =>
      cls.startsWith("language-"),
    );
    const language = languageClass
      ? languageClass.replace("language-", "")
      : "python";

    if (!languageClass) {
      pre.classList.add("language-python");
      code.classList.add("language-python");
    }

    const header = document.createElement("div");
    header.className = "code-header";

    const langLabel = document.createElement("span");
    langLabel.className = "code-lang";
    langLabel.textContent = toPrettyLanguage(language);

    const copyBtn = document.createElement("button");
    copyBtn.className = "copy-btn";
    copyBtn.type = "button";
    copyBtn.innerHTML = '<i class="bi bi-clipboard"></i> Copy';

    copyBtn.addEventListener("click", function () {
      navigator.clipboard.writeText(code.innerText).then(() => {
        copyBtn.classList.add("copied");
        copyBtn.innerHTML = '<i class="bi bi-check2"></i> Copied!';
        setTimeout(() => {
          copyBtn.classList.remove("copied");
          copyBtn.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
        }, 2000);
      });
    });

    header.appendChild(langLabel);
    header.appendChild(copyBtn);
    pre.insertBefore(header, pre.firstChild);
  });

  if (typeof Prism !== "undefined") {
    Prism.highlightAll();
  }
});
