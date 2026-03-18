// Client-side thumbnail image size validation for Django admin
(function () {
  'use strict';

  var MAX_SIZE_MB = 2;
  var MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;
  var META_MAX_CHARS = 600;

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

  function enforceMetaLimit(input) {
    if (!input) return;

    input.setAttribute('maxlength', String(META_MAX_CHARS));

    var counterId = 'meta-char-counter';
    var counter = document.getElementById(counterId);

    if (!counter) {
      counter = document.createElement('p');
      counter.id = counterId;
      counter.style.cssText = 'margin-top:6px; font-size:12px; color:#8f8f8f;';
      input.parentNode.appendChild(counter);
    }

    function updateCounter() {
      var length = (input.value || '').length;
      counter.textContent = length + ' / ' + META_MAX_CHARS;
      counter.style.color = length >= META_MAX_CHARS ? '#ba2121' : '#8f8f8f';
    }

    function trimToLimit() {
      var value = input.value || '';
      if (value.length > META_MAX_CHARS) {
        input.value = value.slice(0, META_MAX_CHARS);
      }
      updateCounter();
    }

    input.addEventListener('input', trimToLimit);
    input.addEventListener('paste', function () {
      setTimeout(trimToLimit, 0);
    });

    trimToLimit();
  }

  document.addEventListener('DOMContentLoaded', function () {
    var thumbnailInput = document.getElementById('id_thumbnail_img');
    if (thumbnailInput) {
      thumbnailInput.addEventListener('change', function () { validateThumbnail(this); });
    }

    var metaInput = document.getElementById('id_meta');
    enforceMetaLimit(metaInput);
  });
})();
