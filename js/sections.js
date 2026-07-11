/* Client-side rendering of data-driven sections (news, patents, projects,
 * talks, awards). Each section stays hidden until its JSON has items; the
 * matching nav anchor is hidden too. Runs on every page so nav stays
 * consistent; sections themselves only exist on the home page. */
(function () {
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function bi(en, ko) {
    if (!ko || en === ko) { return esc(en || ko); }
    return '<span lang="en">' + esc(en) + '</span><span lang="ko" hidden>' + esc(ko) + '</span>';
  }

  function reveal(sectionId, anchor) {
    var sec = document.getElementById(sectionId);
    if (sec) { sec.hidden = false; }
    document.querySelectorAll('#navlist a[href$="#' + anchor + '"]').forEach(function (a) {
      var li = a.closest('li');
      if (li) { li.hidden = false; }
    });
  }

  function load(name) {
    return fetch('/data/' + name + '.json', { cache: 'no-cache' })
      .then(function (r) { return r.ok ? r.json() : { items: [] }; })
      .catch(function () { return { items: [] }; });
  }

  var RENDER = {
    news: function (items) {
      var el = document.getElementById('news-list');
      if (!el) { return; }
      el.innerHTML = items.slice(0, 5).map(function (n) {
        return '<li class="news-item"><span class="news-date">' + esc(n.date) + '</span> — ' +
          bi(n.en, n.ko) +
          (n.title ? ' <span class="news-title">(' + esc(n.title) + ')</span>' : '') + '</li>';
      }).join('');
      reveal('news-section', 'news');
    },
    patents: function (items) {
      var el = document.getElementById('patents-list');
      if (!el) { return; }
      el.innerHTML = items.map(function (p) {
        var nums = [];
        if (p.applicationNumber) { nums.push('출원 ' + esc(p.applicationNumber)); }
        if (p.registrationNumber) { nums.push('등록 ' + esc(p.registrationNumber)); }
        return '<li class="pub-item">' + esc(p.title) +
          (p.status ? ' <span class="pub-badge">' + esc(p.status) + '</span>' : '') +
          '<span class="pub-links">' + nums.join(' · ') +
          (p.year ? ' · ' + esc(p.year) : '') +
          (p.link ? ' <a href="' + esc(p.link) + '" target="_blank" rel="noopener">KIPRIS</a>' : '') +
          '</span></li>';
      }).join('');
      reveal('patents-section', 'patents');
    },
    projects: function (items) {
      var el = document.getElementById('projects-list');
      if (!el) { return; }
      el.innerHTML = items.map(function (p) {
        var meta = [p.period, p.ministry, p.role].filter(Boolean).map(esc).join(' · ');
        return '<li class="pub-item">' + esc(p.title) +
          (meta ? '<span class="pub-links">' + meta + '</span>' : '') + '</li>';
      }).join('');
      reveal('projects-section', 'projects');
    },
    talks: function (items) {
      simpleList('talks', items);
    },
    awards: function (items) {
      simpleList('awards', items);
    }
  };

  function simpleList(name, items) {
    var el = document.getElementById(name + '-list');
    if (!el) { return; }
    el.innerHTML = items.map(function (t) {
      var body = bi(t.en, t.ko);
      if (t.link) { body = '<a href="' + esc(t.link) + '" target="_blank" rel="noopener">' + body + '</a>'; }
      return '<li class="news-item"><span class="news-date">' + esc(t.date) + '</span> — ' + body + '</li>';
    }).join('');
    reveal(name + '-section', name);
  }

  var names = Object.keys(RENDER);
  Promise.all(names.map(load)).then(function (results) {
    var any = false;
    results.forEach(function (data, i) {
      var items = (data && data.items) || [];
      if (items.length) { RENDER[names[i]](items); any = true; }
    });
    // Re-sync bilingual visibility for freshly injected markup
    if (any && window.applyLang) {
      window.applyLang(document.documentElement.getAttribute('lang') || 'en');
    }
  });
})();
