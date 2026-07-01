# Day 3 — Trustpilot Review Scraper (curl_cffi)

> **Stack:** curl_cffi · BeautifulSoup4 · Streamlit  
> **Target:** www.trustpilot.com  
> **Series:** [Python Scraping Series](../)

Scrapes Trustpilot reviews for any company using `curl_cffi` — a Python binding for
curl-impersonate that bypasses TLS fingerprint detection.

## What This Is About

Trustpilot uses Cloudflare to check the TLS fingerprint of every incoming request.
Python's `httpx` sends a fingerprint that looks like a bot → `403 Forbidden`.
`curl_cffi` sends Chrome's exact TLS fingerprint → `200 OK`.

This is **not** JavaScript rendering. It's purely about the TLS handshake.

## Files

```
day03_curl_cffi/
├── scraper.py          ← core scraper: curl_cffi session + __NEXT_DATA__ parser
├── app.py              ← Streamlit UI with filters, charts, export
└── requirements.txt
```

## Quick Start

```bash
cd day03_curl_cffi
pip install -r requirements.txt

# Terminal
python scraper.py --company apple.com --pages 3
python scraper.py --company airbnb.com --pages 1

# Streamlit UI
streamlit run app.py
```

## What Broke

**Problem 1 — httpx returns 403 on Trustpilot**  
Cloudflare identifies Python's default TLS fingerprint and blocks it.  
Fix: use `curl_cffi` with `impersonate="chrome120"` — impersonates Chrome's exact TLS cipher suite and HTTP/2 settings.

**Problem 2 — Wrong impersonate version → still blocked**  
`impersonate="chrome99"` was too old; newer Cloudflare rules catch it.  
Fix: use a recent version like `chrome120`. Check `curl_cffi.requests.DEFAULT_CHROME` for the current default.

**Problem 3 — curl_cffi gets in but infinite scroll doesn't load**  
Trustpilot loads initial reviews server-side (in `__NEXT_DATA__` JSON). Pages 2+ work with `?page=N`.  
But some companies with fewer reviews show a JS-driven "load more" button instead of pagination.  
For those, you need Playwright (Day 8). curl_cffi alone can't execute JavaScript.

## Articles

- Medium: [Day 3 — Trustpilot Review Scraper with curl_cffi] *(link after publish)*
- LinkedIn: [What Actually Blocks Python Scrapers (and How curl_cffi Fixes It)] *(link after publish)*
