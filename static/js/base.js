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
  });
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

// ── Hero Interactive Dot Grid ────────────────────────────────────
(function () {
  const canvas = document.getElementById("hero-grid");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  let w, h, cols, rows, offsetX, offsetY;
  const gap = 32;
  const dotBase = 0.4;
  const mouse = { x: -1000, y: -1000 };
  const radius = 120;

  function resize() {
    w = canvas.width = window.innerWidth * devicePixelRatio;
    h = canvas.height = window.innerHeight * devicePixelRatio;
    canvas.style.width = window.innerWidth + "px";
    canvas.style.height = window.innerHeight + "px";
    ctx.scale(devicePixelRatio, devicePixelRatio);
    
    cols = Math.floor(window.innerWidth / gap) + 1;
    rows = Math.floor(window.innerHeight / gap) + 1;
    
    // Calculate offsets to keep grid perfectly centered and symmetrical
    const gridWidth = (cols - 1) * gap;
    const gridHeight = (rows - 1) * gap;
    offsetX = (window.innerWidth - gridWidth) / 2;
    offsetY = (window.innerHeight - gridHeight) / 2;
  }

  resize();
  window.addEventListener("resize", resize);

  window.addEventListener("mousemove", (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  window.addEventListener("mouseleave", () => {
    mouse.x = -1000;
    mouse.y = -1000;
  });

  window.addEventListener("scroll", () => {
    mouse.x = -1000;
    mouse.y = -1000;
  }, { passive: true });

  function draw() {
    ctx.clearRect(0, 0, w / devicePixelRatio, h / devicePixelRatio);
    for (let i = 0; i < cols; i++) {
      for (let j = 0; j < rows; j++) {
        const x = offsetX + i * gap;
        const y = offsetY + j * gap;
        const dx = mouse.x - x;
        const dy = mouse.y - y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const intensity = Math.max(0, 1 - dist / radius);

        ctx.beginPath();
        ctx.arc(x, y, dotBase + intensity * 2, 0, Math.PI * 2);

        if (intensity > 0) {
          const alpha = 0.08 + intensity * 0.7;
          ctx.fillStyle = `rgba(103, 232, 249, ${alpha})`;
        } else {
          ctx.fillStyle = "rgba(156, 163, 175, 0)";
        }
        ctx.fill();
      }
    }
    requestAnimationFrame(draw);
  }

  draw();
})();

// ── Hero Typing Effect ───────────────────────────────────────────
(function () {
  const el = document.getElementById("hero-typed");
  if (!el) return;

  const phrases = [
    "Sharing what I learn",
    "Documenting the journey",
    "Exploring new ideas",
    "Thinking out loud",
  ];

  let pi = 0,
    ci = 0,
    deleting = false;

  function tick() {
    const phrase = phrases[pi];
    if (!deleting) {
      el.textContent = phrase.slice(0, ci + 1);
      ci++;
      if (ci === phrase.length) {
        deleting = true;
        return setTimeout(tick, 2200);
      }
      return setTimeout(tick, 55);
    } else {
      el.textContent = phrase.slice(0, ci - 1);
      ci--;
      if (ci === 0) {
        deleting = false;
        pi = (pi + 1) % phrases.length;
        return setTimeout(tick, 350);
      }
      return setTimeout(tick, 30);
    }
  }

  setTimeout(tick, 600);
})();
