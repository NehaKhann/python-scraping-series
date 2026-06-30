"""
Subdomain experiment: does sa.linkedin.com / pk.linkedin.com return regional jobs?

LinkedIn has country-specific subdomains (uk.linkedin.com, in.linkedin.com etc.)
The hypothesis: hitting sa.linkedin.com instead of www.linkedin.com might route
the guest API to a regional data source.

Run this on your local machine (not in a cloud sandbox):
    pip install httpx beautifulsoup4
    python test_subdomain.py

What to look for:
- If job URLs show sa.linkedin.com  → it worked, regional data returned
- If job URLs still show uk.linkedin.com → subdomain makes no difference
- If status is 404/302  → subdomain doesn't support the guest API
"""

import httpx
import time
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

ENDPOINT = "/jobs-guest/jobs/api/seeMoreJobPostings/search"

TESTS = [
    # ── Saudi Arabia ──────────────────────────────────────────────────────────
    {
        "label":    "CONTROL  — www.linkedin.com → Saudi Arabia",
        "base":     "https://www.linkedin.com",
        "params":   {"keywords": "Software Engineer", "location": "Saudi Arabia",
                     "geoId": "101004847", "start": 0},
        "country":  "saudi",
    },
    {
        "label":    "SUBDOMAIN — sa.linkedin.com → Saudi Arabia",
        "base":     "https://sa.linkedin.com",
        "params":   {"keywords": "Software Engineer", "location": "Saudi Arabia",
                     "geoId": "101004847", "start": 0},
        "country":  "saudi",
    },
    # ── Pakistan ──────────────────────────────────────────────────────────────
    {
        "label":    "CONTROL  — www.linkedin.com → Pakistan",
        "base":     "https://www.linkedin.com",
        "params":   {"keywords": "Software Engineer", "location": "Pakistan",
                     "geoId": "100600279", "start": 0},
        "country":  "pakistan",
    },
    {
        "label":    "SUBDOMAIN — pk.linkedin.com → Pakistan",
        "base":     "https://pk.linkedin.com",
        "params":   {"keywords": "Software Engineer", "location": "Pakistan",
                     "geoId": "100600279", "start": 0},
        "country":  "pakistan",
    },
]

REGIONAL_KEYWORDS = {
    "saudi":   ["saudi", "riyadh", "jeddah", "dammam", "khobar", "sa.linkedin"],
    "pakistan": ["pakistan", "karachi", "lahore", "islamabad", "rawalpindi", "pk.linkedin"],
}


def parse_jobs(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for card in soup.find_all("div", class_="base-card"):
        title_el    = card.find("h3", class_="base-search-card__title")
        company_el  = card.find("h4", class_="base-search-card__subtitle")
        loc_el      = card.find("span", class_="job-search-card__location")
        link_el     = card.find("a", class_="base-card__full-link")
        jobs.append({
            "title":    title_el.get_text(strip=True)   if title_el   else "—",
            "company":  company_el.get_text(strip=True) if company_el else "—",
            "location": loc_el.get_text(strip=True)     if loc_el     else "—",
            "url":      link_el["href"].split("?")[0]   if link_el    else "—",
        })
    return jobs


def url_domain(url: str) -> str:
    try:
        return url.split("/")[2]
    except Exception:
        return "—"


def run():
    print("\n" + "=" * 70)
    print("LinkedIn Subdomain Experiment")
    print("Testing: does sa.linkedin.com / pk.linkedin.com return regional jobs?")
    print("=" * 70)

    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=15) as client:
        for i, test in enumerate(TESTS):
            if i > 0:
                time.sleep(3)   # polite delay between tests

            url = test["base"] + ENDPOINT
            print(f"\n── {test['label']}")
            print(f"   URL: {url}")

            try:
                resp = client.get(url, params=test["params"])
            except Exception as e:
                print(f"   ❌ Connection error: {e}")
                continue

            print(f"   Status: {resp.status_code}  |  Final URL: {resp.url}")

            if resp.status_code != 200:
                print(f"   ❌ Non-200 — response: {resp.text[:200]}")
                continue

            jobs = parse_jobs(resp.text)

            if not jobs:
                print("   ⚠️  No job cards parsed")
                print(f"   Raw HTML snippet: {resp.text[:300]}")
                continue

            # Count how many jobs are from the expected vs wrong region
            regional_kws = REGIONAL_KEYWORDS[test["country"]]
            regional  = [j for j in jobs if
                         any(kw in j["location"].lower() or kw in j["url"].lower()
                             for kw in regional_kws)]
            uk_jobs   = [j for j in jobs if "united kingdom" in j["location"].lower()
                         or "uk.linkedin" in j["url"].lower()]

            print(f"   Jobs: {len(jobs)} total | ✅ Regional: {len(regional)} | ❌ UK jobs: {len(uk_jobs)}")

            # Print first 5 jobs
            print(f"\n   {'Title':<38} {'Location':<32} {'URL domain'}")
            print("   " + "-" * 100)
            for j in jobs[:5]:
                domain = url_domain(j["url"])
                print(f"   {j['title'][:37]:<38} {j['location'][:31]:<32} {domain}")

            # Verdict
            if len(regional) > len(uk_jobs):
                print(f"\n   🎉 RESULT: SUBDOMAIN WORKS — {len(regional)}/{len(jobs)} jobs are from the target region")
            elif len(regional) > 0:
                print(f"\n   ⚠️  RESULT: PARTIAL — {len(regional)}/{len(jobs)} regional jobs mixed with {len(uk_jobs)} UK jobs")
            else:
                print(f"\n   ❌ RESULT: NO DIFFERENCE — still returning UK/non-regional jobs")

    print("\n" + "=" * 70)
    print("SUMMARY: compare CONTROL vs SUBDOMAIN rows for the same country.")
    print("If regional count is higher in the SUBDOMAIN row → it works.")
    print("If both return UK jobs → subdomain makes no difference.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run()
