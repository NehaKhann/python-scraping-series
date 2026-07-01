"""
Day 3 — Trustpilot Review Scraper
Stack: curl_cffi (browser impersonation) + BeautifulSoup4

The problem this solves:
  httpx / requests → 403 Forbidden on Trustpilot
  curl_cffi        → 200 OK (impersonates Chrome's TLS fingerprint)

What curl_cffi does NOT do:
  - Execute JavaScript (that's Playwright, Day 8)
  - Bypass CAPTCHA challenges
  - Help with login-required pages

Run:
  python scraper.py --company apple.com --pages 3
  python scraper.py --company airbnb.com --pages 1
"""

import argparse
import json
import csv
import time
import random
from dataclasses import dataclass, asdict
from typing import Optional, Callable
from datetime import datetime

from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup


# ── Config ────────────────────────────────────────────────────────────────────

BASE_URL   = "https://www.trustpilot.com/review/{company}?page={page}"
DELAY_MIN  = 1.5
DELAY_MAX  = 3.0

# Impersonate a specific Chrome version — must be recent.
# Older versions (chrome99, chrome101) still get blocked on Cloudflare sites.
IMPERSONATE = "chrome120"


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class Review:
    reviewer:     str
    country:      str
    rating:       int           # 1–5
    title:        str
    body:         str
    date:         str           # ISO format
    verified:     bool
    helpful:      int
    company:      str


# ── Core scraper ──────────────────────────────────────────────────────────────

def scrape_page(session, company: str, page: int, log: Callable = print) -> tuple[list[Review], int]:
    """
    Fetch one page of reviews.
    Returns (reviews_list, total_pages).
    """
    url = BASE_URL.format(company=company, page=page)
    log(f"Fetching page {page}: {url}")

    resp = session.get(url, timeout=15)

    if resp.status_code != 200:
        log(f"  ❌ Status {resp.status_code} — skipping page {page}")
        return [], 0

    soup = BeautifulSoup(resp.text, "html.parser")

    # ── Strategy 1: extract from Next.js __NEXT_DATA__ JSON (preferred) ──────
    # Trustpilot is a Next.js app. For SEO, it embeds review data in JSON
    # inside a <script id="__NEXT_DATA__"> tag — no JavaScript needed to read it.
    next_tag = soup.find("script", id="__NEXT_DATA__")
    if next_tag:
        try:
            data = json.loads(next_tag.string)
            page_props = data.get("props", {}).get("pageProps", {})

            raw_reviews   = page_props.get("reviews", [])
            total_pages   = (
                page_props
                .get("filters", {})
                .get("pagination", {})
                .get("totalPages", 1)
            )

            if not raw_reviews:
                # Alternate JSON path some Trustpilot versions use
                raw_reviews = page_props.get("businessUnit", {}).get("reviews", [])

            reviews = [_parse_next_review(r, company) for r in raw_reviews]
            log(f"  ✅ Page {page}: {len(reviews)} reviews via __NEXT_DATA__ (total pages: {total_pages})")
            return reviews, total_pages

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            log(f"  ⚠️  __NEXT_DATA__ parse failed ({e}) — falling back to HTML")

    # ── Strategy 2: parse HTML directly (fallback) ────────────────────────────
    reviews, total_pages = _parse_html(soup, company)
    log(f"  ✅ Page {page}: {len(reviews)} reviews via HTML fallback (total pages: {total_pages})")
    return reviews, total_pages


def _parse_next_review(raw: dict, company: str) -> Review:
    """Parse one review from the __NEXT_DATA__ JSON blob."""
    consumer   = raw.get("consumer", {})
    dates      = raw.get("dates", {})
    labels     = raw.get("labels", {})
    verification = labels.get("verification", {})

    # Date — ISO string from Trustpilot, trim to date only
    raw_date = dates.get("publishedDate", "")
    try:
        date = datetime.fromisoformat(raw_date.replace("Z", "+00:00")).date().isoformat()
    except Exception:
        date = raw_date[:10] if raw_date else ""

    return Review(
        reviewer  = consumer.get("displayName", "Anonymous"),
        country   = consumer.get("countryCode", ""),
        rating    = int(raw.get("stars", 0)),
        title     = raw.get("title", ""),
        body      = raw.get("text", ""),
        date      = date,
        verified  = verification.get("verificationLevel", "") in ("verified", "stripe_verified"),
        helpful   = raw.get("likes", 0),
        company   = company,
    )


def _parse_html(soup: BeautifulSoup, company: str) -> tuple[list[Review], int]:
    """
    Fallback: parse review cards directly from HTML.
    Trustpilot's CSS classes are obfuscated (hashed), so we use
    structural selectors instead.
    """
    reviews = []

    # Each review is in an <article> with a data attribute
    cards = soup.find_all("article", attrs={"data-service-review-card-paper": True})
    if not cards:
        # Try alternate container
        cards = soup.select("article[class*='reviewCard']") or soup.find_all("article")

    for card in cards:
        # Rating — look for <img alt="Rated X out of 5 stars">
        rating = 0
        img = card.find("img", alt=lambda a: a and "out of 5 stars" in a)
        if img:
            try:
                rating = int(img["alt"].split()[1])
            except Exception:
                pass

        # Stars from data attribute if available
        star_div = card.find(attrs={"data-service-review-rating": True})
        if star_div:
            try:
                rating = int(star_div["data-service-review-rating"])
            except Exception:
                pass

        # Reviewer name
        reviewer = ""
        name_el = card.find(attrs={"data-consumer-name-typography": True})
        if name_el:
            reviewer = name_el.get_text(strip=True)

        # Review title
        title = ""
        title_el = card.find(attrs={"data-service-review-title-typography": True})
        if title_el:
            title = title_el.get_text(strip=True)

        # Review body
        body = ""
        body_el = card.find(attrs={"data-service-review-text-typography": True})
        if body_el:
            body = body_el.get_text(strip=True)

        # Date
        date = ""
        time_el = card.find("time")
        if time_el:
            raw_date = time_el.get("datetime", "")
            date = raw_date[:10] if raw_date else ""

        # Verified
        verified = bool(card.find(string=lambda t: t and "verified" in t.lower()))

        if reviewer or title or body:
            reviews.append(Review(
                reviewer = reviewer or "Anonymous",
                country  = "",
                rating   = rating,
                title    = title,
                body     = body,
                date     = date,
                verified = verified,
                helpful  = 0,
                company  = company,
            ))

    # Total pages — look for pagination
    total_pages = 1
    pagination = soup.find(attrs={"data-pagination-button-last-arrow": True})
    if not pagination:
        # Try href pattern: ?page=N
        import re
        last_page_links = soup.find_all("a", href=re.compile(r"[?&]page=(\d+)"))
        if last_page_links:
            pages = []
            for a in last_page_links:
                m = re.search(r"page=(\d+)", a["href"])
                if m:
                    pages.append(int(m.group(1)))
            total_pages = max(pages) if pages else 1

    return reviews, total_pages


# ── Main scrape function ──────────────────────────────────────────────────────

def scrape(
    company:           str,
    max_pages:         int   = 3,
    output_json:       str   = "reviews.json",
    output_csv:        str   = "reviews.csv",
    progress_callback: Optional[Callable] = None,
    log:               Callable = print,
) -> list[dict]:
    """
    Scrape reviews for a company from Trustpilot.

    Args:
        company:    e.g. "apple.com", "airbnb.com"
        max_pages:  number of pages to scrape (≈10 reviews per page)
        ...
    """
    log(f"Starting Trustpilot scrape: {company}")
    log(f"Impersonating: {IMPERSONATE} (bypasses TLS fingerprint detection)")

    session = cffi_requests.Session(impersonate=IMPERSONATE)
    all_reviews: list[Review] = []

    # Scrape page 1 first to get total_pages
    reviews, total_pages = scrape_page(session, company, 1, log)
    all_reviews.extend(reviews)

    if progress_callback:
        progress_callback(1, min(max_pages, total_pages), f"Scraped page 1")

    pages_to_scrape = min(max_pages, total_pages)

    for page in range(2, pages_to_scrape + 1):
        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        log(f"Waiting {delay:.1f}s before page {page}...")
        time.sleep(delay)

        page_reviews, _ = scrape_page(session, company, page, log)
        all_reviews.extend(page_reviews)

        if progress_callback:
            progress_callback(page, pages_to_scrape, f"Scraped page {page}/{pages_to_scrape}")

    log(f"\n✅ Done — {len(all_reviews)} reviews scraped from {company}")

    # Save output
    dicts = [asdict(r) for r in all_reviews]

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(dicts, f, indent=2, ensure_ascii=False)
        log(f"Saved → {output_json}")

    if output_csv:
        if dicts:
            with open(output_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=dicts[0].keys())
                writer.writeheader()
                writer.writerows(dicts)
            log(f"Saved → {output_csv}")

    return dicts


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Trustpilot reviews")
    parser.add_argument("--company", default="apple.com", help="Company domain (e.g. apple.com)")
    parser.add_argument("--pages",   type=int, default=3,  help="Max pages to scrape")
    args = parser.parse_args()

    scrape(
        company   = args.company,
        max_pages = args.pages,
        output_json = f"reviews_{args.company}.json",
        output_csv  = f"reviews_{args.company}.csv",
    )
