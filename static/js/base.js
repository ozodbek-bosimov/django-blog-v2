// Mobile Menu
const toggleButton = document.querySelector('.nav-btn');
const navbarContent = document.querySelector('.mob-nav');

function toggleMobileMenu() {
  if (navbarContent.classList.contains('translate-x-full')) {
    navbarContent.classList.remove('translate-x-full', 'opacity-0');
  } else {
    navbarContent.classList.add('translate-x-full', 'opacity-0');
  }
}

toggleButton.addEventListener('click', toggleMobileMenu);

document.querySelectorAll('.mob-nav a').forEach(link => {
  link.addEventListener('click', () => {
    navbarContent.classList.add('translate-x-full', 'opacity-0');
  });
});

document.addEventListener('click', (event) => {
  if (!navbarContent.contains(event.target) && !toggleButton.contains(event.target)) {
    navbarContent.classList.add('translate-x-full', 'opacity-0');
  }
});

window.addEventListener('scroll', () => {
  navbarContent.classList.add('translate-x-full', 'opacity-0');
});

// Search Modal
const searchBtns = document.querySelectorAll(".searchBtn, .searchBtn1");
const searchModal = document.querySelector(".searchModal");
const searchCloseBtn = document.querySelector(".searchCloseBtn");
const searchInput = document.querySelector(".searchInput");

function showSearchModal() {
  searchModal.style.display = "block";
  setTimeout(() => { searchInput.focus(); }, 50);
}

function hideSearchModal() {
  searchModal.style.display = "none";
}

function submitSearchForm(event) {
  const searchQuery = searchInput.value.trim();
  if (!searchQuery) {
    event.preventDefault();
    searchInput.classList.add('shake');
    setTimeout(() => { searchInput.classList.remove('shake'); }, 500);
  }
}

searchBtns.forEach(btn => btn.addEventListener("click", showSearchModal));

if (searchCloseBtn) {
  searchCloseBtn.addEventListener("click", hideSearchModal);
}

const searchForm = searchModal.querySelector('form');
if (searchForm) {
  searchForm.addEventListener("submit", submitSearchForm);
}

window.addEventListener("click", (event) => {
  if (event.target === searchModal) {
    hideSearchModal();
  } else {
    const overlayDiv = searchModal.querySelector('.absolute.inset-0.bg-gray-800.opacity-75');
    const modalContainer = searchModal.querySelector('.fixed.inset-0.transition-opacity');
    if (event.target === overlayDiv || event.target === modalContainer) {
      hideSearchModal();
    }
  }
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && searchModal.style.display === "block") {
    hideSearchModal();
  }
});
