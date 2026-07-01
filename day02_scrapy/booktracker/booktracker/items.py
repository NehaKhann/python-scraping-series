import scrapy


class BookItem(scrapy.Item):
    title        = scrapy.Field()
    price        = scrapy.Field()   # float after pipeline (e.g. 12.99)
    rating       = scrapy.Field()   # int after pipeline (1–5)
    availability = scrapy.Field()   # "In stock" or "Out of stock"
    category     = scrapy.Field()
    description  = scrapy.Field()
    url          = scrapy.Field()
