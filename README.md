# Python Scraping Series

14 days. 14 scraping projects. Real code, real mistakes, real fixes.

Each day covers a different tool or technique — from bare HTTP requests to full browser automation.
Every project includes working Python code + a Streamlit UI + a written breakdown of what broke and why.

---

## Projects

| Day | Project | Stack | Status |
|-----|---------|-------|--------|
| 01 | [LinkedIn Job Scraper](./day01_linkedin_jobs/) | httpx + BeautifulSoup4 + Streamlit | ✅ Done |
| 02 | [Book Price Tracker](./day02_scrapy/) | Scrapy + Streamlit | ✅ Done |
| 03 | [Trustpilot Review Scraper](./day03_curl_cffi/) | curl_cffi + BeautifulSoup4 + Streamlit | ✅ Done |
| 🎁 | [Scrapy + curl_cffi Combined](./bonus_scrapy_curl_cffi/) | Scrapy + scrapy-impersonate + curl_cffi + Streamlit | ✅ Done |
| 04 | AI-powered crawler | crawl4ai | 🔜 Coming |
| 05 | Agent-based scraping | browser-use | 🔜 Coming |
| 06 | Auto-detect scraper | autoscraper | 🔜 Coming |
| 07 | Managed scraping API | Firecrawl | 🔜 Coming |
| 08 | Dynamic pages | Playwright | 🔜 Coming |
| 09 | Cloudflare bypass (cookies + request mirroring) | CloudflareBypassForScraping | 🔜 Coming |
| 10 | Large-scale crawling | crawlee-python | 🔜 Coming |
| 11 | Markdown from any URL | markitdown | 🔜 Coming |
| 12 | News article extraction | newspaper4k | 🔜 Coming |
| 13 | CAPTCHA solving | 2captcha | 🔜 Coming |
| 14 | Rotating proxies | proxy rotator | 🔜 Coming |
| 15 | Lightweight headless browser for AI agents | Obscura (Rust) | 🔜 Coming |

---

## Articles

Each day has three pieces of content:

- **Medium article** — technical deep-dive with full code
- **LinkedIn Article** — story-driven breakdown of mistakes and fixes
- **LinkedIn Post** — short feed post linking both

---

## Structure

```
python-scraping-series/
├── day01_linkedin_jobs/
│   ├── scraper.py          ← async scraper (httpx + BeautifulSoup4)
│   ├── app.py              ← Streamlit UI
│   ├── locations.py        ← country/city/geoId data + reliability ratings
│   ├── find_geoid.py       ← CLI tool to look up verified LinkedIn geoIds
│   ├── test_subdomain.py   ← experiment: do country subdomains help?
│   └── requirements.txt
├── day02_scrapy/
│   ├── booktracker/        ← Scrapy project
│   ├── app.py              ← Streamlit UI
│   └── requirements.txt
├── day03_curl_cffi/
│   ├── scraper.py          ← curl_cffi session + __NEXT_DATA__ parser
│   ├── app.py              ← Streamlit UI
│   └── requirements.txt
└── ...
```

---

## Running Day 1

```bash
cd day01_linkedin_jobs
pip install -r requirements.txt

# Streamlit UI
streamlit run app.py

# Terminal
python scraper.py --keyword "Data Engineer" --location "United Kingdom" --max-jobs 25

# Verify geoId for any location
python find_geoid.py "Germany"
```

---

## Key Findings

**LinkedIn's guest API (`jobs-guest`) only reliably covers US/UK markets.**

For Saudi Arabia, UAE, Pakistan, India and most of the Middle East and South Asia:
- Passing `location=Saudi Arabia` → returns UK jobs
- Passing correct `geoId=101004847` → returns UK jobs
- Hitting `sa.linkedin.com` instead of `www.linkedin.com` → same UK jobs
- Hitting `pk.linkedin.com` for Pakistan → same UK jobs

Country subdomains are DNS aliases pointing at the same backend. There is no URL workaround.
Use LinkedIn directly (logged in) or a paid service like Apify/BrightData for those regions.

---

## Follow Along

Articles published daily on [Medium](https://medium.com/@n.nehakhan333) and [LinkedIn](https://www.linkedin.com/in/neha-khan-b576b7219/).
