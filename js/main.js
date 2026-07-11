(function () {
  var html = document.documentElement;

  /* ---------- Language toggle ---------- */

  function applyLang(lang) {
    document.querySelectorAll('span[lang="en"], span[lang="ko"]').forEach(function (el) {
      el.hidden = el.getAttribute('lang') !== lang;
    });
    html.setAttribute('lang', lang);
    html.classList.toggle('lang-ko', lang === 'ko');
    document.querySelectorAll('#lang-toggle .lang-opt').forEach(function (opt) {
      opt.classList.toggle('active', opt.getAttribute('data-lang') === lang);
    });
  }

  var savedLang = 'en';
  try { savedLang = localStorage.getItem('lang') || 'en'; } catch (e) {}
  applyLang(savedLang);

  var langToggle = document.getElementById('lang-toggle');
  if (langToggle) {
    langToggle.addEventListener('click', function (e) {
      e.preventDefault();
      var opt = e.target.closest('.lang-opt');
      var lang = opt ? opt.getAttribute('data-lang')
                     : (html.getAttribute('lang') === 'ko' ? 'en' : 'ko');
      applyLang(lang);
      try { localStorage.setItem('lang', lang); } catch (err) {}
    });
  }

  /* ---------- Dark mode toggle ---------- */

  var themeBtn = document.getElementById('theme-toggle');

  function currentTheme() {
    if (html.classList.contains('dark')) { return 'dark'; }
    if (html.classList.contains('light')) { return 'light'; }
    return (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)
      ? 'dark' : 'light';
  }

  function updateThemeIcon() {
    if (themeBtn) { themeBtn.textContent = currentTheme() === 'dark' ? '☀️' : '🌙'; }
  }

  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      html.classList.remove('dark', 'light');
      html.classList.add(next);
      try { localStorage.setItem('theme', next); } catch (e) {}
      updateThemeIcon();
    });
    updateThemeIcon();
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateThemeIcon);
    }
  }

  /* ---------- Back to top ---------- */

  var topBtn = document.getElementById('back-to-top');
  if (topBtn) {
    var onScroll = function () { topBtn.hidden = window.scrollY < 400; };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    topBtn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ---------- BibTeX copy ---------- */

  document.querySelectorAll('.bibtex-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var d = btn.dataset;
      var firstAuthor = (d.authors || '').split(',')[0].trim().split(' ').pop().toLowerCase();
      var firstWord = (d.title || '').toLowerCase().replace(/[^a-z0-9 ]/g, '').trim().split(/\s+/)[0] || '';
      var lines = ['@article{' + firstAuthor + d.year + firstWord + ','];
      lines.push('  author  = {' + (d.authors || '').split(', ').join(' and ') + '},');
      lines.push('  title   = {' + (d.title || '') + '},');
      if (d.venue) { lines.push('  journal = {' + d.venue + '},'); }
      lines.push('  year    = {' + d.year + '},');
      if (d.month) { lines.push('  month   = {' + d.month + '},'); }
      if (d.doi) { lines.push('  doi     = {' + d.doi + '},'); }
      lines.push('}');
      var text = lines.join('\n');

      function done() {
        var old = btn.textContent;
        btn.textContent = 'Copied!';
        btn.disabled = true;
        setTimeout(function () { btn.textContent = old; btn.disabled = false; }, 1500);
      }

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text, done); });
      } else {
        fallbackCopy(text, done);
      }
    });
  });

  function fallbackCopy(text, done) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
    done();
  }
})();
