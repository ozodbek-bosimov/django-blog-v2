// Live character counter + hard limit for the Project "description" field
// in the Django admin. Mirrors the Blog meta counter behaviour.
(function () {
  "use strict";

  function init() {
    var input = document.getElementById("id_description");
    if (!input) return;

    var maxChars = parseInt(input.getAttribute("maxlength"), 10);
    if (!maxChars || maxChars < 1) {
      maxChars = 2000;
    }
    input.setAttribute("maxlength", String(maxChars));

    var counter = document.getElementById("desc-char-counter");
    if (!counter) {
      counter = document.createElement("p");
      counter.id = "desc-char-counter";
      counter.style.cssText = "margin-top:6px; font-size:12px; color:#8f8f8f;";
      input.parentNode.appendChild(counter);
    }

    function update() {
      var length = (input.value || "").length;
      counter.textContent = length + " / " + maxChars;
      counter.style.color = length >= maxChars ? "#ba2121" : "#8f8f8f";
    }

    function trimToLimit() {
      var value = input.value || "";
      if (value.length > maxChars) {
        input.value = value.slice(0, maxChars);
      }
      update();
    }

    input.addEventListener("input", trimToLimit);
    input.addEventListener("paste", function () {
      setTimeout(trimToLimit, 0);
    });

    trimToLimit();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
