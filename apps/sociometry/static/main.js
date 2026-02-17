(function () {
  const root = document.documentElement;
  const key = 'sociometry-theme';
  const current = localStorage.getItem(key) || 'light';
  root.setAttribute('data-theme', current);
  const btn = document.getElementById('themeToggle');
  if (btn) {
    btn.addEventListener('click', () => {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem(key, next);
    });
  }

  document.querySelectorAll('fieldset').forEach((field) => {
    field.addEventListener('change', (e) => {
      if (!e.target.matches('input[type="checkbox"]')) return;
      const checked = field.querySelectorAll('input[type="checkbox"]:checked');
      if (checked.length > 3) {
        e.target.checked = false;
      }
    });
  });
})();
