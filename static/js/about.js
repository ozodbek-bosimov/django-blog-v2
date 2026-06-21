function initAbout() {
  document.querySelectorAll('.skill-bar').forEach(bar => {
    const percentage = bar.getAttribute('data-percentage');
    bar.style.setProperty('--target-width', percentage + '%');
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initAbout);
} else {
  initAbout();
}

if (!window._aboutListenerAdded) {
  document.body.addEventListener("htmx:afterSettle", function () {
    if (window.location.pathname.includes('/about')) {
      initAbout();
    }
  });
  window._aboutListenerAdded = true;
}


function toggleBullets(listId) {
    const list = document.getElementById(listId);
    if (!list) return;
    const hiddenItems = list.querySelectorAll('.hidden-bullet');
    const ellipsis = list.querySelector('.timeline-ellipsis');
    const moreBtn = list.querySelector('.timeline-inline-more');
    
    if (hiddenItems.length > 0) {
        hiddenItems.forEach(item => {
            item.classList.remove('hidden-bullet');
            item.classList.add('shown-bullet');
        });
        if (ellipsis) ellipsis.style.display = 'none';
        if (moreBtn) moreBtn.style.display = 'none';
    } else {
        const shownItems = list.querySelectorAll('.shown-bullet');
        shownItems.forEach(item => {
            item.classList.remove('shown-bullet');
            item.classList.add('hidden-bullet');
        });
        if (ellipsis) ellipsis.style.display = 'inline';
        if (moreBtn) moreBtn.style.display = 'inline';
    }
}
