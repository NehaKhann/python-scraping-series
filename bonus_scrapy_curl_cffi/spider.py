"""
Bonus Project — Scrapy + curl_cffi (custom handler)
Target: scrapingcourse.com/cloudflare-challenge

Key difference from Day 3:
  Day 3  → curl_cffi handles ONE page manually with a loop
  Bonus  → Scrapy manages crawling; curl_cffi handles every request via curl_handler.py

How it works:
  curl_handler.CurlCffiHandler replaces Scrapy's default HTTP engine.
  Every request Scrapy sends goes through curl_cffi instead of Twisted's HTTP client.
  curl_cffi sends Chrome's TLS fingerprint. Cloudflare sees Chrome. Gets through.
  Scrapy still handles: pagination, retries, output — everything else.
"""

import scrapy


class ProductsSpider(scrapy.Spider):
    name = "products"

    custom_settings = {
        # Replace Scrapy's HTTP engine with our custom curl_cffi handler.
        # curl_handler.py uses curl_cffi's Session(impersonate=...) for every request.
        # No scrapy-impersonate needed — we wrote the handler ourselves.
        "DOWNLOAD_HANDLERS": {
            "http":  "curl_handler.CurlCffiHandler",
            "https": "curl_handler.CurlCffiHandler",
        },

        "AUTOTHROTTLE_ENABLED":     True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY":   5,
        "CONCURRENT_REQUESTS":      1,   # 1 at a time — polite scraping
        "LOG_LEVEL":                "INFO",
    }

    START_URL = "https://www.scrapingcourse.com/cloudflare-challenge"

    def start_requests(self):
        yield scrapy.Request(
            self.START_URL,
            callback=self.parse,
            meta={"impersonate": "chrome131"},
        )

    def parse(self, response):
        """Parse products. Follow pagination if a next-page link exists."""

        if response.status != 200:
            self.logger.warning(f"Non-200 ({response.status}). Snippet: {response.text[:300]}")
            return

        products = response.css("li.product")

        if not products:
            self.logger.warning(f"No li.product found. Snippet: {response.text[:300]}")
            return

        self.logger.info(f"Found {len(products)} products on {response.url}")

        for product in products:
            name = (
                product.css("h2.woocommerce-loop-product__title::text").get()
                or product.css("h2::text").get()
                or ""
            ).strip()

            price = (
                product.css("span.price bdi::text").get()
                or product.css(".price::text").get()
                or ""
            ).strip()

            image = product.css("img::attr(src)").get(default="")
            url   = product.css("a::attr(href)").get(default="")

            if name:
                yield {
                    "name":  name,
                    "price": price,
                    "image": image,
                    "url":   url,
                    "page":  response.url,
                }

        # Scrapy follows pagination automatically
        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            self.logger.info(f"Next page → {next_page}")
            yield scrapy.Request(
                next_page,
                callback=self.parse,
                meta={"impersonate": "chrome131"},
            )
