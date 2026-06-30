"""
Day 1 — LinkedIn Job Postings Scraper
Stack: httpx (async) + BeautifulSoup4
No Selenium. No browser. Uses LinkedIn's internal guest API.

Usage (terminal):
    pip install httpx beautifulsoup4
    python scraper.py --keyword "Data Engineer" --location "Remote" --max-jobs 25

Usage (from UI):
    Import scrape() and pass a progress_callback to get real-time updates.
"""

import asyncio
import json
import csv
import argparse
import random
from dataclasses import dataclass, asdict
from typing import Optional, Callable

import httpx
from bs4 import BeautifulSoup

# ─── Config ──────────────────────────────────────────────────────────────────

BASE_URL       = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
JOB_DETAIL_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
JOBS_PER_PAGE  = 25

# Safer concurrency — 2 at a time instead of 5
CONCURRENCY = 2

# Delay between each detail request (seconds) — random to look human
DETAIL_DELAY_MIN = 2.0
DETAIL_DELAY_MAX = 4.0

# Retry settings for 429 errors
MAX_RETRIES   = 3
RETRY_BACKOFF = 5  # seconds to wait before retrying after a 429

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer":         "https://www.linkedin.com/jobs/",
}

# ─── Data model ──────────────────────────────────────────────────────────────

@dataclass
class Job:
    job_id:          str = ""
    title:           str = ""
    company:         str = ""
    location:        str = ""
    date_posted:     str = ""
    job_url:         str = ""
    pay_range:       str = ""
    seniority_level: str = ""
    employment_type: str = ""
    job_function:    str = ""
    industries:      str = ""
    num_applicants:  str = ""
    description:     str = ""
    logo_url:        str = ""

# ─── Parsing helpers ─────────────────────────────────────────────────────────

def parse_job_card(card: BeautifulSoup) -> Optional[Job]:
    """Extract basic info from a single job card in the search results list."""
    try:
        job = Job()

        entity = card.find("a", class_="base-card__full-link")
        if entity and entity.get("href"):
            job.job_url = entity["href"].split("?")[0]
            parts = job.job_url.rstrip("/").split("-")
            job.job_id = parts[-1] if parts[-1].isdigit() else ""

        title_el = card.find("h3", class_="base-search-card__title")
        if title_el:
            job.title = title_el.get_text(strip=True)

        company_el = card.find("h4", class_="base-search-card__subtitle")
        if company_el:
            job.company = company_el.get_text(strip=True)

        location_el = card.find("span", class_="job-search-card__location")
        if location_el:
            job.location = location_el.get_text(strip=True)

        date_el = card.find("time")
        if date_el:
            job.date_posted = date_el.get("datetime", date_el.get_text(strip=True))

        img_el = card.find("img", class_="artdeco-entity-image")
        if img_el:
            job.logo_url = img_el.get("data-delayed-url", img_el.get("src", ""))

        return job if job.job_id else None

    except Exception as e:
        return None


def parse_job_detail(html: str, job: Job) -> Job:
    """Add full description, salary, and criteria to an existing Job object."""
    soup = BeautifulSoup(html, "html.parser")

    desc_el = soup.find("div", class_="show-more-less-html__markup")
    if desc_el:
        job.description = desc_el.get_text(separator="\n", strip=True)

    pay_el = soup.find("div", class_="compensation__salary-range")
    if pay_el:
        job.pay_range = pay_el.get_text(strip=True)

    criteria_items = soup.find_all("li", class_="description__job-criteria-item")
    for item in criteria_items:
        header_el = item.find("h3", class_="description__job-criteria-subheader")
        value_el  = item.find("span", class_="description__job-criteria-text")
        if not header_el or not value_el:
            continue
        header = header_el.get_text(strip=True).lower()
        value  = value_el.get_text(strip=True)
        if "seniority"  in header: job.seniority_level = value
        elif "employment" in header: job.employment_type = value
        elif "function"   in header: job.job_function    = value
        elif "industr"    in header: job.industries       = value

    applicants_el = soup.find("span", class_="num-applicants__caption")
    if applicants_el:
        job.num_applicants = applicants_el.get_text(strip=True)

    return job

# ─── HTTP helpers with retry ─────────────────────────────────────────────────

async def get_with_retry(
    client:  httpx.AsyncClient,
    url:     str,
    params:  dict = None,
    log:     Callable = print,
) -> Optional[httpx.Response]:
    """
    GET a URL with automatic retry on 429 (Too Many Requests).
    Waits RETRY_BACKOFF seconds before each retry.
    Returns the response or None if all retries fail.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = await client.get(url, params=params, headers=HEADERS, timeout=20)

            if resp.status_code == 429:
                wait = RETRY_BACKOFF * attempt
                log(f"⚠️ Rate limited — waiting {wait}s (retry {attempt}/{MAX_RETRIES})")
                await asyncio.sleep(wait)
                continue

            resp.raise_for_status()
            return resp

        except httpx.HTTPStatusError as e:
            log(f"❌ HTTP {e.response.status_code} error")
            return None
        except httpx.RequestError as e:
            log(f"❌ Connection error: {e}")
            return None

    log(f"❌ Gave up after {MAX_RETRIES} retries")
    return None

# ─── Core fetchers ───────────────────────────────────────────────────────────


# ─── GeoID reference table ────────────────────────────────────────────────────
# LinkedIn uses numeric geoIds internally for reliable location matching.
# Text-only location works for US/UK but is unreliable for Middle East / Asia.
# Pass geoId alongside location for best results outside the US.

GEO_IDS = {
    # Americas
    "United States":        "103644278",
    "Canada":               "101174742",
    "Brazil":               "106057199",
    # Europe
    "United Kingdom":       "101165590",
    "Germany":              "101282230",
    "France":               "105015875",
    "Netherlands":          "102890719",
    # Middle East
    "Saudi Arabia":         "101004847",
    "United Arab Emirates": "104305776",
    "Qatar":                "104813976",
    "Kuwait":               "104516386",
    "Bahrain":              "100565514",
    "Egypt":                "106139199",
    # South Asia
    "India":                "102713980",
    "Pakistan":             "100600279",
    # East Asia
    "Singapore":            "102454443",
    "Australia":            "101452733",
    # Remote
    "Remote":               "",   # no geoId needed for Remote
}


async def fetch_job_list_page(
    client:   httpx.AsyncClient,
    keyword:  str,
    location: str,
    start:    int,
    geo_id:   str = "",
    log:      Callable = print,
) -> list[Job]:
    """Fetch one page of 25 job cards from the search results."""
    params = {
        "keywords": keyword,
        "location": location,
        "start":    start,
        "f_TPR":    "",
        "position": 1,
        "pageNum":  0,
    }

    # Add geoId if provided — critical for non-US locations
    if geo_id:
        params["geoId"] = geo_id
    resp = await get_with_retry(client, BASE_URL, params=params, log=log)
    if not resp:
        return []

    soup  = BeautifulSoup(resp.text, "html.parser")
    cards = soup.find_all("div", class_="base-search-card")
    jobs  = [j for card in cards if (j := parse_job_card(card))]
    return jobs


async def fetch_job_detail(
    client:    httpx.AsyncClient,
    job:       Job,
    semaphore: asyncio.Semaphore,
    log:       Callable = print,
) -> Job:
    """
    Fetch the detail page for one job.
    - Waits for a semaphore slot (max CONCURRENCY at once)
    - Adds a random delay BEFORE the request to avoid flooding LinkedIn
    """
    async with semaphore:
        if not job.job_id:
            return job

        # Random delay between requests — looks more human, avoids 429
        delay = random.uniform(DETAIL_DELAY_MIN, DETAIL_DELAY_MAX)
        await asyncio.sleep(delay)

        url  = JOB_DETAIL_URL.format(job_id=job.job_id)
        resp = await get_with_retry(client, url, log=log)
        if resp:
            return parse_job_detail(resp.text, job)
        return job

# ─── Main scrape function ─────────────────────────────────────────────────────

async def scrape(
    keyword:           str      = "Software Engineer",
    location:          str      = "United States",
    geo_id:            str      = "",         # override auto-lookup if needed
    max_jobs:          int      = 25,
    fetch_details:     bool     = True,
    output_json:       str      = "jobs.json",
    output_csv:        str      = "jobs.csv",
    progress_callback: Callable = None,
    log:               Callable = print,
) -> list[dict]:
    """
    Main scraping function.
    Returns a list of job dicts (also saved to JSON and CSV).

    progress_callback(done, total, message) is called after each detail fetch —
    use this to update a UI progress bar.
    """
    # Auto-lookup geoId from table if not manually provided
    resolved_geo_id = geo_id or GEO_IDS.get(location, "")

    log(f"🔍 Searching: {keyword} | {location} | max {max_jobs} jobs")
    if not resolved_geo_id and location not in ("Remote", ""):
        log(f"⚠️ No geoId for '{location}' — results may be limited")

    all_jobs: list[Job] = []

    async with httpx.AsyncClient(follow_redirects=True) as client:

        # ── Step 1: collect job cards ──────────────────────────────────────
        log("📄 Collecting job listings...")
        start = 0
        while len(all_jobs) < max_jobs:
            page_jobs = await fetch_job_list_page(
                client, keyword, location, start, resolved_geo_id, log
            )
            if not page_jobs:
                break
            all_jobs.extend(page_jobs)
            start += JOBS_PER_PAGE
            await asyncio.sleep(2.0)

        all_jobs = all_jobs[:max_jobs]
        log(f"✅ Found {len(all_jobs)} jobs")

        # ── Step 2: enrich with detail pages ──────────────────────────────
        if fetch_details and all_jobs:
            log(f"📋 Fetching job details...")
            semaphore = asyncio.Semaphore(CONCURRENCY)
            total = len(all_jobs)
            done  = 0

            async def fetch_and_track(job: Job) -> Job:
                nonlocal done
                result = await fetch_job_detail(client, job, semaphore, log)
                done += 1
                if progress_callback:
                    progress_callback(done, total, f"{result.title} @ {result.company}")
                return result

            all_jobs = list(await asyncio.gather(*[fetch_and_track(j) for j in all_jobs]))
            log(f"✅ Details fetched")

    # ── Step 3: save output ───────────────────────────────────────────────
    dicts = [asdict(j) for j in all_jobs]

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(dicts, f, indent=2, ensure_ascii=False)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        if dicts:
            writer = csv.DictWriter(f, fieldnames=dicts[0].keys())
            writer.writeheader()
            writer.writerows(dicts)

    log(f"🎉 Done — {len(all_jobs)} jobs scraped")

    return dicts

# ─── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LinkedIn Job Scraper — no browser needed")
    parser.add_argument("--keyword",     default="Software Engineer")
    parser.add_argument("--location",    default="United States")
    parser.add_argument("--geo-id",      default="", help="LinkedIn geoId (auto-looked up if location is in GEO_IDS table)")
    parser.add_argument("--max-jobs",    default=25, type=int)
    parser.add_argument("--no-details",  action="store_true")
    parser.add_argument("--output-json", default="jobs.json")
    parser.add_argument("--output-csv",  default="jobs.csv")
    args = parser.parse_args()

    asyncio.run(scrape(
        keyword       = args.keyword,
        location      = args.location,
        geo_id        = args.geo_id,
        max_jobs      = args.max_jobs,
        fetch_details = not args.no_details,
        output_json   = args.output_json,
        output_csv    = args.output_csv,
    ))
