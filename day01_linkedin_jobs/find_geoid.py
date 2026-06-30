"""
LinkedIn GeoID Finder
─────────────────────
Finds the correct LinkedIn geoId for any country or city by querying
LinkedIn's autocomplete API — the same API their search box uses.

Usage:
    python find_geoid.py "Pakistan"
    python find_geoid.py "Karachi"
    python find_geoid.py "Riyadh"
    python find_geoid.py "Manchester"

Output:
    GeoID results for: "Pakistan"
    ─────────────────────────────
    [1] Pakistan                    → geoId: 100600279  (country)
    [2] Pakistan Ordnance Factories → geoId: 106568310  (city)
    ...

Copy the geoId you want into locations.py.
"""

import httpx
import json
import sys

AUTOCOMPLETE_URL = "https://www.linkedin.com/jobs-guest/api/typeaheadHits"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://www.linkedin.com/jobs/",
}


def find_geoid(query: str) -> list[dict]:
    """Query LinkedIn's autocomplete API to find geoIds for a location."""
    params = {
        "query":    query,
        "typeaheadType": "GEO",
        "geoTypes": "POPULATED_PLACE,ADMIN_DIVISION_2,MARKET_AREA,COUNTRY_REGION",
    }
    try:
        resp = httpx.get(AUTOCOMPLETE_URL, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Error: {e}")
        return []


def manual_instructions():
    """Print DevTools instructions as a fallback."""
    print("""
─── Manual Method (always works) ─────────────────────────────────
1. Open https://www.linkedin.com/jobs/ in Chrome
2. Type your location in the Location search box
3. Open DevTools → Network tab (F12)
4. Select a location from the dropdown suggestions
5. Look for a request to: seeMoreJobPostings/search
6. Click it → Payload tab → find "geoId" in the parameters
7. That number is your geoId
──────────────────────────────────────────────────────────────────
""")


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Enter location to search: ")

    if not query.strip():
        print("Usage: python find_geoid.py <location>")
        sys.exit(1)

    print(f'\nSearching LinkedIn for: "{query}"\n')
    results = find_geoid(query)

    if not results:
        print("No results found via API. Try the manual method:\n")
        manual_instructions()
        sys.exit(0)

    print(f"{'Name':<45} {'GeoID':<15} {'Type'}")
    print("─" * 75)
    for item in results[:10]:
        name   = item.get("displayName", item.get("text", ""))
        geo_id = item.get("id", "—")
        kind   = item.get("type", "")
        print(f"{name:<45} {str(geo_id):<15} {kind}")

    print()
    print("Copy the geoId you want into locations.py under the correct country/city.")
    print()
    manual_instructions()
