// Client-side thumbnail image size validation for Django admin
(function () {
  'use strict';

  var MAX_SIZE_MB = 2;
  var MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

  function validateThumbnail(input) {
    if (!input.files || input.files.length === 0) return;

    var file = input.files[0];
    var errorId = 'thumbnail-size-error';
    var existing = document.getElementById(errorId);

    if (file.size > MAX_SIZE_BYTES) {
      var sizeMB = (file.size / (1024 * 1024)).toFixed(1);

      if (!existing) {
        var msg = document.createElement('p');
        msg.id = errorId;
        msg.className = 'errornote';
        msg.style.cssText =
          'color:#ba2121; background:#fff0f0; border:1px solid #ba2121;' +
          ' padding:8px 12px; margin-top:8px; border-radius:4px;';
        input.parentNode.insertBefore(msg, input.nextSibling);
        existing = msg;
      }

      existing.textContent =
        'Image size is ' + sizeMB + ' MB — maximum allowed size is ' +
        MAX_SIZE_MB + ' MB. Please compress the image or choose a smaller file.';

      // Disable save buttons
      document.querySelectorAll('[name="_save"], [name="_continue"], [name="_addanother"]')
        .forEach(function (btn) { btn.disabled = true; });

      // Reset input so user must re-pick
      setTimeout(function () { input.value = ''; }, 0);
    } else {
      if (existing) existing.remove();
      document.querySelectorAll('[name="_save"], [name="_continue"], [name="_addanother"]')
        .forEach(function (btn) { btn.disabled = false; });
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    var input = document.getElementById('id_thumbnail_img');
    if (!input) return;
    input.addEventListener('change', function () { validateThumbnail(this); });
  });
})();
