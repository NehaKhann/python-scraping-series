"""
Run the ProductsSpider from the command line.
Output saved to products.json.

Usage:
    python run_spider.py

No asyncio reactor hack needed — our custom curl_handler.py uses
deferToThread() which works with Scrapy's default Twisted reactor.
"""

import json
from pathlib import Path
from scrapy.crawler import CrawlerProcess

from spider import ProductsSpider

OUTPUT = Path(__file__).parent / "products.json"


def run() -> list[dict]:
    process = CrawlerProcess(settings={
        "FEEDS": {
            str(OUTPUT): {
                "format":    "json",
                "overwrite": True,
            }
        },
        "LOG_LEVEL": "INFO",
    })
    process.crawl(ProductsSpider)
    process.start()  # blocks until spider is done

    if OUTPUT.exists():
        data = json.loads(OUTPUT.read_text(encoding="utf-8"))
        print(f"✅ Done — {len(data)} products saved to {OUTPUT.name}")
        return data

    print("❌ Spider finished but no output file found.")
    return []


if __name__ == "__main__":
    run()
