#!/usr/bin/env python3
"""Fetch patents from the KIPRIS Plus open API into data/patents.json.

Searches patent/utility-model filings with inventor "조환희" and keeps only
those whose applicant contains "한국철도기술연구원" (to filter out people who
share the same name).

Requires the KIPRIS_API_KEY environment variable (repo secret). Get a free key
at https://plus.kipris.or.kr — sign up, then apply for the
"특허·실용신안 정보 검색 서비스" REST API; the issued ServiceKey is the value
to store as the secret.

Behavior:
  * KIPRIS_API_KEY not set  -> print a notice and exit 0 (step skipped)
  * API/parse failure       -> exit 1 WITHOUT touching data/patents.json
  * success                 -> rewrite data/patents.json

NOTE (first-run check): field/param names below follow the published
patUtiModInfoSearchSevice/getAdvancedSearch spec, but verify the first real
response — same-name inventors or a renamed field can slip through. The raw
XML is printed to the workflow log when parsing finds no items.
"""

import json
import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

API_URL = "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getAdvancedSearch"
INVENTOR = "조환희"
APPLICANT = "한국철도기술연구원"
OUT = Path(__file__).resolve().parent.parent / "data" / "patents.json"


def call(key, page):
    params = {
        "inventor": INVENTOR,
        "applicant": APPLICANT,
        "patent": "true",
        "utility": "true",
        "numOfRows": "100",
        "pageNo": str(page),
        "ServiceKey": key,
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "wheee88.github.io data updater"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", "replace")


def text(node, *tags):
    for tag in tags:
        el = node.find(tag)
        if el is not None and (el.text or "").strip():
            return el.text.strip()
    return ""


def main():
    key = os.environ.get("KIPRIS_API_KEY", "").strip()
    if not key:
        print("KIPRIS_API_KEY is not set - skipping patent update.")
        print("Register the key as a repository secret to enable this step (see README).")
        return 0

    items = []
    page = 1
    while True:
        raw = call(key, page)
        root = ET.fromstring(raw)
        # KIPRIS wraps errors in a header; treat non-success as failure
        result_code = (root.findtext(".//resultCode") or "").strip()
        success = (root.findtext(".//successYN") or "").strip()
        if result_code not in ("", "00") or success == "N":
            print("KIPRIS returned an error header:")
            print(raw[:2000])
            return 1
        page_items = root.findall(".//item")
        if not page_items and page == 1:
            # No results at all: legitimate (no patents yet) but log the raw
            # response so a silently changed schema is noticeable.
            print("No <item> elements found. Raw response head:")
            print(raw[:2000])
        for it in page_items:
            applicant = text(it, "applicantName", "applicant")
            if APPLICANT not in applicant:
                continue
            app_no = text(it, "applicationNumber")
            app_date = text(it, "applicationDate")
            items.append({
                "title": text(it, "inventionTitle", "inventionName"),
                "applicationNumber": app_no,
                "registrationNumber": text(it, "registerNumber"),
                "status": text(it, "registerStatus"),
                "year": app_date[:4] if len(app_date) >= 4 else "",
                "applicant": applicant,
                # TODO(first run): verify this deep-link pattern still resolves
                "link": ("https://kpat.kipris.or.kr/kpat/biblioa.do?method=biblioFrame&applno="
                         + urllib.parse.quote(app_no)) if app_no else "https://www.kipris.or.kr",
            })
        if len(page_items) < 100:
            break
        page += 1
        if page > 10:  # safety stop
            break

    items.sort(key=lambda x: x.get("year", ""), reverse=True)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "items": items,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(items)} patent(s) to {OUT}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # network/parse failure: keep the old JSON
        print(f"Patent update failed, keeping existing data/patents.json: {e!r}")
        sys.exit(1)
