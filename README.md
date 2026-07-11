# wheee88.github.io

Personal academic homepage of **Hwanhee Cho** (Senior Researcher, Korea Railroad Research Institute), served by GitHub Pages at [wheee88.github.io](https://wheee88.github.io).

Based on the [researcher](https://github.com/ankitsultana/researcher) Jekyll template ([GNU GPL v3](LICENSE)).

## Structure

* `index.md` — main page (about, education, selected publications, data-driven sections)
* `publications.md` — full publication list, collapsible by year
* `contact.md` — contact page
* `_data/publications.yml` — publication data (`selected: true` marks papers shown on the main page)
* `_data/cv.yml` — profile data used to build `cv.pdf`
* `data/*.json` — auto-fetched (patents, projects, news) and manual (talks, awards) section data
* `_includes/pub_item.html` — shared publication card markup
* `js/main.js` — language toggle (EN/KO), dark mode, back-to-top, BibTeX copy
* `js/sections.js` — renders `data/*.json` sections client-side; empty sections stay hidden
* `scripts/` — data pipeline (see below)

## Automated data pipeline

`.github/workflows/update-data.yml` runs **every Monday 06:00 KST** and on demand
(Actions 탭 → *Update data & CV* → **Run workflow**). Each step:

| Step | Script | Source | Output |
|------|--------|--------|--------|
| Publications | `scripts/update_publications.py` | OpenAlex + ORCID [0000-0002-4966-0099](https://orcid.org/0000-0002-4966-0099) (키 불필요) | `_data/publications.yml`, `data/news.json` |
| Patents | `scripts/fetch_patents.py` | KIPRIS Plus API — 발명자 "조환희" & 출원인 "한국철도기술연구원" | `data/patents.json` |
| Funded projects | `scripts/fetch_projects.py` | NTIS Open API — "조환희 한국철도기술연구원" | `data/projects.json` |
| CV | `scripts/build_cv.py` | 위 데이터 전부 | `cv.pdf` |

실패한 스텝은 기존 JSON을 **덮어쓰지 않고** 워크플로만 실패로 표시됩니다. 성공한 스텝의 결과만 커밋되고, 커밋되면 GitHub Pages가 자동으로 재배포합니다. 새 논문이 추가되면 `data/news.json`에 소식 한 줄이 자동 생성됩니다.

### API 키 발급 (각 5분)

**KIPRIS** — 특허 데이터용
1. <https://plus.kipris.or.kr> 회원가입 → 로그인
2. [오픈API] → "특허·실용신안 정보 검색 서비스" **활용 신청** (무료)
3. 발급된 **ServiceKey**를 아래 방법으로 `KIPRIS_API_KEY` 시크릿에 등록

**NTIS** — 연구과제 데이터용
1. <https://www.ntis.go.kr> 회원가입 → [OpenAPI](https://www.ntis.go.kr/rndopen/api/mng/apiMain.do) → "국가R&D 과제검색 서비스(대국민용)" 활용 신청
2. 발급된 **인증키(apprvKey)**를 `NTIS_API_KEY` 시크릿에 등록

### 시크릿 등록

GitHub 저장소 → **Settings → Secrets and variables → Actions → New repository secret**
* Name: `KIPRIS_API_KEY`, Secret: (KIPRIS ServiceKey)
* Name: `NTIS_API_KEY`, Secret: (NTIS apprvKey)

키가 없으면 해당 스텝은 건너뛰고 나머지(논문/CV)만 갱신됩니다.

### 첫 실행 & 검수

1. 시크릿 등록 후 **Actions → Update data & CV → Run workflow** 클릭
2. 실행이 끝나면 `data/patents.json`, `data/projects.json`을 열어 **동명이인 항목이 섞였는지 1회 검수** (표기 차이·동명이인 때문에 첫 결과에 오탐이 있을 수 있음)
3. 잘못된 항목은 JSON에서 삭제 — 이후 실행은 전체를 다시 쓰므로, 오탐이 반복되면 스크립트의 필터(출원인/기관명)를 좁히면 됨
4. NTIS 응답 스키마는 공식 매뉴얼 PDF에만 공개되어 있어 `scripts/fetch_projects.py`의 태그 후보가 안 맞을 수 있음 — 워크플로 로그에 원본 XML 헤드가 출력되니 그걸 보고 `FIELDS` 후보를 조정

### 수동 관리 데이터

* `data/talks.json`, `data/awards.json` — 파일 안 `_schema` 형식대로 `items`에 추가하면 해당 섹션이 자동으로 나타납니다 (비어 있으면 섹션·메뉴 숨김)
* `data/news.json` — 자동 생성 외에 손으로 항목을 추가해도 됩니다 (최근 5건 표시)

## CV PDF

`cv.pdf`는 `_data/cv.yml`(프로필) + 논문/특허/과제 데이터로 워크플로가 자동 재생성하며, 헤더의 **CV** 버튼으로 내려받을 수 있습니다. 학력·경력이 바뀌면 `_data/cv.yml`을 수정하세요.
