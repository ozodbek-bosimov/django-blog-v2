(function () {
  function initBlogPost() {
    // Clean up previous scroll listener
    if (window._blogpostScrollListener) {
      window.removeEventListener("scroll", window._blogpostScrollListener);
      window._blogpostScrollListener = null;
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

    /* ── CKEditor / Bare Links Embeds Processing ───────────────────── */
    function processEmbeds() {
      const content = document.querySelector('.blog-content');
      if (!content) return;

      // 1. Process <oembed> tags (Twitter, Instagram)
      content.querySelectorAll('oembed').forEach(oembed => {
        let url = oembed.getAttribute('url') || '';
        if (!url) return;
        let figure = oembed.closest('figure.media') || oembed.parentElement;

        if (url.includes('twitter.com') || url.includes('x.com')) {
          url = url.replace('x.com', 'twitter.com');
          const blockquote = document.createElement('blockquote');
          blockquote.className = 'twitter-tweet';
          blockquote.setAttribute('data-theme', 'dark');
          const a = document.createElement('a');
          a.href = url;
          blockquote.appendChild(a);
          figure.parentNode.replaceChild(blockquote, figure);
        } else if (url.includes('instagram.com')) {
          const blockquote = document.createElement('blockquote');
          blockquote.className = 'instagram-media';
          blockquote.setAttribute('data-instgrm-permalink', url);
          blockquote.setAttribute('data-instgrm-version', '14');
          blockquote.setAttribute('data-theme', 'dark');
          blockquote.style.maxWidth = '540px';
          blockquote.style.width = '100%';
          figure.parentNode.replaceChild(blockquote, figure);
        }
      });

      // 2. Convert bare links (LinkedIn, Instagram reels) into embeds
      content.querySelectorAll('a').forEach(link => {
        const url = link.href;
        const parent = link.parentElement;
        if (!parent || parent.tagName !== 'P') return;
        if (parent.textContent.trim() !== link.textContent.trim()) return;

        if (url.includes('linkedin.com/posts/')) {
          const match = url.match(/-([0-9]{19})/);
          if (match && match[1]) {
            const urnId = match[1];
            let urnType = 'share';
            if (url.includes('ugcPost')) urnType = 'ugcPost';
            else if (url.includes('activity')) urnType = 'activity';
            const iframe = document.createElement('iframe');
            iframe.src = `https://www.linkedin.com/embed/feed/update/urn:li:${urnType}:${urnId}?theme=dark`;
            iframe.height = "600";
            iframe.width = "100%";
            iframe.style.minHeight = "550px";
            iframe.style.colorScheme = "dark";
            iframe.frameBorder = "0";
            iframe.allowFullscreen = true;
            iframe.title = "Embedded LinkedIn post";
            iframe.classList.add("w-full", "rounded-lg", "shadow-sm", "my-4");
            parent.parentNode.replaceChild(iframe, parent);
          }
        } else if (url.includes('instagram.com/')) {
          const blockquote = document.createElement('blockquote');
          blockquote.className = 'instagram-media';
          blockquote.setAttribute('data-instgrm-permalink', url);
          blockquote.setAttribute('data-instgrm-version', '14');
          blockquote.setAttribute('data-theme', 'dark');
          blockquote.style.maxWidth = '540px';
          blockquote.style.width = '100%';
          parent.parentNode.replaceChild(blockquote, parent);
        }
      });

      // 3. Process widgets with retries if scripts are still loading
      let retries = 0;
      function tryProcessWidgets() {
        let processedTwitter = false;
        let processedInstagram = false;

        if (window.twttr && window.twttr.widgets) {
          window.twttr.widgets.load();
          processedTwitter = true;
        }
        if (window.instgrm && window.instgrm.Embeds) {
          window.instgrm.Embeds.process();
          processedInstagram = true;
        }

        const hasTwitter = !!content.querySelector('.twitter-tweet') || !!content.querySelector('blockquote.twitter-tweet');
        const hasInstagram = !!content.querySelector('.instagram-media') || !!content.querySelector('blockquote.instagram-media');

        const needTwitterRetry = hasTwitter && !processedTwitter;
        const needInstagramRetry = hasInstagram && !processedInstagram;

        if ((needTwitterRetry || needInstagramRetry) && retries < 15) {
          retries++;
          setTimeout(tryProcessWidgets, 300);
        }
      }
      
      setTimeout(tryProcessWidgets, 100);
    }

    try {
      processEmbeds();
    } catch (e) {
      console.error("Embed processing error:", e);
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

      window._blogpostScrollListener = updateProgressBar;
      window.addEventListener("scroll", window._blogpostScrollListener, { passive: true });
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

  let _blogPostInitTimer = null;
  function debouncedInitBlogPost() {
    if (_blogPostInitTimer) clearTimeout(_blogPostInitTimer);
    _blogPostInitTimer = setTimeout(initBlogPost, 50);
  }

  // Run immediately for initial page load (DOM is already parsed up to this point)
  setTimeout(debouncedInitBlogPost, 10);

  if (!window._blogPostListenerAdded) {
    document.body.addEventListener("htmx:afterSettle", function () {
      if (window.location.pathname.includes('/blog/')) {
        debouncedInitBlogPost();
      } else {
        if (window._blogpostScrollListener) {
          window.removeEventListener("scroll", window._blogpostScrollListener);
          window._blogpostScrollListener = null;
        }
      }
    });
    document.body.addEventListener("htmx:restored", function () {
      if (window.location.pathname.includes('/blog/')) {
        debouncedInitBlogPost();
      } else {
        if (window._blogpostScrollListener) {
          window.removeEventListener("scroll", window._blogpostScrollListener);
          window._blogpostScrollListener = null;
        }
      }
    });
    window._blogPostListenerAdded = true;
  }

})();
