# Bonus — Scrapy + curl_cffi: The Power Duo

> **Stack:** Scrapy · scrapy-impersonate · curl_cffi · Streamlit  
> **Target:** scrapingcourse.com/cloudflare-challenge  
> **Series:** [Python Scraping Series](../)

Combines the frameworks from Day 2 and Day 3:

- **Day 2 (Scrapy)** — manages crawling at scale: pagination, retries, pipelines, output
- **Day 3 (curl_cffi)** — bypasses Cloudflare TLS fingerprint detection

The bridge between them is `scrapy-impersonate` — it replaces Scrapy's built-in HTTP client with curl_cffi. Every request Scrapy fires now uses Chrome's exact TLS fingerprint.

## The Problem This Solves

Scrapy alone gets **403** on Cloudflare-protected sites. Its default HTTP engine (Twisted) has a Python bot fingerprint that Cloudflare blocks immediately.

curl_cffi alone handles one URL at a time. You write the pagination logic, retry logic, and output handling yourself.

If a site has **50 Cloudflare-protected pages**, you need both.

## What Changed From Normal Scrapy

Just two things:

**1. Add `custom_settings` to replace the HTTP engine:**
```python
custom_settings = {
    "DOWNLOAD_HANDLERS": {
        "http":  "scrapy_impersonate.ImpersonateDownloadHandler",
        "https": "scrapy_impersonate.ImpersonateDownloadHandler",
    },
    "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
}
```

**2. Add `meta={"impersonate": "chrome124"}` to each request:**
```python
yield scrapy.Request(url, meta={"impersonate": "chrome124"})
```

Everything else is normal Scrapy. Pagination, pipelines, feeds — unchanged.

## Files

```
bonus_scrapy_curl_cffi/
├── spider.py       ← Scrapy spider with scrapy-impersonate
├── run_spider.py   ← Runs spider, saves products.json
├── app.py          ← Streamlit UI
├── requirements.txt
├── article.md
├── linkedin_article.md
└── linkedin_post.md
```

## Quick Start

```bash
cd bonus_scrapy_curl_cffi
pip install -r requirements.txt

# Terminal — run spider directly
python run_spider.py

# Streamlit UI
streamlit run app.py
```

## Reference

- [scrapy-impersonate on GitHub](https://github.com/jxlil/scrapy-impersonate)
- [Original article by Dima Kynal](https://medium.com/@dimakynal/enhancing-scrapy-with-curl-cffi-a-powerful-duo-for-web-scraping-5231c5968d2e)
