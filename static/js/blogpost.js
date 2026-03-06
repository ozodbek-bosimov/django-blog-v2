document.addEventListener('DOMContentLoaded', function () {
  const toPrettyLanguage = (lang) => {
    if (!lang) return 'Python';
    const normalized = lang.toLowerCase();
    if (normalized === 'cpp') return 'C++';
    if (normalized === 'cs') return 'C#';
    return normalized.charAt(0).toUpperCase() + normalized.slice(1);
  };

  const preElements = document.querySelectorAll('pre');

  preElements.forEach(pre => {
    const code = pre.querySelector('code');
    if (!code) return;

    const languageClass = [...code.classList, ...pre.classList]
      .find(cls => cls.startsWith('language-'));
    const language = languageClass ? languageClass.replace('language-', '') : 'python';

    if (!languageClass) {
      pre.classList.add('language-python');
      code.classList.add('language-python');
    }

    const header = document.createElement('div');
    header.className = 'code-header';

    const langLabel = document.createElement('span');
    langLabel.className = 'code-lang';
    langLabel.textContent = toPrettyLanguage(language);

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn';
    copyBtn.type = 'button';
    copyBtn.innerHTML = '<i class="bi bi-clipboard"></i> Copy';

    copyBtn.addEventListener('click', function () {
      navigator.clipboard.writeText(code.innerText).then(() => {
        copyBtn.classList.add('copied');
        copyBtn.innerHTML = '<i class="bi bi-check2"></i> Copied!';
        setTimeout(() => {
          copyBtn.classList.remove('copied');
          copyBtn.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
        }, 2000);
      });
    });

    header.appendChild(langLabel);
    header.appendChild(copyBtn);
    pre.insertBefore(header, pre.firstChild);
  });

  if (typeof Prism !== 'undefined') {
    Prism.highlightAll();
  }
});
