// Stabilize CKEditor layout in Django admin after async init and viewport changes.
(function () {
  'use strict';

  function safeRelayout(editor) {
    if (!editor) return;

    // CKEditor UI size is computed during init; force one more pass after paint.
    requestAnimationFrame(function () {
      if (editor.ui && typeof editor.ui.update === 'function') {
        editor.ui.update();
      }
      window.dispatchEvent(new Event('resize'));
    });

    setTimeout(function () {
      if (editor.ui && typeof editor.ui.update === 'function') {
        editor.ui.update();
      }
      window.dispatchEvent(new Event('resize'));
    }, 120);
  }

  function attachEditorFix(id) {
    if (typeof window.ckeditorRegisterCallback !== 'function') return;

    window.ckeditorRegisterCallback(id, function (editor) {
      safeRelayout(editor);

      if (editor.editing && editor.editing.view && editor.editing.view.document) {
        editor.editing.view.document.on('focus', function () {
          safeRelayout(editor);
        });
      }

      if (editor.model && editor.model.document) {
        editor.model.document.on('change:data', function () {
          safeRelayout(editor);
        });
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('textarea.django_ckeditor_5').forEach(function (el) {
      if (el.id) attachEditorFix(el.id);
    });
  });
}());
