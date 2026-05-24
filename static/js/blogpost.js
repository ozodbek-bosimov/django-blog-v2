document.addEventListener("DOMContentLoaded", function () {
  /* ── Lazy-load iframes (YouTube, Spotify, etc.) ────────────────── */
  /* The server-side `lazy_iframes` template filter already delivers  */
  /* iframes with data-src instead of src, so the browser never       */
  /* eagerly loads them. This JS restores src when appropriate:        */
  /*   Desktop → IntersectionObserver with queued concurrent loading  */
  /*   Mobile  → click-to-load facades (tap the ▶ to load)           */
  (function lazyLoadIframes() {
    var iframes = document.querySelectorAll("iframe.lazy-iframe[data-src]");
    if (!iframes.length) return;

    var isMobile = window.matchMedia("(hover: none) and (pointer: coarse)").matches;
    var MAX_CONCURRENT = isMobile ? 1 : 2;
    var MARGIN = isMobile ? "50px 0px" : "200px 0px";
    var activeLoads = 0;
    var loadQueue = [];

    // Extract YouTube video ID from various URL formats
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
        if (next.getAttribute("data-src")) startLoad(next);
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

    // ── Mobile: add click-to-load facades ──
    if (isMobile) {
      iframes.forEach(function (iframe) {
        var wrapper = iframe.parentElement;
        if (wrapper && getComputedStyle(wrapper).position === "static") {
          wrapper.style.position = "relative";
        }

        var facade = document.createElement("div");
        facade.className = "lazy-iframe-facade";

        var ytId = getYouTubeId(iframe.getAttribute("data-src"));
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

        iframe.parentNode.insertBefore(facade, iframe);
      });
    }

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
        observer.observe(iframe);
      });
    } else if (!isMobile) {
      // Fallback for desktop without IntersectionObserver
      iframes.forEach(function (iframe) {
        enqueueLoad(iframe);
      });
    }
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
