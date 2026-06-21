(function () {
  let scrollListener = null;

  function initBlogPost() {
    // Clean up previous scroll listener
    if (scrollListener) {
      window.removeEventListener("scroll", scrollListener);
      scrollListener = null;
    }

    /* ── Lazy Load Iframes (Run First to ensure they load even if other things fail) ────────────────────────────────────────── */
    function runLazyIframes() {
        var phs = document.querySelectorAll(".lazy-iframe-ph");
        if (!phs.length) return;

        var queue = [];

        function loadIframe(ph) {
            if (ph._loaded) return;
            ph._loaded = true;
            var tpl = ph.nextElementSibling;
            if (!tpl || tpl.tagName !== "TEMPLATE") return;
            var el = tpl.content.firstElementChild;
            if (!el) return;
            var iframe = el.cloneNode(true);
            ph.parentNode.insertBefore(iframe, ph);
            ph.remove();
            tpl.remove();
        }

        if ("IntersectionObserver" in window) {
            try {
                var obs = new IntersectionObserver(function(entries){
                    entries.forEach(function(e){
                        if (e.isIntersecting) {
                            obs.unobserve(e.target);
                            loadIframe(e.target);
                        }
                    });
                }, {rootMargin: "300px 0px"});
                phs.forEach(function(ph){ obs.observe(ph); queue.push(ph); });
            } catch (err) {
                console.error("IntersectionObserver failed:", err);
                phs.forEach(loadIframe);
                return;
            }
        } else {
            phs.forEach(loadIframe);
            return;
        }

        setTimeout(function tick(){
            while (queue.length && queue[0]._loaded) queue.shift();
            if (!queue.length) return;
            var ph = queue.shift();
            if (obs) try { obs.unobserve(ph); } catch(e){}
            loadIframe(ph);
            if (queue.length) setTimeout(tick, 1500);
        }, 2000);
    }

    try {
        runLazyIframes();
    } catch (e) {
        console.error("Lazy iframe error:", e);
    }

    /* ── Reading Progress Bar ─────────────────────────────────────── */
    const progressBar = document.getElementById("reading-progress-bar");

    if (progressBar) {
      function updateProgressBar() {
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const docHeight =
          document.documentElement.scrollHeight -
          document.documentElement.clientHeight;
        const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
        progressBar.style.width = Math.min(progress, 100) + "%";
      }

      scrollListener = updateProgressBar;
      window.addEventListener("scroll", scrollListener, { passive: true });
      updateProgressBar();
    }

    /* ── Copy Link Button ─────────────────────────────────────────── */
    const copyLinkBtn = document.getElementById("copy-link-btn");

    if (copyLinkBtn) {
      // Remove previous listener to prevent duplicates if init runs multiple times
      const newCopyBtn = copyLinkBtn.cloneNode(true);
      copyLinkBtn.parentNode.replaceChild(newCopyBtn, copyLinkBtn);
      
      newCopyBtn.addEventListener("click", function () {
        const url = newCopyBtn.dataset.url || window.location.href;
        const icon = newCopyBtn.querySelector("i");

        navigator.clipboard
          .writeText(url)
          .then(function () {
            newCopyBtn.classList.add("copied");
            if (icon) {
              icon.className = "bi bi-check2";
            }

            setTimeout(function () {
              newCopyBtn.classList.remove("copied");
              if (icon) {
                icon.className = "bi bi-link-45deg";
              }
            }, 2000);
          })
          .catch(function () {
            const textarea = document.createElement("textarea");
            textarea.value = url;
            textarea.style.position = "fixed";
            textarea.style.opacity = "0";
            document.body.appendChild(textarea);
            textarea.focus();
            textarea.select();
            try {
              document.execCommand("copy");
              newCopyBtn.classList.add("copied");
              if (icon) icon.className = "bi bi-check2";
              setTimeout(function () {
                newCopyBtn.classList.remove("copied");
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
      // Skip if already processed
      if (pre.querySelector(".code-header")) return;

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
      try {
        Prism.highlightAll();
      } catch (e) {
        console.error("Prism highlight error:", e);
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initBlogPost);
  } else {
    initBlogPost();
  }

  if (!window._blogPostListenerAdded) {
    const triggerInit = function () {
      if (window.location.pathname.includes('/blog/')) {
        setTimeout(initBlogPost, 50);
      }
    };
    document.body.addEventListener("htmx:restored", triggerInit);
    window._blogPostListenerAdded = true;
  }

})();
