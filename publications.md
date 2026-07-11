---
layout: default
title: Publications
permalink: /publications/
---

## <span lang="en">Publications</span><span lang="ko" hidden>논문</span>

<span lang="en">First-author papers are <span class="pub-highlight">highlighted</span>. The full record is also available on [ORCID](https://orcid.org/0000-0002-4966-0099).</span><span lang="ko" hidden>1저자 논문은 <span class="pub-highlight">하이라이트</span>로 표시되어 있습니다. 전체 목록은 [ORCID](https://orcid.org/0000-0002-4966-0099)에서도 확인할 수 있습니다.</span>

{% assign years = site.data.publications | map: "year" | uniq %}
{% for y in years %}
<details class="pub-year"{% if forloop.index <= 2 %} open{% endif %}>
<summary>{{ y }}</summary>
<ul class="pub-list">
{% assign year_pubs = site.data.publications | where: "year", y %}{% for pub in year_pubs %}{% include pub_item.html pub=pub %}{% endfor %}
</ul>
</details>
{% endfor %}
