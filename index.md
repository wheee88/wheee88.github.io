---
layout: default
title: Hwanhee Cho
---

## <span class="en">About Me</span><span class="ko">소개</span>

<img class="profile-picture" src="CHH.jpg">

<span class="en">I am a senior researcher in the Electric Railway Power Research Division at the Korea Railroad Research Institute (KRRI). My research focuses on power system stability and oscillation analysis, and on electric railway power supply systems including energy-saving operation, hybrid energy storage, and MVDC.</span><span class="ko">한국철도기술연구원(KRRI) 전철전력연구실 선임연구원으로 재직하고 있습니다. 전력계통 안정도 및 진동 해석, 그리고 에너지 절감 운전·하이브리드 에너지저장장치(ESS)·MVDC 등 전기철도 급전 시스템을 연구하고 있습니다.</span>

## <span class="en">Education</span><span class="ko">학력</span>

- <span class="en">B.S. in Electrical and Electronic Engineering, Dankook University, Yongin, South Korea (2007 – 2014)</span><span class="ko">단국대학교 전자전기공학부 학사 (2007 – 2014)</span>
- <span class="en">Integrated M.S. and Ph.D. in Electrical and Electronic Engineering, Korea University, Seoul, South Korea (2014 – 2020)</span><span class="ko">고려대학교 전기전자공학과 석박사통합과정 (2014 – 2020)</span>

## <span class="en">Experience</span><span class="ko">경력</span>

- <span class="en">Secondment to the Korea Agency for Infrastructure Technology Advancement (KAIA), Anyang-si, South Korea (Feb. 23, 2026 – Feb. 22, 2027)</span><span class="ko">국토교통과학기술진흥원(KAIA) 파견 (2026. 02. 23 – 2027. 02. 22)</span>
- <span class="en">Senior Researcher, Electric Railway Power Research Division, Korea Railroad Research Institute (KRRI), Uiwang-si, South Korea (since 2020)</span><span class="ko">한국철도기술연구원(KRRI) 전철전력연구실 선임연구원 (2020 – 현재)</span>

## <span class="en">Research Interests</span><span class="ko">연구 분야</span>

* **<span class="en">Power Systems</span><span class="ko">전력계통</span>** : <span class="en">Power System Oscillations, PMU, Power System Stability etc.</span><span class="ko">전력계통 진동, PMU, 전력계통 안정도 등</span>
* **<span class="en">Electric Railway Systems</span><span class="ko">전기철도</span>** : <span class="en">Energy Saving, Hybrid ESS, MVDC, AC/DC Hybrid, Railway Computation etc.</span><span class="ko">에너지 절감, 하이브리드 ESS, MVDC, AC/DC 하이브리드, 철도 급전 해석 등</span>

## <span class="en">Skills</span><span class="ko">보유 기술</span>

* **<span class="en">Engineering Tools</span><span class="ko">엔지니어링 툴</span>** : PSSE, PSCAD, MATLAB, Simulink, and OPAL-RT (eFPGASim, eMEGASim)
* **<span class="en">Languages</span><span class="ko">프로그래밍 언어</span>** : C and Python

## <span class="en">Publications</span><span class="ko">논문</span>

<span class="en">First-author papers are <span class="pub-highlight">highlighted</span>. The full record is also available on [ORCID](https://orcid.org/0000-0002-4966-0099).</span><span class="ko">1저자 논문은 <span class="pub-highlight">하이라이트</span>로 표시되어 있습니다. 전체 목록은 [ORCID](https://orcid.org/0000-0002-4966-0099)에서도 확인할 수 있습니다.</span>

{% assign prev_year = 0 %}
{% for pub in site.data.publications %}{% if pub.year != prev_year %}
### {{ pub.year }}
{% assign prev_year = pub.year %}{% endif %}
{% capture pub_text %}{{ pub.authors }}, "{{ pub.title }},"{% if pub.venue and pub.venue != "" %} *{{ pub.venue }}*,{% endif %} {{ pub.date_label }}.{% endcapture %}* {% if pub.highlight %}<span class="pub-highlight">**{{ pub_text }}**</span>{% else %}{{ pub_text }}{% endif %}{% if pub.url %} [[DOI]({{ pub.url }})]{% endif %}
{% endfor %}
