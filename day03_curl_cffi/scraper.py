"""
Day 3 — Cloudflare Bypass with curl_cffi
Target: scrapingcourse.com/cloudflare-challenge
Stack: curl_cffi + BeautifulSoup4

This site is specifically designed to demonstrate Cloudflare TLS bypass.
httpx gets blocked. curl_cffi (impersonating Chrome) gets through.

What curl_cffi does:
  - Impersonates Chrome's exact TLS fingerprint
  - Bypasses standard Cloudflare protection

What curl_cffi does NOT do:
  - Execute JavaScript (Playwright does that — Day 8)
  - Bypass Cloudflare Bot Management (Trustpilot, G2 use this)
  - Bypass CAPTCHAs

Run:
  python scraper.py
"""

import json
import csv
import time
import random
from dataclasses import dataclass, asdict
from typing import Optional, Callable

from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup


# ── Config ────────────────────────────────────────────────────────────────────

URL       = "https://www.scrapingcourse.com/cloudflare-challenge"
DELAY_MIN = 1.0
DELAY_MAX = 2.5

# Try newest Chrome version first — Cloudflare blocklists old ones over time
IMPERSONATE_VERSIONS = ["chrome131", "chrome124", "chrome120", "chrome110"]

# Match Chrome's real headers — Cloudflare checks these too after TLS passes
HEADERS = {
    "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
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


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class Product:
    name:  str
    price: str
    image: str


# ── Scraper ───────────────────────────────────────────────────────────────────

def _find_working_session(log: Callable = print) -> Optional[cffi_requests.Session]:
    """
    Try Chrome versions newest-first. Return the first session that gets 200.
    If all fail — the site has stronger protection than TLS fingerprinting.
    """
    for version in IMPERSONATE_VERSIONS:
        log(f"Trying impersonate={version}...")
        try:
            session = cffi_requests.Session(impersonate=version)
            resp    = session.get(URL, headers=HEADERS, timeout=15)
            log(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                log(f"  ✅ {version} works!")
                return session
            else:
                log(f"  ❌ {version} blocked ({resp.status_code})")
        except Exception as e:
            log(f"  ❌ {version} error: {e}")
    return None


def _parse_products(html: str) -> list[Product]:
    """
    Parse products from scrapingcourse.com/cloudflare-challenge.
    The page lists products with name, price, and image.
    """
    soup     = BeautifulSoup(html, "html.parser")
    products = []

    # Products are in <li> cards — each has an image, name, and price
    cards = soup.select("li.product, div.product, article")
    if not cards:
        # Fallback: any element with a price-looking child
        cards = soup.find_all(lambda tag: tag.find(string=lambda t: t and "$" in t))

    for card in cards:
        # Name
        name_el = card.find(["h2", "h3", "h4", "a"], class_=lambda c: c and "name" in c.lower() if c else False)
        if not name_el:
            name_el = card.find(["h2", "h3", "h4"])
        name = name_el.get_text(strip=True) if name_el else ""

        # Price
        price_el = card.find(class_=lambda c: c and "price" in c.lower() if c else False)
        if not price_el:
            price_el = card.find(string=lambda t: t and "$" in t)
        price = price_el.get_text(strip=True) if hasattr(price_el, "get_text") else (str(price_el).strip() if price_el else "")

        # Image
        img    = card.find("img")
        image  = img.get("src", "") if img else ""

        if name or price:
            products.append(Product(name=name, price=price, image=image))

    return products


def scrape(
    output_json:       Optional[str]  = "products.json",
    output_csv:        Optional[str]  = "products.csv",
    progress_callback: Optional[Callable] = None,
    log:               Callable       = print,
) -> list[dict]:
    """
    Scrape scrapingcourse.com/cloudflare-challenge.
    Demonstrates: httpx fails (TLS fingerprint) — curl_cffi succeeds.
    """
    log("=" * 50)
    log("Day 3 — curl_cffi TLS Fingerprint Demo")
    log("=" * 50)

    # ── Step 1: Show that httpx fails ────────────────────────────────────────
    log("\n[1/3] Testing httpx (standard Python HTTP)...")
    try:
        import httpx
        resp = httpx.get(URL, timeout=10)
        log(f"  httpx status: {resp.status_code}")
        if resp.status_code == 403:
            log("  ❌ httpx blocked — TLS fingerprint detected as bot")
        else:
            log(f"  httpx status: {resp.status_code}")
    except Exception as e:
        log(f"  httpx error: {e}")

    # ── Step 2: Try curl_cffi ─────────────────────────────────────────────────
    log("\n[2/3] Testing curl_cffi (Chrome TLS impersonation)...")
    time.sleep(random.uniform(1.0, 1.5))

    session = _find_working_session(log)

    if session is None:
        log("\n❌ curl_cffi also blocked.")
        log("   This site may have upgraded beyond standard TLS checking.")
        log("   Solution: Playwright (Day 8) — runs a real browser.")
        return []

    # ── Step 3: Parse the page ────────────────────────────────────────────────
    log("\n[3/3] Parsing products from the page...")
    resp     = session.get(URL, headers=HEADERS, timeout=15)
    products = _parse_products(resp.text)

    if progress_callback:
        progress_callback(1, 1, f"Found {len(products)} products")

    log(f"\n✅ Done — {len(products)} products scraped")

    dicts = [asdict(p) for p in products]

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
    scrape()
