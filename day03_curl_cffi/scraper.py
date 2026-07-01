"""
Day 3 — G2 Review Scraper
Stack: curl_cffi (browser impersonation) + BeautifulSoup4

The problem this solves:
  httpx / requests → 403 Forbidden (TLS fingerprint detected as bot)
  curl_cffi        → 200 OK (impersonates Chrome's exact TLS fingerprint)

Originally targeted Trustpilot — but Trustpilot uses Cloudflare Bot Management,
which goes beyond TLS fingerprinting into JS challenges and behaviour analysis.
curl_cffi can't solve that. Switched to G2.com which uses standard Cloudflare.

What curl_cffi does NOT do:
  - Execute JavaScript (that's Playwright, Day 8)
  - Bypass Cloudflare Bot Management (Trustpilot, some banking sites)
  - Bypass CAPTCHA challenges

Run:
  python scraper.py --product notion --pages 3
  python scraper.py --product slack --pages 1
  python scraper.py --product figma --pages 2
"""

import argparse
import json
import csv
import time
import random
import re
from dataclasses import dataclass, asdict
from typing import Optional, Callable
from datetime import datetime

from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup


# ── Config ────────────────────────────────────────────────────────────────────

BASE_URL  = "https://www.g2.com/products/{product}/reviews"
PAGE_URL  = "https://www.g2.com/products/{product}/reviews?page={page}"
HOME_URL  = "https://www.g2.com"
DELAY_MIN = 1.5
DELAY_MAX = 3.0

# Try newest first — Cloudflare blocklists old fingerprints over time.
IMPERSONATE_VERSIONS = ["chrome131", "chrome124", "chrome120", "chrome110"]

HEADERS = {
    "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language":           "en-US,en;q=0.9",
    "Cache-Control":             "max-age=0",
    "Sec-Ch-Ua":                 '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile":          "?0",
    "Sec-Ch-Ua-Platform":        '"Windows"',
    "Sec-Fetch-Dest":            "document",
    "Sec-Fetch-Mode":            "navigate",
    "Sec-Fetch-Site":            "none",
    "Sec-Fetch-User":            "?1",
    "Upgrade-Insecure-Requests": "1",
}

HEADERS_NAV = {
    **HEADERS,
    "Referer":        "https://www.g2.com/",
    "Sec-Fetch-Site": "same-origin",
}


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class Review:
    reviewer: str
    rating:   int     # 1–5
    title:    str
    body:     str
    date:     str     # YYYY-MM-DD
    verified: bool
    product:  str


# ── Parsing ───────────────────────────────────────────────────────────────────

def _parse_reviews(soup: BeautifulSoup, product: str) -> list[Review]:
    """
    G2 uses Schema.org itemprop markup on review cards — standard HTML,
    no JavaScript needed to read. Great for scraping.

    Each review card looks like:
      <div itemprop="review">
        <span itemprop="author">John D.</span>
        <meta itemprop="ratingValue" content="5">
        <span itemprop="name">Great product</span>
        <span itemprop="reviewBody">Love the integrations...</span>
        <time itemprop="datePublished" datetime="2024-10-15">
        <span class="verified">Verified User</span>
      </div>
    """
    reviews = []

    cards = soup.find_all(attrs={"itemprop": "review"})
    if not cards:
        # Fallback: look for G2's article containers
        cards = soup.find_all("div", attrs={"data-testid": "review"})
    if not cards:
        cards = soup.select("div[class*='paper'][class*='review'], article")

    for card in cards:
        # Author
        author_el = card.find(attrs={"itemprop": "author"})
        reviewer  = author_el.get_text(strip=True) if author_el else "Anonymous"

        # Rating — stored as a <meta> tag: <meta itemprop="ratingValue" content="5">
        rating = 0
        rating_el = card.find("meta", attrs={"itemprop": "ratingValue"})
        if rating_el:
            try:
                rating = int(float(rating_el.get("content", 0)))
            except (ValueError, TypeError):
                pass
        if not rating:
            # Fallback: count filled star elements
            filled = card.select("svg[class*='star'][class*='filled'], .star--filled, [class*='star-full']")
            rating = min(len(filled), 5)

        # Title
        title_el = card.find(attrs={"itemprop": "name"})
        title    = title_el.get_text(strip=True) if title_el else ""

        # Body
        body_el = card.find(attrs={"itemprop": "reviewBody"})
        body    = body_el.get_text(strip=True) if body_el else ""

        # Date
        date    = ""
        time_el = card.find("time", attrs={"itemprop": "datePublished"})
        if time_el:
            raw  = time_el.get("datetime", "")
            date = raw[:10] if raw else ""
        if not date:
            time_el = card.find("time")
            if time_el:
                raw  = time_el.get("datetime", "")
                date = raw[:10] if raw else ""

        # Verified
        verified_text = card.get_text(separator=" ").lower()
        verified      = "verified" in verified_text

        if reviewer != "Anonymous" or title or body:
            reviews.append(Review(
                reviewer = reviewer,
                rating   = rating,
                title    = title,
                body     = body,
                date     = date,
                verified = verified,
                product  = product,
            ))

    return reviews


def _get_total_pages(soup: BeautifulSoup) -> int:
    """Find how many review pages exist."""
    # G2 pagination: look for page number links
    page_links = soup.find_all("a", href=re.compile(r"[?&]page=(\d+)"))
    if page_links:
        pages = []
        for a in page_links:
            m = re.search(r"page=(\d+)", a["href"])
            if m:
                pages.append(int(m.group(1)))
        return max(pages) if pages else 1

    # Fallback: look for "Next" button
    if soup.find("a", string=re.compile(r"Next", re.I)):
        return 99  # unknown max, caller will stop when empty

    return 1


def scrape_page(session, product: str, page: int, log: Callable = print) -> tuple[list[Review], int]:
    url = BASE_URL.format(product=product) if page == 1 else PAGE_URL.format(product=product, page=page)
    log(f"Fetching page {page}: {url}")

    resp = session.get(url, headers=HEADERS_NAV, timeout=15)

    if resp.status_code != 200:
        log(f"  ❌ Status {resp.status_code} — skipping page {page}")
        return [], 0

    soup        = BeautifulSoup(resp.text, "html.parser")
    reviews     = _parse_reviews(soup, product)
    total_pages = _get_total_pages(soup)

    log(f"  ✅ Page {page}: {len(reviews)} reviews (total pages: {total_pages})")
    return reviews, total_pages


# ── Main scrape function ──────────────────────────────────────────────────────

def scrape(
    product:           str,
    max_pages:         int            = 3,
    output_json:       Optional[str]  = "reviews.json",
    output_csv:        Optional[str]  = "reviews.csv",
    progress_callback: Optional[Callable] = None,
    log:               Callable       = print,
) -> list[dict]:
    """
    Scrape G2 reviews for a product.

    Args:
        product:   G2 product slug, e.g. "notion", "slack", "figma"
        max_pages: how many review pages to fetch (~10 reviews each)
    """
    log(f"Starting G2 scrape: {product}")

    # ── Find a working impersonate version ────────────────────────────────────
    # We visit the G2 homepage first (warm-up) to get the Cloudflare session
    # cookie. Without this, even the right TLS fingerprint can get a 403
    # because Cloudflare sees no prior session for this IP.
    session = None
    for version in IMPERSONATE_VERSIONS:
        log(f"Trying impersonate={version}...")
        try:
            s       = cffi_requests.Session(impersonate=version)
            warmup  = s.get(HOME_URL, headers=HEADERS, timeout=10)
            log(f"  Warm-up (g2.com): {warmup.status_code}")
            if warmup.status_code == 200:
                session = s
                log(f"  ✅ {version} works")
                time.sleep(random.uniform(1.0, 2.0))
                break
            else:
                log(f"  ❌ {version} blocked ({warmup.status_code})")
        except Exception as e:
            log(f"  ❌ {version} error: {e}")

    if session is None:
        log("❌ All versions blocked. Try upgrading curl_cffi: pip install --upgrade curl_cffi")
        return []

    # ── Scrape pages ──────────────────────────────────────────────────────────
    all_reviews: list[Review] = []

    reviews, total_pages = scrape_page(session, product, 1, log)
    all_reviews.extend(reviews)

    if progress_callback:
        progress_callback(1, min(max_pages, total_pages), "Scraped page 1")

    pages_to_scrape = min(max_pages, total_pages)

    for page in range(2, pages_to_scrape + 1):
        if not reviews:
            log("No reviews on previous page — stopping early")
            break
        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        log(f"Waiting {delay:.1f}s...")
        time.sleep(delay)
        reviews, _ = scrape_page(session, product, page, log)
        all_reviews.extend(reviews)
        if progress_callback:
            progress_callback(page, pages_to_scrape, f"Scraped page {page}/{pages_to_scrape}")

    log(f"\n✅ Done — {len(all_reviews)} reviews for {product}")

    dicts = [asdict(r) for r in all_reviews]

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(dicts, f, indent=2, ensure_ascii=False)
        log(f"Saved → {output_json}")

    if output_csv and dicts:
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=dicts[0].keys())
            writer.writeheader()
            writer.writerows(dicts)
        log(f"Saved → {output_csv}")

    return dicts


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape G2 reviews")
    parser.add_argument("--product", default="notion",  help="G2 product slug (e.g. notion, slack, figma)")
    parser.add_argument("--pages",   type=int, default=3, help="Max pages to scrape")
    args = parser.parse_args()

    scrape(
        product     = args.product,
        max_pages   = args.pages,
        output_json = f"reviews_{args.product}.json",
        output_csv  = f"reviews_{args.product}.csv",
    )
