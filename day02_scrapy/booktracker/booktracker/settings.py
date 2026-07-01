BOT_NAME = "booktracker"

SPIDER_MODULES = ["booktracker.spiders"]
NEWSPIDER_MODULE = "booktracker.spiders"

# ── Politeness ────────────────────────────────────────────────────────────────
# Default CONCURRENT_REQUESTS is 16 — way too aggressive for a single site.
# Lower it to be respectful and avoid getting blocked.
CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 0.5          # seconds between requests from the SAME spider
RANDOMIZE_DOWNLOAD_DELAY = True  # adds 0.5× to 1.5× jitter — looks more human

# ── Robots.txt ────────────────────────────────────────────────────────────────
ROBOTSTXT_OBEY = True         # books.toscrape.com allows scraping — good habit

# ── Output ────────────────────────────────────────────────────────────────────
# Written to the Scrapy project root (next to scrapy.cfg)
FEEDS = {
    "books.json": {
        "format":    "json",
        "encoding":  "utf-8",
        "overwrite": True,
    },
}

# ── Pipelines ────────────────────────────────────────────────────────────────
ITEM_PIPELINES = {
    "booktracker.pipelines.BookTrackerPipeline": 300,
}

# ── Misc ──────────────────────────────────────────────────────────────────────
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"
