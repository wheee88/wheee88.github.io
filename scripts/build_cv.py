#!/usr/bin/env python3
"""Assemble cv.pdf from the site's data sources.

Inputs: _data/cv.yml (profile), _data/publications.yml (papers),
data/patents.json and data/projects.json (auto-fetched; skipped when empty).

Rendered with WeasyPrint. English layout; Korean text (patent/project titles)
is covered by the Noto Sans CJK font installed in the workflow image
(fonts-noto-cjk) with common local fallbacks listed in the stylesheet.
"""

import html
import json
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cv.pdf"

CSS = """
@page { size: A4; margin: 2cm 1.8cm; @bottom-center {
    content: "Hwanhee Cho — CV — page " counter(page) " of " counter(pages);
    font-size: 8pt; color: #888; } }
body { font-family: "Noto Sans CJK KR", "Noto Sans KR", "NanumGothic",
       "Helvetica Neue", Arial, sans-serif; font-size: 9.5pt;
       line-height: 1.45; color: #202020; }
h1 { font-size: 20pt; margin: 0 0 2pt 0; }
.subtitle { color: #555; margin: 0 0 4pt 0; }
.contact { font-size: 8.5pt; color: #444; margin-bottom: 14pt; }
h2 { font-size: 12pt; border-bottom: 1.2pt solid #333; padding-bottom: 2pt;
     margin: 14pt 0 6pt 0; }
ul { margin: 4pt 0; padding-left: 14pt; }
li { margin: 3pt 0; }
.first { background: #fff3bf; }
.muted { color: #666; font-size: 8.5pt; }
"""


def esc(s):
    return html.escape(str(s or ""))


def li_list(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def main():
    cv = yaml.safe_load((ROOT / "_data" / "cv.yml").read_text(encoding="utf-8"))
    pubs = yaml.safe_load((ROOT / "_data" / "publications.yml").read_text(encoding="utf-8")) or []

    def load_json(name):
        try:
            return json.loads((ROOT / "data" / name).read_text(encoding="utf-8")).get("items", [])
        except (FileNotFoundError, ValueError):
            return []

    patents = load_json("patents.json")
    projects = load_json("projects.json")

    pub_lines = []
    for p in pubs:
        authors = esc(p.get("authors"))
        line = (f"{authors}, " if authors else "") + f"“{esc(p['title'])},”"
        if p.get("venue"):
            line += f" <em>{esc(p['venue'])}</em>,"
        line += f" {esc(p.get('date_label', p.get('year', '')))}."
        if p.get("doi"):
            line += f" <span class='muted'>doi:{esc(p['doi'])}</span>"
        if p.get("highlight"):
            line = f"<span class='first'>{line}</span>"
        pub_lines.append(line)

    patent_lines = []
    for p in patents:
        nums = " / ".join(x for x in [
            f"Application {esc(p['applicationNumber'])}" if p.get("applicationNumber") else "",
            f"Registration {esc(p['registrationNumber'])}" if p.get("registrationNumber") else "",
        ] if x)
        patent_lines.append(
            f"{esc(p.get('title'))} <span class='muted'>({nums}"
            + (f", {esc(p['status'])}" if p.get("status") else "")
            + (f", {esc(p['year'])}" if p.get("year") else "") + ")</span>")

    project_lines = []
    for p in projects:
        meta = " · ".join(esc(x) for x in [p.get("period"), p.get("ministry"), p.get("role")] if x)
        project_lines.append(f"{esc(p.get('title'))}"
                             + (f" <span class='muted'>({meta})</span>" if meta else ""))

    sections = [
        ("Education", li_list(map(esc, cv.get("education", [])))),
        ("Experience", li_list(map(esc, cv.get("experience", [])))),
        ("Research Interests", li_list(map(esc, cv.get("interests", [])))),
        ("Skills", li_list(map(esc, cv.get("skills", [])))),
        (f"Publications ({len(pub_lines)})", li_list(pub_lines)),
    ]
    if patent_lines:
        sections.append((f"Patents ({len(patent_lines)})", li_list(patent_lines)))
    if project_lines:
        sections.append((f"Funded Projects ({len(project_lines)})", li_list(project_lines)))

    body = "".join(f"<h2>{esc(t) if '<' not in t else t}</h2>{c}" for t, c in sections)
    doc = f"""<!doctype html><html><head><meta charset="utf-8">
<style>{CSS}</style></head><body>
<h1>{esc(cv['name'])}</h1>
<p class="subtitle">{esc(cv['title'])}</p>
<p class="contact">{esc(cv['email'])} · ORCID {esc(cv['orcid'])} ·
{esc(cv['website'])} · {esc(cv['github'])}<br>
<span class="muted">Generated {date.today().isoformat()} — first-author papers highlighted</span></p>
<p>{esc(cv.get('summary', ''))}</p>
{body}
</body></html>"""

    from weasyprint import HTML
    HTML(string=doc, base_url=str(ROOT)).write_pdf(str(OUT))
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
