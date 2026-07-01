# Day 3 — Cloudflare Bypass with curl_cffi

> **Stack:** curl_cffi · BeautifulSoup4 · Streamlit  
> **Target:** scrapingcourse.com/cloudflare-challenge  
> **Series:** [Python Scraping Series](../)

Demonstrates how `curl_cffi` bypasses standard Cloudflare TLS fingerprint detection.
`httpx` gets 403. `curl_cffi` impersonating Chrome gets 200.

## The Core Concept

Before any HTTP request, your client does a TLS handshake — announces which cipher suites
it supports in a specific order. This is a **fingerprint**. Cloudflare blocks Python's
fingerprint. `curl_cffi` sends Chrome's exact fingerprint instead.

> **Why not Trustpilot or G2?**  
> Both were tried and blocked — even on a fresh IP (mobile hotspot).  
> They use **Cloudflare Bot Management**, not standard Cloudflare.  
> Bot Management adds JavaScript challenges and behaviour analysis on top of TLS checking.  
> curl_cffi cannot execute JavaScript. This is not a bug — it's a different product.  
> Those sites need Playwright (Day 8).

## Files

```
day03_curl_cffi/
├── scraper.py              ← shows httpx fail, then curl_cffi succeed, then parses
├── app.py                  ← Streamlit UI with side-by-side httpx vs curl_cffi demo
├── diagnose.py             ← tests if curl_cffi works on your machine
├── requirements.txt
├── article.md              ← Medium article
├── linkedin_article.md
├── linkedin_post.md
├── linkedin_carousel.html  ← 7 slides 1080×1080px
└── linkedin_infographic.html
```

## Quick Start

```bash
cd day03_curl_cffi
pip install -r requirements.txt

# Terminal demo — shows httpx vs curl_cffi comparison
python scraper.py

# Streamlit UI
streamlit run app.py

# Diagnostic — check if curl_cffi works on your machine
python diagnose.py
```

## What Broke (3 real mistakes)

**Mistake 1 — Wrong target: Trustpilot uses Bot Management, not standard Cloudflare**  
curl_cffi solves TLS fingerprinting. Trustpilot's Cloudflare also runs JS challenges.
curl_cffi cannot execute JavaScript. Every Chrome version blocked.

**Mistake 2 — Wrong target again: G2 same story**  
G2 also uses Bot Management. Even switching to a mobile hotspot (fresh IP) didn't help —
the JS challenge fails regardless of IP. Switched to `scrapingcourse.com` which uses
standard Cloudflare and is designed for this exact demo.

**Mistake 3 — Debugging by changing code instead of diagnosing**  
Spent time trying different Chrome versions before checking if curl_cffi worked at all.
`python diagnose.py` proves in 10 seconds whether the tool is broken or the target is.

## How to Tell Which Cloudflare Tier a Site Uses

Open the site in Chrome with JavaScript disabled → `chrome://settings/content/javascript`

- Page loads normally → Standard Cloudflare → curl_cffi works ✅
- Challenge screen or blank page → Bot Management → need Playwright ❌

## Articles

- Medium: [Three Sites. All Blocked. Here's What I Learned About Cloudflare.] *(link after publish)*
- LinkedIn Article: [Three Sites. All Blocked. Cloudflare Has Two Tiers.] *(link after publish)*
