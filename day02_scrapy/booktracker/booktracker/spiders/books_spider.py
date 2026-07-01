"""
Day 2 — books.toscrape.com spider

Scrapes title, price, rating, availability, category, and description
for every book on the site (or up to CLOSESPIDER_ITEMCOUNT).

Run from the booktracker/ directory:
    scrapy crawl books
    scrapy crawl books -s CLOSESPIDER_ITEMCOUNT=50
    scrapy crawl books -a category="Mystery"
"""

import scrapy
from booktracker.items import BookItem


class BooksSpider(scrapy.Spider):
    name         = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls   = ["https://books.toscrape.com/"]

    # Optional filters passed via -a flag or CrawlerProcess kwargs
    def __init__(self, category=None, min_rating=None, max_price=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_category  = category.strip().lower() if category else None
        self.filter_min_rating = int(min_rating) if min_rating else None
        self.filter_max_price  = float(max_price) if max_price else None

    # ── Step 1: Parse book listing pages ─────────────────────────────────────

    def parse(self, response):
        """
        Called on each catalogue page (50 books per page).
        Yields a follow request to each book's detail page.
        Also follows the "next" pagination link.
        """
        for book_el in response.css("article.product_pod"):
            # Grab the partial detail URL and make it absolute
            relative_url = book_el.css("h3 a::attr(href)").get()
            detail_url   = response.urljoin(relative_url)

            # Collect list-page fields here so we don't need a second request
            # if we're running in item-count-limited mode
            partial = BookItem(
                title        = book_el.css("h3 a::attr(title)").get(default=""),
                price        = book_el.css("p.price_color::text").get(default="£0.00"),
                rating       = book_el.css("p.star-rating::attr(class)").get(default=""),
                availability = book_el.css("p.availability::text").getall(),
                url          = detail_url,
                # These come from the detail page
                category     = "",
                description  = "",
            )

            yield response.follow(
                relative_url,
                callback  = self.parse_detail,
                cb_kwargs = {"item": partial},
            )

        # ── Pagination ────────────────────────────────────────────────────────
        next_href = response.css("li.next a::attr(href)").get()
        if next_href:
            yield response.follow(next_href, callback=self.parse)

    # ── Step 2: Parse individual book detail pages ────────────────────────────

    def parse_detail(self, response, item):
        """
        Fills in category and description from the book's own page,
        then applies optional filters before yielding the item.
        """
        item["category"] = (
            response.css("ul.breadcrumb li:nth-child(3) a::text").get(default="Unknown")
            .strip()
        )
        item["description"] = (
            response.css("#product_description ~ p::text").get(default="").strip()
        )

        # ── Optional filters (applied AFTER pipeline would run, so raw values) ─
        # Note: pipeline hasn't run yet, so price/rating are still raw strings.
        # We do a quick inline check here so we don't yield items we'd discard.

        # Category filter
        if self.filter_category and self.filter_category != item["category"].lower():
            return

        yield item
