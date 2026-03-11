document.addEventListener("DOMContentLoaded", function () {
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

    window.addEventListener("scroll", updateProgressBar, { passive: true });
    updateProgressBar();
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
            if (label) label.textContent = "Copied!";
            setTimeout(function () {
              copyLinkBtn.classList.remove("copied");
              if (icon) icon.className = "bi bi-link-45deg";
              if (label) label.textContent = "Copy Link";
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
