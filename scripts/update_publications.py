#!/usr/bin/env python3
"""Append newly indexed publications to _data/publications.yml.

Queries OpenAlex for works by Hwanhee Cho (KRRI) and appends any paper that is
not already in the data file. Existing entries are never modified, so manual
edits (titles, venues, months, highlight flags) are preserved. Entries are
matched by DOI when available, otherwise by OpenAlex work id.

Run manually:  python3 scripts/update_publications.py
Run by CI:     .github/workflows/update-publications.yml (weekly)

If a new paper does not appear within a few weeks of publication it is usually
because OpenAlex has not indexed it yet, or indexed it under a stray author
profile. In that case simply add the entry to _data/publications.yml by hand.
"""

import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

# OpenAlex author profiles for Hwanhee Cho.
# A5043946628 is the main profile linked to ORCID 0000-0002-4966-0099.
# A5015337744 is a stray "H. Cho" profile that holds a few of his papers mixed
# with papers from unrelated researchers; the name filter + exclude list below
# keep the unrelated ones out.
AUTHOR_IDS = ["A5043946628", "A5015337744"]

# OpenAlex work ids that match the name filter but belong to other people.
EXCLUDE_WORKS = {
    "W7117463295",  # Building Damage Assessment Captioning (remote sensing, UNIST)
}

NAME_RE = re.compile(r"^hwan[\s-]?hee\s+cho$", re.I)
MONTHS = ["", "Jan.", "Feb.", "Mar.", "Apr.", "May", "Jun.",
          "Jul.", "Aug.", "Sep.", "Oct.", "Nov.", "Dec."]

DATA_FILE = Path(__file__).resolve().parent.parent / "_data" / "publications.yml"

HEADER = (
    "# Publication list rendered on the homepage (index.md).\n"
    "# Updated automatically by scripts/update_publications.py (weekly GitHub Action),\n"
    "# which appends newly indexed papers from OpenAlex (matched by ORCID profile).\n"
    "# Existing entries are matched by DOI / openalex id, so manual edits here\n"
    "# (titles, venues, months, highlight flags) are preserved.\n"
)


def fetch_works():
    works = []
    for aid in AUTHOR_IDS:
        cursor = "*"
        while cursor:
            params = urllib.parse.urlencode({
                "filter": f"authorships.author.id:{aid}",
                "per-page": 50,
                "cursor": cursor,
                "select": "id,doi,title,publication_date,primary_location,authorships,type",
                "mailto": "hcho88@krri.re.kr",
            })
            req = urllib.request.Request(
                f"https://api.openalex.org/works?{params}",
                headers={"User-Agent": "wheee88.github.io publication updater"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.load(resp)
            works.extend(data["results"])
            cursor = data["meta"].get("next_cursor")
    return works


def is_me(authorship):
    raw = (authorship.get("raw_author_name") or "").replace("‐", "-")
    display = authorship["author"]["display_name"].replace("‐", "-")
    return bool(NAME_RE.match(raw) or NAME_RE.match(display))


def initials(name):
    parts = name.replace("‐", "-").strip().split()
    return f"{parts[0][0]}. {parts[-1]}"


def to_entry(work):
    doi = (work.get("doi") or "").replace("https://doi.org/", "") or None
    year = int(work["publication_date"][:4])
    month = 0 if work["publication_date"].endswith("-01-01") else int(work["publication_date"][5:7])
    source = (work.get("primary_location") or {}).get("source") or {}
    authorships = work.get("authorships") or []
    entry = {
        "openalex": work["id"].replace("https://openalex.org/", ""),
        "title": (work.get("title") or "").replace("‐", "-"),
        "authors": ", ".join(initials(a["author"]["display_name"]) for a in authorships),
        "venue": source.get("display_name") or "",
        "year": year,
        "month": month,
        "date_label": (MONTHS[month] + " " if month else "") + str(year),
        "highlight": bool(authorships and is_me(authorships[0])),
    }
    if doi:
        entry["doi"] = doi
        entry["url"] = "https://doi.org/" + doi
    return entry


def main():
    existing = yaml.safe_load(DATA_FILE.read_text()) or []
    known = set()
    for e in existing:
        if e.get("doi"):
            known.add(e["doi"].lower())
        if e.get("openalex"):
            known.add(e["openalex"])

    added = []
    for work in fetch_works():
        wid = work["id"].replace("https://openalex.org/", "")
        doi = (work.get("doi") or "").replace("https://doi.org/", "").lower()
        if wid in EXCLUDE_WORKS or wid in known or (doi and doi in known):
            continue
        if not work.get("title"):
            continue
        if not any(is_me(a) for a in work.get("authorships") or []):
            continue
        entry = to_entry(work)
        added.append(entry)
        known.add(wid)
        if doi:
            known.add(doi)

    if not added:
        print("No new publications found.")
        return

    merged = existing + added
    merged.sort(key=lambda e: (e.get("year", 0), e.get("month", 0)), reverse=True)
    with DATA_FILE.open("w") as f:
        f.write(HEADER)
        yaml.dump(merged, f, sort_keys=False, allow_unicode=True, width=1000)

    print(f"Added {len(added)} new publication(s):")
    for e in added:
        print(f"  - [{e['date_label']}] {e['title']}")


if __name__ == "__main__":
    sys.exit(main())
