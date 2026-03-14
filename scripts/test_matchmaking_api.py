"""
Backend test script for the full AI matchmaking flow.

Assumes you have loaded NGOs via: python scripts/import_ngos_book2.py
Donors are not stored in the DB for matchmaking – we send donor name + strategy
in the request only (no donor rows to delete).

Covers:
- GET /api/ngos, GET /api/donors (same DB, different tables)
- POST /api/matchmaking/generate – single-donor match with real-sounding donors, normalized scores
- POST /api/matchmaking/export – CSV download
- Validation (400 when required fields missing)

Run with backend up:
  uvicorn backend.main_api:app --reload
  python scripts/test_matchmaking_api.py

Set BASE_URL if your API is elsewhere (e.g. export BASE_URL=http://localhost:8000).
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


REAL_SOUNDING_DONORS = [
    {
        "donor_name": "Captain Vassilis & Carmen Constantakopoulos Foundation",
        "donor_strategy": "Education, Social care, Economic Development, Environment / Climate Change, Culture",
    },
    {
        "donor_name": "McKinsey & Company",
        "donor_strategy": "Diversity - Equality - Inclusion, Education, Social care, Environment / Climate",
    },
]


def url(path: str) -> str:
    return f"{BASE_URL.rstrip('/')}{path}"


def section(name: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {name}")
    print("=" * 60)


def test_list_ngos():
    """GET /api/ngos – list all NGOs (loaded by you via book2 script)."""
    section("1. List NGOs")
    r = requests.get(url("/api/ngos"), timeout=10)
    r.raise_for_status()
    data = r.json()
    print(f"   Total NGOs in DB: {len(data)}")
    if data:
        print(f"   First NGO example: id={data[0].get('id')}, name={data[0].get('name')}")
    if len(data) == 0:
        print("   (Load NGOs first: python scripts/import_ngos_book2.py)")
    return data


def test_list_donors():
    """GET /api/donors – list donors (same DB, donors table)."""
    section("2. List donors (same database, different table)")
    r = requests.get(url("/api/donors"), timeout=10)
    r.raise_for_status()
    data = r.json()
    print(f"   Total donors in DB: {len(data)}")
    return data


def test_matchmaking_generate():
    """POST /api/matchmaking/generate – real-sounding donors, normalized scores."""
    section("3. Matchmaking generate (mock donors, your NGOs)")
    for donor in REAL_SOUNDING_DONORS:
        payload = {
            **donor,
            "match_threshold_percent": 50.0,
        }
        r = requests.post(url("/api/matchmaking/generate"), json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        print(f"   Donor: {data.get('donor_name')}")
        print(f"   Total matched NGOs: {data.get('total_matched')}")
        matches = data.get("matches") or []
        for i, m in enumerate(matches[:5], 1):
            raw = m.get("raw_score") or 0
            print(f"   {i}. {m.get('ngo_name')} – AI Match: {m.get('ai_match_score_percent')}% (raw: {raw:.3f})")
        if len(matches) > 5:
            print(f"   ... and {len(matches) - 5} more")
        if matches:
            pcts = [m["ai_match_score_percent"] for m in matches]
            assert max(pcts) <= 100 and min(pcts) >= 0, "Normalized scores should be 0–100"
            assert pcts == sorted(pcts, reverse=True), "Scores should be descending"
        print("")
    print("   OK: normalized scores and order verified for all donors")


def test_matchmaking_export():
    """POST /api/matchmaking/export – writes CSV to data/export_file/, returns path."""
    section("4. Matchmaking export (CSV to data/export_file/)")
    donor = REAL_SOUNDING_DONORS[0]
    r = requests.post(url("/api/matchmaking/export"), json={**donor}, timeout=60)
    r.raise_for_status()
    data = r.json()
    assert "saved_to" in data and "path_absolute" in data, "Expected saved_to and path_absolute in response"
    print(f"   Donor: {donor['donor_name']}")
    print(f"   saved_to: {data['saved_to']}")
    print(f"   total_matched: {data.get('total_matched')}")
    export_path = Path(data["path_absolute"])
    assert export_path.exists(), f"CSV file should exist at {export_path}"
    content = export_path.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    # CSV format: line 0 = Donor,<name>; line 1 = header (#, NGO name, ...); then data
    assert len(lines) >= 2 and "NGO name" in content, "Expected donor row and header row (with 'NGO name') in saved CSV"
    print("   First 3 lines of saved file:")
    for line in lines[:3]:
        print(f"      {line[:80]}{'...' if len(line) > 80 else ''}")
    print("   OK: CSV written to app export folder")


def test_validation():
    """Missing donor name or strategy should return 400."""
    section("5. Validation (missing fields)")
    r = requests.post(
        url("/api/matchmaking/generate"),
        json={"donor_name": "", "donor_strategy": "Education"},
        timeout=10,
    )
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print("   Missing donor_name -> 400 OK")
    r2 = requests.post(
        url("/api/matchmaking/generate"),
        json={"donor_name": "Acme", "donor_strategy": ""},
        timeout=10,
    )
    assert r2.status_code == 400, f"Expected 400, got {r2.status_code}"
    print("   Missing donor_strategy -> 400 OK")


def main():
    print("Matchmaking API tests (mock donors, NGOs from book2)")
    print(f"BASE_URL = {BASE_URL}")

    try:
        test_list_ngos()
        test_list_donors()
        test_matchmaking_generate()
        test_matchmaking_export()
        test_validation()
    except requests.exceptions.ConnectionError as e:
        print(f"\nConnection error: {e}")
        print("Make sure the backend is running: uvicorn backend.main_api:app --reload")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\nHTTP error: {e}")
        if e.response is not None:
            print(e.response.text)
        sys.exit(1)
    except AssertionError as e:
        print(f"\nAssertion failed: {e}")
        sys.exit(1)

    section("Done")
    print("  All matchmaking API tests passed.\n")

 
if __name__ == "__main__":
    main()
