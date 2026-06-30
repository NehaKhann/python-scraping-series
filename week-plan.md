# 2-Week Scraping Series — Full Content & Build Plan (14+ Projects)

> **Goal:** One project per day for 2 weeks (14 days + 1 bonus).  
> **Each day delivers:** Working Python code + Medium article draft + LinkedIn post  
> **Audience:** Mixed (beginner-friendly framing, real technical depth)  
> **LinkedIn strategy:** Hook → What we built → Pros → Cons/Limitations → CTA (follow for tomorrow's)

---

## WEEK 1 — Foundations to AI

**Arc:** Simple HTTP → Classic Framework → Anti-Detection → AI Crawling → LLM Agent → Zero-Config → Production

---

### Day 1 — LinkedIn Job Postings Scraper
**Source:** [Medium by Emmanuel Uchenna](https://medium.com/@eunithelp/how-to-scrape-linkedin-job-postings-with-python-a-step-by-step-guide-67341eb3dbde)  
**Stack:** `httpx` + `BeautifulSoup4` + Apify residential proxies  
**Target:** LinkedIn public job listings (title, company, location, salary, description)  

**Hook:** "I scraped 500 LinkedIn jobs in 60 seconds — without Selenium, without a browser."

**Pros:** Fast async HTTP, no browser overhead, uses LinkedIn's internal guest API endpoint, no login needed  
**Cons:** IP bans at scale → needs rotating proxies, LinkedIn changes endpoints, against ToS at scale, Apify proxies cost money  

---

### Day 2 — Scrapy Spider (E-Commerce Price Tracker)
**Repo:** [github.com/scrapy/scrapy](https://github.com/scrapy/scrapy) · ⭐ 62k+  
**Stack:** `scrapy` + `scrapy-playwright` middleware  
**Target:** books.toscrape.com → titles, prices, ratings, availability → auto-export to CSV  

**Hook:** "The grandfather of Python scrapers is 12 years old — and it still dominates. Here's why."

**Pros:** Battle-tested, built-in pipelines + middleware + exports, handles pagination natively, huge ecosystem  
**Cons:** Steep learning curve, overkill for one-offs, JS-heavy sites need scrapy-playwright add-on  

---

### Day 3 — Bypass Cloudflare with curl-impersonate
**Repo:** [github.com/lwthiker/curl-impersonate](https://github.com/lwthiker/curl-impersonate)  
**Stack:** `curl-impersonate` + Python subprocess wrapper  
**Target:** Any Cloudflare-protected site — impersonate Chrome's TLS fingerprint  

**Hook:** "Cloudflare blocked my scraper. So I made Python pretend to be Chrome."

**Pros:** Bypasses TLS fingerprinting (#1 modern block method), no browser overhead, still fast  
**Cons:** Linux/macOS only (no Windows binary), needs compiling from source, doesn't defeat JS challenges  

---

### Day 4 — AI-Powered Crawling with crawl4ai
**Repo:** [github.com/unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) · ⭐ 68k+  
**Stack:** `crawl4ai` + async Python  
**Target:** News site + product page → clean Markdown + structured JSON via LLM extraction  

**Hook:** "68,000 devs starred this. crawl4ai turns any website into clean data in one line of Python."

**Pros:** Zero CSS selectors, LLM extracts structure, outputs Markdown (perfect for RAG), async multi-URL  
**Cons:** LLM extraction costs API tokens, slower than raw httpx, non-deterministic output  

---

### Day 5 — LLM Browser Agent with browser-use
**Repo:** [github.com/browser-use/browser-use](https://github.com/browser-use/browser-use)  
**Stack:** `browser-use` + Playwright + GPT-4o / Claude  
**Target:** "Go to Hacker News, find top 5 AI posts, return titles and upvotes" — pure natural language  

**Hook:** "I gave GPT-4o a browser and said 'scrape this.' It did. No code. No selectors. Just vibes."

**Pros:** No selectors needed, handles login + multi-step flows, works on any site a human can use  
**Cons:** Expensive (LLM API per action), slow, non-deterministic, not for bulk scraping  

---

### Day 6 — Zero-Config Scraping with autoscraper
**Repo:** [github.com/alirezamika/autoscraper](https://github.com/alirezamika/autoscraper)  
**Stack:** `autoscraper` (pure Python)  
**Target:** Train on one example value → extract all similar items from any similar page  

**Hook:** "This Python library learns your scraping rules from one example. No selectors. No code."

**Pros:** Insanely low barrier, self-learns HTML patterns, reusable/saveable model, great for list pages  
**Cons:** Fragile on JS-heavy sites, breaks if layout changes, can't handle pagination well  

---

### Day 7 — Production AI Pipeline with Firecrawl
**Repo:** [github.com/mendableai/firecrawl](https://github.com/mendableai/firecrawl) · ⭐ 131k+  
**Stack:** `firecrawl-py` SDK  
**Target:** Crawl entire docs site → clean Markdown per page → ready for RAG / AI knowledge base  

**Hook:** "131,000 GitHub stars. One line of Python. This is what production AI scraping looks like in 2026."

**Pros:** JS rendering + pagination + sitemaps automatic, LLM-ready output, managed (no proxy config)  
**Cons:** Free tier limited (500 pages/month), API dependency, overkill for simple scrapes  

---

## WEEK 2 — Stealth, Scale & Niche

**Arc:** Modern Browser Automation → Cloudflare Python → Production Framework → Document Scraping → News Extraction → CAPTCHA Solving → Proxy Rotation → Mobile Scraping (Bonus)

---

### Day 8 — Playwright (Modern Selenium Replacement)
**Repo:** [github.com/microsoft/playwright-python](https://github.com/microsoft/playwright-python) · ⭐ 12k+  
**Stack:** `playwright` (async Python)  
**Target:** Scrape a JS-heavy SPA (Single Page App) — e.g. a React-rendered job board or dashboard  

**Hook:** "I stopped using Selenium in 2026. Here's what I use instead — and why it's 10x better."

**Pros:** Native async, auto-waiting (no more time.sleep()), multi-browser (Chrome + Firefox + WebKit), fast  
**Cons:** Larger install size, fingerprinting detection still possible, overkill for static sites  

---

### Day 9 — Bypass Cloudflare in Pure Python with cloudscraper
**Repo:** [github.com/VeNoMouS/cloudscraper](https://github.com/VeNoMouS/cloudscraper)  
**Stack:** `cloudscraper` (drop-in `requests` replacement)  
**Target:** Sites protected by Cloudflare Bot Management — zero browser, pure Python  

**Hook:** "Two lines of Python. Cloudflare bypassed. Meet cloudscraper."

**Pros:** Drop-in replacement for `requests`, handles JS challenges, supports proxy rotation, Turnstile support  
**Cons:** Cloudflare updates break it periodically, not effective against heavy bot scores, no active 2026 maintenance  

---

### Day 10 — Production Crawling with crawlee-python (Apify)
**Repo:** [github.com/apify/crawlee-python](https://github.com/apify/crawlee-python)  
**Stack:** `crawlee` + BeautifulSoup / Playwright  
**Target:** Full site crawler with request queue, retry logic, proxy rotation, structured output  

**Hook:** "This is how big companies build scrapers. Crawlee gives you enterprise features in 10 lines."

**Pros:** Built-in retry, request queue, proxy rotation, supports both HTTP and browser crawling  
**Cons:** More setup than simple scripts, Python port is newer (JS version more mature), heavier dependency  

---

### Day 11 — Scrape PDFs, Word Docs & YouTube with markitdown
**Repo:** [github.com/microsoft/markitdown](https://github.com/microsoft/markitdown) · Microsoft  
**Stack:** `markitdown` (Python)  
**Target:** Convert PDFs, .docx, .pptx, YouTube video transcripts, and HTML pages → clean Markdown  

**Hook:** "Microsoft just open-sourced a tool that turns PDFs, Word docs, and YouTube videos into scrapable text."

**Pros:** Handles PDFs, Office files, images, YouTube, HTML in one unified API, LLM-ready output  
**Cons:** No browser rendering, OCR quality varies, YouTube requires API key for transcripts  

---

### Day 12 — Automated News Scraping with newspaper4k
**Repo:** [github.com/AndyTheFactory/newspaper4k](https://github.com/AndyTheFactory/newspaper4k)  
**Stack:** `newspaper4k` (Python)  
**Target:** Give it a news URL → extract article text, author, publish date, top image, keywords, summary  

**Hook:** "One line of Python extracts any news article — text, author, date, keywords, summary. Meet newspaper4k."

**Pros:** Zero HTML parsing needed, NLP features built-in (keywords, summary), handles 100+ news formats  
**Cons:** Paywalled content inaccessible, inconsistent on non-news sites, NLP requires NLTK download  

---

### Day 13 — Solving CAPTCHAs Programmatically (2captcha)
**Repo:** [github.com/2captcha/2captcha-python](https://github.com/2captcha/2captcha-python)  
**Stack:** `2captcha-python` + Playwright  
**Target:** Build a scraper that hits a reCAPTCHA-protected form, solves it via 2captcha API, submits  

**Hook:** "Yes, you can solve CAPTCHAs with Python. Here's how — and why it's not magic."

**Pros:** Solves reCAPTCHA, hCaptcha, Turnstile, FunCaptcha, image CAPTCHAs — works on real sites  
**Cons:** Costs money (~$3/1000 solves), 15-60 second solve time, some sites now detect the pattern  

---

### Day 14 — Build Your Own Proxy Rotator (Free Proxies)
**Repo:** [github.com/topics/proxy-rotation](https://github.com/topics/proxy-rotation) + custom build  
**Stack:** `requests` + `fp-proxy-rotation` or custom pool logic  
**Target:** Scrape a free proxy list, validate them, build a rotating proxy pool, use it in a scraper  

**Hook:** "I built a free proxy rotator in Python — here's what worked, what broke, and the hard truth about free proxies."

**Pros:** Free, teaches you how proxy rotation works under the hood, reusable across all scrapers  
**Cons:** Free proxies are unreliable (80%+ dead), slow, not suitable for production — this is educational  

---

### Day 15 (BONUS) — Scrape Mobile Apps with scrcpy
**Repo:** [github.com/Genymobile/scrcpy](https://github.com/Genymobile/scrcpy) · ⭐ 120k+  
**Stack:** `scrcpy` + `adb` + Python screen capture + `pytesseract` OCR  
**Target:** Mirror Android screen → take screenshots of app UI → OCR the text → extract data  

**Hook:** "120k GitHub stars — and nobody talks about using scrcpy to scrape mobile apps. I tried it."

**Pros:** Access data from apps that have no website or API, works on any Android app  
**Cons:** Requires physical device or emulator, OCR errors on complex UIs, slow vs. web scraping, fragile  

---

## Full 2-Week Calendar

| Day | Topic | Stack / Repo | Hook Theme | Difficulty |
|-----|-------|-------------|------------|------------|
| 1 | LinkedIn Jobs Scraper | httpx + BS4 | "Without Selenium" | Beginner |
| 2 | Scrapy Spider | Scrapy ⭐62k | "Still the GOAT?" | Intermediate |
| 3 | Bypass Cloudflare (CLI) | curl-impersonate | "Pretend to be Chrome" | Intermediate |
| 4 | AI Web Crawling | crawl4ai ⭐68k | "68k stars, I tried it" | Beginner-AI |
| 5 | LLM Browser Agent | browser-use | "GPT-4o with a browser" | AI/Advanced |
| 6 | Zero-Config Scraper | autoscraper | "Learns from one example" | Beginner |
| 7 | Production AI Pipeline | Firecrawl ⭐131k | "131k stars, 1 line" | Intermediate |
| 8 | Playwright Scraping | playwright-python ⭐12k | "I quit Selenium" | Intermediate |
| 9 | Bypass Cloudflare (Python) | cloudscraper | "Two lines, bypassed" | Beginner |
| 10 | Production Crawler | crawlee-python (Apify) | "How big companies do it" | Intermediate |
| 11 | PDF/Doc/YouTube Scraping | markitdown (Microsoft) | "Microsoft's secret tool" | Beginner |
| 12 | News Article Extraction | newspaper4k | "One line, full article" | Beginner |
| 13 | CAPTCHA Solving | 2captcha + Playwright | "Yes, you can solve CAPTCHAs" | Advanced |
| 14 | Build a Proxy Rotator | Custom Python | "Free proxies: the truth" | Intermediate |
| 15 ⭐ | Scrape Mobile Apps | scrcpy ⭐120k + OCR | "Nobody talks about this" | Advanced |

---

## LinkedIn Content Strategy

**Post format for each day:**
1. **Hook** (1-2 lines, bold claim or surprising fact)
2. **What I built** (2-3 lines, what it does)
3. **The setup** (quick 3-step: install → code → run)
4. **Pros** (3 bullets)
5. **Cons/Limitations** (3 bullets — this builds trust)
6. **CTA** ("Follow for Day X tomorrow → [topic]")

**Hashtags to use:** #Python #WebScraping #DataEngineering #OpenSource #BuildInPublic #100DaysOfCode

---

## Repos — Full Reference

| Repo | Stars | Used |
|------|-------|------|
| [firecrawl/firecrawl](https://github.com/mendableai/firecrawl) | ⭐131k | Day 7 |
| [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy) | ⭐120k | Day 15 |
| [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) | ⭐68k | Day 4 |
| [scrapy/scrapy](https://github.com/scrapy/scrapy) | ⭐62k | Day 2 |
| [browser-use/browser-use](https://github.com/browser-use/browser-use) | — | Day 5 |
| [microsoft/playwright-python](https://github.com/microsoft/playwright-python) | ⭐12k | Day 8 |
| [microsoft/markitdown](https://github.com/microsoft/markitdown) | — | Day 11 |
| [apify/crawlee-python](https://github.com/apify/crawlee-python) | — | Day 10 |
| [lwthiker/curl-impersonate](https://github.com/lwthiker/curl-impersonate) | — | Day 3 |
| [VeNoMouS/cloudscraper](https://github.com/venomous/cloudscraper) | — | Day 9 |
| [alirezamika/autoscraper](https://github.com/alirezamika/autoscraper) | — | Day 6 |
| [2captcha/2captcha-python](https://github.com/2captcha/2captcha-python) | — | Day 13 |
| [AndyTheFactory/newspaper4k](https://github.com/AndyTheFactory/newspaper4k) | — | Day 12 |

---

## Folder Structure
```
Scraping/
├── week-plan.md
├── day01_linkedin_jobs/
├── day02_scrapy_spider/
├── day03_curl_impersonate/
├── day04_crawl4ai/
├── day05_browser_use/
├── day06_autoscraper/
├── day07_firecrawl/
├── day08_playwright/
├── day09_cloudscraper/
├── day10_crawlee/
├── day11_markitdown/
├── day12_newspaper4k/
├── day13_captcha_solving/
├── day14_proxy_rotator/
└── day15_scrcpy_mobile/
```
