"""
Item pipeline — cleans raw scraped data into usable types.

Raw data from the spider:
  price        → "Â£12.99" or "£12.99"  (encoding quirk on books.toscrape.com)
  rating       → "star-rating Three"     (CSS class, not a number)
  availability → ["In stock", "\n"]      (list with whitespace)

After pipeline:
  price        → 12.99  (float)
  rating       → 3      (int)
  availability → "In stock"
"""


RATING_MAP = {
    "One":   1,
    "Two":   2,
    "Three": 3,
    "Four":  4,
    "Five":  5,
}


class BookTrackerPipeline:
    def process_item(self, item):
        # ── Price ─────────────────────────────────────────────────────────────
        # books.toscrape.com sometimes encodes £ as "Â£" due to a UTF-8 issue
        raw_price = item.get("price", "0")
        clean_price = (
            raw_price
            .replace("Â£", "")
            .replace("£", "")
            .strip()
        )
        try:
            item["price"] = float(clean_price)
        except ValueError:
            item["price"] = 0.0

        # ── Rating ────────────────────────────────────────────────────────────
        # CSS class is "star-rating Three" — extract the word, map to int
        rating_class = item.get("rating", "")
        word = rating_class.replace("star-rating", "").strip()
        item["rating"] = RATING_MAP.get(word, 0)

        # ── Availability ──────────────────────────────────────────────────────
        avail_parts = item.get("availability", [])
        combined = " ".join(avail_parts).strip()
        item["availability"] = "In stock" if "In stock" in combined else "Out of stock"

        # ── Description ───────────────────────────────────────────────────────
        item["description"] = (item.get("description") or "").strip()

        return item
