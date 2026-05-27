// Back to Top Button
const backToTopBtn = document.getElementById("back-to-top");
if (backToTopBtn) {
  window.addEventListener(
    "scroll",
    function () {
      if (window.scrollY > 400) {
        backToTopBtn.classList.add("visible");
      } else {
        backToTopBtn.classList.remove("visible");
      }
    },
    { passive: true },
  );

  backToTopBtn.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: "smooth" });
    
    // Add fly animation class
    backToTopBtn.classList.add("fly-animation");
    
    // Remove focus to prevent sticky hover/active states on mobile
    backToTopBtn.blur();
    
    // Remove class after animation finishes (0.8s match with CSS)
    setTimeout(() => {
      backToTopBtn.classList.remove("fly-animation");
    }, 800);
  });
}

// Mobile Menu
const toggleButton = document.querySelector(".nav-btn");
const navbarContent = document.querySelector(".mob-nav");

if (toggleButton && navbarContent) {
  function toggleMobileMenu() {
    if (navbarContent.classList.contains("translate-x-full")) {
      navbarContent.classList.remove("translate-x-full", "opacity-0");
    } else {
      navbarContent.classList.add("translate-x-full", "opacity-0");
    }
  }

  toggleButton.addEventListener("click", toggleMobileMenu);

  document.querySelectorAll(".mob-nav a").forEach((link) => {
    link.addEventListener("click", () => {
      navbarContent.classList.add("translate-x-full", "opacity-0");
    });
  });

  document.addEventListener("click", (event) => {
    if (
      !navbarContent.contains(event.target) &&
      !toggleButton.contains(event.target)
    ) {
      navbarContent.classList.add("translate-x-full", "opacity-0");
    }
  });

  window.addEventListener("scroll", () => {
    navbarContent.classList.add("translate-x-full", "opacity-0");
  }, { passive: true });
}

// Search Modal
const searchBtns = document.querySelectorAll(".searchBtn, .searchBtn1");
const searchModal = document.querySelector(".searchModal");
const searchCloseBtn = document.querySelector(".searchCloseBtn");
const searchInput = document.querySelector(".searchInput");
const searchModalOverlay = searchModal?.querySelector(".searchModal-overlay");

function showSearchModal() {
  if (!searchModal) return;
  searchModal.style.display = "block";
  setTimeout(() => {
    if (searchInput) searchInput.focus();
  }, 50);
}

function hideSearchModal() {
  if (searchModal) {
    searchModal.style.display = "none";
    if (searchInput) searchInput.value = "";
  }
}

function submitSearchForm(event) {
  if (!searchInput) return;
  const searchQuery = searchInput.value.trim();
  if (!searchQuery) {
    event.preventDefault();
    searchInput.classList.add("shake");
    setTimeout(() => {
      searchInput.classList.remove("shake");
    }, 500);
  }
}

if (searchModal) {
  searchBtns.forEach((btn) => btn.addEventListener("click", showSearchModal));

  if (searchCloseBtn) {
    searchCloseBtn.addEventListener("click", hideSearchModal);
  }

  const searchForm = searchModal.querySelector("form");
  if (searchForm) {
    searchForm.addEventListener("submit", submitSearchForm);
  }

  window.addEventListener("click", (event) => {
    if (event.target === searchModal || event.target === searchModalOverlay) {
      hideSearchModal();
    }
  });

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && searchModal.style.display === "block") {
      hideSearchModal();
    }
  });
}

// ── Scroll Reveal Animations ──────────────────────────────────────
// Works on both mobile & desktop — triggered by scroll via IntersectionObserver
(function () {
  // Respect user's motion preferences
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    document
      .querySelectorAll(".reveal, .reveal-fade, .reveal-scale, .reveal-left")
      .forEach(function (el) {
        el.classList.add("reveal-visible");
      });
    return;
  }

  // Auto-assign stagger indices to children of .reveal-stagger
  document.querySelectorAll(".reveal-stagger").forEach(function (parent) {
    var children = parent.querySelectorAll(
      ":scope > .reveal, :scope > .reveal-scale, :scope > .reveal-fade, :scope > .reveal-left",
    );
    children.forEach(function (child, i) {
      child.style.setProperty("--reveal-i", i);
    });
  });

  if (!("IntersectionObserver" in window)) {
    // Fallback: just show everything
    document
      .querySelectorAll(".reveal, .reveal-fade, .reveal-scale, .reveal-left")
      .forEach(function (el) {
        el.classList.add("reveal-visible");
      });
    return;
  }

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          // Trigger if it's currently intersecting, OR if it's already above the viewport (user scrolled past it)
          if (entry.isIntersecting || entry.boundingClientRect.top < window.innerHeight) {
            entry.target.classList.add("reveal-visible");
            observer.unobserve(entry.target);
          }
        });
      },
    {
      threshold: 0.01,
      // Keep the trigger early and reliable across mobile browsers.
      rootMargin: "0px 0px 0px 0px",
    },
  );

  document
    .querySelectorAll(".reveal, .reveal-fade, .reveal-scale, .reveal-left")
    .forEach(function (el) {
      observer.observe(el);
    });



})();

// ── Mobile Touch Fix ──────────────────────────────────────────────
// Problem 1: "Sticky hover" — mobile browsers keep :hover after tap+navigate+back.
// Problem 2: No visible tap feedback — CSS :active is too brief on touch.
(function () {
  var isTouch = "ontouchstart" in window || navigator.maxTouchPoints > 0;
  if (!isTouch) return;

  var interactive =
    "a, button, .glass-card, .btn-social, .btn-primary, .btn-ghost, " +
    ".btn-hero-primary, .btn-hero-ghost, .btn-pagination, .nav-btn, " +
    ".solid-content-card";

  // ── Fix 1: Clear sticky hover on page restore ──────────────────
  // Pre-blur before page is cached
  window.addEventListener("pagehide", function () {
    if (document.activeElement) document.activeElement.blur();
  });

  // On restore (bfcache or Safari soft-load): force clear :hover
  window.addEventListener("pageshow", function () {
    if (document.activeElement && document.activeElement !== document.body) {
      document.activeElement.blur();
    }
    // Force pointer-events cycle to reset :hover state
    document.body.classList.add("no-hover-reset");
    requestAnimationFrame(function () {
      document.body.classList.remove("no-hover-reset");
    });
  });

  // ── Fix 2: Tap feedback via .tapped class ──────────────────────
  var tappedEl = null;
  var clearTimer = null;

  document.addEventListener(
    "touchstart",
    function (e) {
      var el = e.target.closest(interactive);
      if (!el) return;

      if (tappedEl && tappedEl !== el) {
        tappedEl.classList.remove("tapped");
      }

      tappedEl = el;
      el.classList.add("tapped");

      clearTimeout(clearTimer);
      clearTimer = setTimeout(function () {
        if (tappedEl) {
          tappedEl.classList.remove("tapped");
          tappedEl = null;
        }
      }, 400);
    },
    { passive: true },
  );

  document.addEventListener(
    "touchend",
    function () {
      if (!tappedEl) return;
      var el = tappedEl;

      clearTimeout(clearTimer);
      setTimeout(function () {
        el.classList.remove("tapped");
        el.blur();
        tappedEl = null;
      }, 150);
    },
    { passive: true },
  );

  document.addEventListener(
    "touchmove",
    function () {
      if (tappedEl) {
        tappedEl.classList.remove("tapped");
        tappedEl = null;
        clearTimeout(clearTimer);
      }
    },
    { passive: true },
  );
})();
