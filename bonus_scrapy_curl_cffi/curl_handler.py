"""
Custom Scrapy download handler using curl_cffi directly.

Instead of scrapy-impersonate (which has Twisted reactor conflicts),
we write our own handler that:
  1. Receives each Scrapy request
  2. Runs curl_cffi in a thread (so it doesn't block Scrapy's event loop)
  3. Returns a Scrapy HtmlResponse back to the spider

This is the correct way to use synchronous code inside Twisted/Scrapy:
deferToThread() runs the blocking call in a thread pool.
"""

from scrapy.http import HtmlResponse
from twisted.internet import defer, threads
from curl_cffi import requests as cffi_requests


# Chrome headers — same as Day 3 scraper
CHROME_HEADERS = {
    "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language":           "en-US,en;q=0.9",
    "Cache-Control":             "max-age=0",
    "Sec-Ch-Ua":                 '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile":          "?0",
    "Sec-Ch-Ua-Platform":        '"Windows"',
    "Sec-Fetch-Dest":            "document",
    "Sec-Fetch-Mode":            "navigate",
    "Sec-Fetch-Site":            "none",
    "Sec-Fetch-User":            "?1",
    "Upgrade-Insecure-Requests": "1",
}


class CurlCffiHandler:
    """
    Scrapy download handler backed by curl_cffi.
    Drop-in replacement for Scrapy's default handler on any URL.
    """

    def __init__(self, settings):
        self._timeout = settings.getfloat("DOWNLOAD_TIMEOUT", 15)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def download_request(self, request, spider):
        """
        Scrapy calls this for every request.
        We return a Deferred — Twisted's way of saying "result coming later".
        deferToThread runs the actual HTTP call in a background thread
        so Scrapy's event loop stays unblocked.
        """
        return threads.deferToThread(self._fetch, request, spider)

    def _fetch(self, request, spider):
        """Runs in a background thread. Makes the curl_cffi request."""
        impersonate = request.meta.get("impersonate", "chrome131")

        session = cffi_requests.Session(impersonate=impersonate)

        resp = session.get(
            request.url,
            headers=CHROME_HEADERS,
            timeout=self._timeout,
            allow_redirects=True,
        )

        spider.logger.info(f"curl_cffi → {resp.status_code} {request.url} [{impersonate}]")

        return HtmlResponse(
            url        = resp.url,
            status     = resp.status_code,
            body       = resp.content,
            encoding   = "utf-8",
            request    = request,
        )
