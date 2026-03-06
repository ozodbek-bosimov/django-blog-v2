document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('.skill-bar').forEach(bar => {
    const percentage = bar.getAttribute('data-percentage');
    bar.style.setProperty('--target-width', percentage + '%');
  });
});
