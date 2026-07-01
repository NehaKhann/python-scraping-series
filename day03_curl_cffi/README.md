# Day 3 — G2 Review Scraper (curl_cffi)

> **Stack:** curl_cffi · BeautifulSoup4 · Streamlit  
> **Target:** www.g2.com (software reviews)  
> **Series:** [Python Scraping Series](../)

Scrapes G2 software reviews using `curl_cffi` — a Python binding for curl-impersonate that bypasses TLS fingerprint detection.

## What This Is About

Sites protected by Cloudflare check your **TLS fingerprint** — a signature your HTTP client sends during the connection handshake, before any request is made. Python's `httpx` has a fingerprint that looks like a bot. `curl_cffi` sends Chrome's exact fingerprint instead.

> **Why not Trustpilot?** Originally targeted Trustpilot, but they use **Cloudflare Bot Management** — a different tier that also runs JavaScript challenges and behaviour analysis. curl_cffi only handles the TLS layer, not JS challenges. Switched to G2 (standard Cloudflare). Documented as an honest lesson in the article.

## Files

```
day03_curl_cffi/
├── scraper.py        ← curl_cffi session, homepage warm-up, itemprop parser
├── app.py            ← Streamlit UI: product input, charts, filters, export
├── requirements.txt
├── article.md        ← Medium article
├── linkedin_article.md
├── linkedin_post.md
├── linkedin_carousel.html   ← 7 slides, 1080x1080px
└── linkedin_infographic.html ← single tall infographic, 1080px wide
```

## Quick Start

```bash
cd day03_curl_cffi
pip install -r requirements.txt

# Terminal — scrape reviews for a product
python scraper.py --product notion --pages 3
python scraper.py --product slack --pages 1
python scraper.py --product figma --pages 2

# Streamlit UI
streamlit run app.py
```

G2 product slugs come from the URL: `g2.com/products/SLUG/reviews`

## What Broke (3 real mistakes)

**Problem 1 — httpx returns 403**  
Cloudflare identifies Python's TLS fingerprint and blocks it before any HTTP data is sent.  
Fix: `curl_cffi` with `impersonate="chrome124"` — sends Chrome's exact cipher suites and HTTP/2 settings.

**Problem 2 — Wrong target (Trustpilot uses Bot Management, not standard Cloudflare)**  
curl_cffi bypasses TLS fingerprinting. Trustpilot's Cloudflare Bot Management also runs JS challenges — curl_cffi can't execute JavaScript, so all Chrome versions returned 403.  
Fix: switched to G2.com which uses standard Cloudflare. TLS impersonation is enough.

**Problem 3 — Hardcoded Chrome version broke when Cloudflare updated its blocklist**  
`impersonate="chrome120"` stopped working after Cloudflare added it to the blocklist.  
Fix: try multiple versions in sequence (`chrome131 → chrome124 → chrome120 → chrome110`), use the first that returns 200.

## How Parsing Works

G2 uses Schema.org `itemprop` markup on review cards — the same HTML annotation that lets Google show star ratings in search results. This means the review data is clean and labelled directly in the HTML:

```html
<div itemprop="review">
  <span itemprop="author">John D.</span>
  <meta itemprop="ratingValue" content="5">
  <span itemprop="name">Best tool for our team</span>
  <span itemprop="reviewBody">We've been using Notion for 2 years...</span>
  <time itemprop="datePublished" datetime="2024-10-15">
</div>
```

No JavaScript execution needed. No fragile CSS class selectors.

## Articles

- Medium: [Day 3 — I Tried to Scrape Trustpilot. Cloudflare Had Other Plans.] *(link after publish)*
- LinkedIn Article: [I Tried to Scrape Trustpilot. Here's Where That Plan Fell Apart.] *(link after publish)*
