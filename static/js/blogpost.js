document.addEventListener("DOMContentLoaded", function () {
  /* ── Lazy-load iframes (YouTube, Spotify, etc.) ────────────────── */
  /* Prevents all embeds from loading simultaneously on page load,   */
  /* which was causing the page to stall for 7+ seconds on posts     */
  /* with many media embeds (e.g. /blog/my-musics/).                 */
  (function lazyLoadIframes() {
    const iframes = document.querySelectorAll(".blog-content iframe, .ck-content iframe");
    if (!iframes.length) return;

    iframes.forEach(function (iframe) {
      const src = iframe.getAttribute("src");
      if (!src) return;

      // Move real src to data-src so the browser doesn't fetch it yet
      iframe.setAttribute("data-src", src);
      iframe.removeAttribute("src");

      // Mark as not-yet-loaded for CSS placeholder styling
      iframe.classList.add("lazy-iframe");

      // Also add native lazy-loading as a progressive enhancement
      iframe.setAttribute("loading", "lazy");
    });

    // Use IntersectionObserver to load iframes as they approach the viewport
    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;

            var iframe = entry.target;
            var dataSrc = iframe.getAttribute("data-src");
            if (dataSrc) {
              iframe.setAttribute("src", dataSrc);
              iframe.removeAttribute("data-src");
              iframe.addEventListener(
                "load",
                function () {
                  iframe.classList.remove("lazy-iframe");
                  iframe.classList.add("lazy-iframe--loaded");
                  // Recalculate progress bar after iframe loads (height changes)
                  if (typeof window.updateProgressBar === "function") window.updateProgressBar();
                },
                { once: true },
              );
            }
            observer.unobserve(iframe);
          });
        },
        { rootMargin: "200px 0px" },
      );

      iframes.forEach(function (iframe) {
        observer.observe(iframe);
      });
    } else {
      // Fallback: load all iframes immediately if IntersectionObserver is unavailable
      iframes.forEach(function (iframe) {
        var dataSrc = iframe.getAttribute("data-src");
        if (dataSrc) {
          iframe.setAttribute("src", dataSrc);
          iframe.removeAttribute("data-src");
          iframe.classList.remove("lazy-iframe");
        }
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
