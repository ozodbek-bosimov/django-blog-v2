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
  if (searchModal) searchModal.style.display = "none";
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
