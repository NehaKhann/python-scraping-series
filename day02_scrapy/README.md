# Day 2 — Book Price Tracker with Scrapy

> **Stack:** Scrapy · Streamlit · pandas  
> **Target:** books.toscrape.com  
> **Series:** [Python Scraping Series](../)

Scrapes every book on books.toscrape.com — price, rating, category, description.
Streamlit UI with filters, charts, and CSV/JSON export.

## Files

```
day02_scrapy/
├── booktracker/              ← Scrapy project (cd here to run scrapy commands)
│   ├── scrapy.cfg
│   └── booktracker/
│       ├── items.py          ← BookItem schema
│       ├── pipelines.py      ← cleans price (£12.99→12.99), rating ("Three"→3)
│       ├── settings.py       ← concurrency, delay, output config
│       └── spiders/
│           └── books_spider.py
├── app.py                    ← Streamlit UI
└── requirements.txt
```

## Quick Start

```bash
pip install -r requirements.txt

# Terminal — scrape 50 books
cd booktracker
scrapy crawl books -s CLOSESPIDER_ITEMCOUNT=50

# Scrape a specific category
scrapy crawl books -a category="Mystery"

# Streamlit UI (from day02_scrapy/)
cd ..
streamlit run app.py
```

## Articles

- Medium: [How to Build a Book Price Tracker with Scrapy](https://medium.com/@n.nehakhan333/how-to-build-a-book-price-tracker-with-scrapy-and-what-breaks-along-the-way-20a04324394d)
- LinkedIn: [3 Things That Break When You Start with Scrapy](https://www.linkedin.com/feed/update/urn:li:activity:7478197520834416640/)


## What Broke

**Problem 1 — ReactorNotRestartable**
Running Scrapy in a Streamlit thread crashes on the second click.
Twisted's reactor is a singleton — can't restart in the same process.
Fix: run as subprocess (`subprocess.run(["scrapy", "crawl", "books"], cwd=...)`).

**Problem 2 — Rating stored as CSS class word**
`<p class="star-rating Three">` — not a number, not a data attribute.
Pipeline maps: `{"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}`.

**Problem 3 — "Â£12.99" encoding quirk**
books.toscrape.com UTF-8 issue doubles the £ sign.
Pipeline strips both `"Â£"` and `"£"` before converting to float.

