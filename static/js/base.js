// Back to Top Button
const backToTopBtn = document.getElementById("back-to-top");
const prefersReducedMotion = window.matchMedia(
  "(prefers-reduced-motion: reduce)",
);

if (backToTopBtn) {
  backToTopBtn.addEventListener("click", function () {
    window.scrollTo({
      top: 0,
      behavior: prefersReducedMotion.matches ? "auto" : "smooth",
    });
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
}

let latestScrollY = window.scrollY;
let isScrollTicking = false;

function runScrollEffects() {
  if (backToTopBtn) {
    if (latestScrollY > 400) {
      backToTopBtn.classList.add("visible");
    } else {
      backToTopBtn.classList.remove("visible");
    }
  }

  if (toggleButton && navbarContent) {
    navbarContent.classList.add("translate-x-full", "opacity-0");
  }

  isScrollTicking = false;
}

window.addEventListener(
  "scroll",
  () => {
    latestScrollY = window.scrollY;
    if (!isScrollTicking) {
      isScrollTicking = true;
      requestAnimationFrame(runScrollEffects);
    }
  },
  { passive: true },
);

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

