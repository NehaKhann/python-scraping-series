# Day 1 — LinkedIn Job Scraper

> **Stack:** httpx · BeautifulSoup4 · Streamlit  
> **Series:** [Python Scraping Series](../)

Scrapes LinkedIn job listings without a browser or Selenium. Uses LinkedIn's internal guest API directly.

## Files

| File | Purpose |
|------|---------|
| `scraper.py` | Async scraper — handles pagination, rate limiting, retries |
| `app.py` | Streamlit UI with country/city dropdowns and mismatch detection |
| `locations.py` | 35+ countries with geoIds and reliability ratings (✅ ⚠️ ❌) |
| `find_geoid.py` | CLI tool to look up verified LinkedIn geoIds |
| `test_subdomain.py` | Experiment: do `sa.linkedin.com` / `pk.linkedin.com` return regional jobs? |
| `requirements.txt` | Dependencies |

## Quick Start

```bash
pip install -r requirements.txt

# UI
streamlit run app.py

# Terminal
python scraper.py --keyword "Data Engineer" --location "United Kingdom" --max-jobs 25

# Look up a geoId
python find_geoid.py "Germany"
python find_geoid.py "Karachi"
```

## What Broke

**Problem 1 — 429 Too Many Requests**

Sending 50 detail requests simultaneously gets every one blocked. Fixed with:
- `CONCURRENCY = 2` (was 5)
- `random.uniform(2.0, 4.0)` delay before each request
- Exponential backoff retry on 429

**Problem 2 — Saudi Arabia returns UK jobs**

LinkedIn's guest API is US/UK only. For Saudi Arabia, UAE, Pakistan, India — it ignores the geoId and returns UK results. We tested 4 workarounds (including country subdomains). All returned the same Manchester/Leeds jobs.

The app detects this automatically and shows a clear error when >40% of results are from the wrong country.

## Articles

- Medium: [How to Scrape LinkedIn Job Postings with Python — No Selenium Required](https://medium.com/@n.nehakhan333/how-i-scraped-linkedin-job-postings-with-python-without-selenium-bc4207efe001)
- LinkedIn: [2 Things That Break When You Scrape LinkedIn Jobs](https://www.linkedin.com/pulse/how-i-scraped-linkedin-job-postings-python-without-selenium-neha-khan-ykoif/)
