#!/usr/bin/env python3
"""Fetch funded R&D projects from the NTIS open API into data/projects.json.

Searches national R&D projects for researcher "조환희" at
"한국철도기술연구원".

Requires the NTIS_API_KEY environment variable (repo secret). Get a free key
at https://www.ntis.go.kr — 개발자센터/OpenAPI에서 "국가R&D 과제검색 서비스
(대국민용)" 활용 신청 후 발급되는 인증키(apprvKey)를 시크릿으로 등록.

Behavior mirrors fetch_patents.py:
  * NTIS_API_KEY not set -> notice + exit 0 (skipped)
  * API/parse failure    -> exit 1 WITHOUT touching data/projects.json
  * success              -> rewrite data/projects.json

NOTE (first-run check): the NTIS response schema is only published in the
official manual PDF, so the tag names below are best-effort candidates. On the
first keyed run, check the workflow log — the script prints the raw XML head
when it cannot find items — and adjust FIELD candidates if needed. Same-name
researchers may also appear; curate the first JSON once.
"""

import json
import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://www.ntis.go.kr/rndopen/openApi/public_rnd_project_api"
QUERY = "조환희 한국철도기술연구원"
ORG = "한국철도기술연구원"
OUT = Path(__file__).resolve().parent.parent / "data" / "projects.json"

# Candidate tag names per logical field (checked in order).
FIELDS = {
    "title": ["KorPjtNm", "ProjectTitle", "PJT_NM", "korPjtNm", "projectTitle", "title"],
    "number": ["PjtId", "ProjectNumber", "PJT_NO", "pjtId", "projectNumber"],
    "ministry": ["MinistryNm", "MinistryName", "MNSTR_NM", "ministryName"],
    "agency": ["RsrchAgencyNm", "ResearchAgency", "PRCTG_AGCY_NM", "researchAgency", "orgName"],
    "start": ["TotalRsrchStartDt", "ResearchStartDate", "PRD_STRT_DT", "startDate"],
    "end": ["TotalRsrchEndDt", "ResearchEndDate", "PRD_END_DT", "endDate"],
    "period": ["RsrchPeriod", "ResearchPeriod", "TOT_PRD", "period"],
    "manager": ["RsrchManagerNm", "ResearchManager", "PJT_MGR_NM", "manager"],
}


def pick(node, field):
    for tag in FIELDS[field]:
        el = node.find(".//" + tag)
        if el is not None and (el.text or "").strip():
            return el.text.strip()
    return ""


def main():
    key = os.environ.get("NTIS_API_KEY", "").strip()
    if not key:
        print("NTIS_API_KEY is not set - skipping project update.")
        print("Register the key as a repository secret to enable this step (see README).")
        return 0

    params = {
        "apprvKey": key,
        "query": QUERY,
        "collection": "project",
        "startPosition": "1",
        "displayCnt": "100",
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "wheee88.github.io data updater"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8", "replace")

    root = ET.fromstring(raw)
    # NTIS wraps result rows in <HIT> (older docs) or <item>; try both.
    rows = root.findall(".//HIT") or root.findall(".//hit") or root.findall(".//item")
    if not rows:
        print("No result rows found. Raw response head (verify schema / key):")
        print(raw[:2000])
        # An empty-but-valid result set still counts as success only when the
        # response looks like a result envelope; otherwise fail loudly.
        if "TOTALHITS" not in raw and "resultCode" not in raw:
            return 1

    items = []
    for row in rows:
        agency = pick(row, "agency")
        if ORG and agency and ORG not in agency:
            continue
        start, end = pick(row, "start"), pick(row, "end")
        period = pick(row, "period") or (f"{start} – {end}" if start or end else "")
        item = {
            "title": pick(row, "title"),
            "number": pick(row, "number"),
            "period": period,
            "ministry": pick(row, "ministry"),
            "agency": agency,
        }
        manager = pick(row, "manager")
        if manager:  # role info: only include when the API provides it
            item["role"] = "PI" if "조환희" in manager else "Researcher"
        if item["title"]:
            items.append(item)

    items.sort(key=lambda x: x.get("period", ""), reverse=True)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "items": items,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(items)} project(s) to {OUT}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Project update failed, keeping existing data/projects.json: {e!r}")
        sys.exit(1)
