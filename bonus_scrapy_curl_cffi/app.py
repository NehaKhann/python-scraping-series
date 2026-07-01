"""
Bonus Project — Scrapy + curl_cffi via scrapy-impersonate
Streamlit UI
"""

import json
import subprocess
import sys
import pandas as pd
import streamlit as st
from pathlib import Path

HERE = Path(__file__).parent

st.set_page_config(
    page_title="Bonus — Scrapy + curl_cffi",
    page_icon="🕷️",
    layout="wide",
)

st.title("🕷️ Scrapy + curl_cffi: The Power Duo")
st.caption("Bonus Project · Python Scraping Series · Stack: Scrapy + scrapy-impersonate + curl_cffi")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("What this demos")
    st.markdown("""
**Day 2 — Scrapy**
Great for crawling many pages automatically.
Bad with Cloudflare (blocked at TLS layer).

**Day 3 — curl_cffi**
Bypasses Cloudflare TLS fingerprinting.
No built-in crawling — you manage everything manually.

**Bonus — Both together**
`scrapy-impersonate` replaces Scrapy's HTTP engine
with curl_cffi. Scrapy manages the crawl.
curl_cffi handles the TLS fingerprint.

---
**Target:** scrapingcourse.com/cloudflare-challenge
*(real Cloudflare, standard tier)*
""")
    run = st.button("▶ Run Spider", type="primary")

# ── Session state ─────────────────────────────────────────────────────────────
if "products" not in st.session_state:
    st.session_state.products = []
if "ran" not in st.session_state:
    st.session_state.ran = False
if "error" not in st.session_state:
    st.session_state.error = ""

# ── Run spider ────────────────────────────────────────────────────────────────
if run:
    with st.spinner("Scrapy spider running with Chrome TLS fingerprint..."):
        result = subprocess.run(
            [sys.executable, "run_spider.py"],
            capture_output=True,
            text=True,
            cwd=str(HERE),
        )

    output_file = HERE / "products.json"
    st.session_state.ran   = True
    st.session_state.error = ""

    if output_file.exists():
        try:
            data = json.loads(output_file.read_text(encoding="utf-8"))
            st.session_state.products = data
            if data:
                st.success(f"✅ Scraped {len(data)} products — Scrapy + curl_cffi worked")
            else:
                st.warning("Spider ran but found no products. The page structure may have changed.")
        except json.JSONDecodeError:
            st.session_state.error = "Output file exists but could not be parsed."
            st.error(st.session_state.error)
    else:
        err = result.stderr or "Spider produced no output file."
        st.session_state.error = err
        st.error("Spider failed.")
        st.code(err[:2000])

# ── Results ───────────────────────────────────────────────────────────────────
data = st.session_state.products

if data:
    df = pd.DataFrame(data)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Products scraped", len(df))
    with col2:
        prices = df["price"].str.replace(r"[^\d.]", "", regex=True)
        prices = pd.to_numeric(prices, errors="coerce")
        avg = prices.mean()
        st.metric("Avg price", f"${avg:.2f}" if not pd.isna(avg) else "—")
    with col3:
        pages = df["page"].nunique() if "page" in df.columns else 1
        st.metric("Pages crawled", pages)

    st.divider()
    st.subheader("Products")

    display_cols = [c for c in ["name", "price", "page"] if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True)

    st.download_button(
        "Download JSON",
        data      = json.dumps(data, indent=2),
        file_name = "products.json",
        mime      = "application/json",
    )

elif st.session_state.ran and not st.session_state.error:
    st.info("No products returned. Try running again.")

else:
    # ── Empty state — explain the concept ────────────────────────────────────
    st.divider()
    st.subheader("The Problem: Scrapy alone gets blocked")

    col_a, col_b = st.columns(2)

    with col_a:
        st.error("❌ Scrapy alone — 403 Forbidden")
        st.code("""import scrapy

class ProductsSpider(scrapy.Spider):
    # Scrapy's default: Twisted HTTP client
    # Twisted fingerprint = Python bot
    # Cloudflare blocks it immediately

    def start_requests(self):
        yield scrapy.Request(
            "https://www.scrapingcourse.com"
            "/cloudflare-challenge"
        )
        # Status: 403 Forbidden ❌""", language="python")

    with col_b:
        st.success("✅ Scrapy + scrapy-impersonate — 200 OK")
        st.code("""import scrapy

class ProductsSpider(scrapy.Spider):
    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_impersonate"
                     ".ImpersonateDownloadHandler",
        },
        "TWISTED_REACTOR":
            "twisted.internet"
            ".asyncioreactor.AsyncioSelectorReactor",
    }

    def start_requests(self):
        yield scrapy.Request(
            "https://www.scrapingcourse.com"
            "/cloudflare-challenge",
            meta={"impersonate": "chrome124"},
        )
        # Status: 200 OK ✅""", language="python")

    st.divider()
    st.subheader("What changed — just two things")

    st.markdown("""
**1. Add `custom_settings` to the spider:**
```python
custom_settings = {
    "DOWNLOAD_HANDLERS": {
        "http":  "scrapy_impersonate.ImpersonateDownloadHandler",
        "https": "scrapy_impersonate.ImpersonateDownloadHandler",
    },
    "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
}
```
This replaces Scrapy's HTTP client with curl_cffi. Every request now uses Chrome's TLS fingerprint.

**2. Add `meta={"impersonate": "chrome124"}` to each request:**
```python
yield scrapy.Request(url, meta={"impersonate": "chrome124"})
```
This tells curl_cffi which browser version to impersonate.

Everything else — pagination, retries, pipelines, output — stays exactly the same as normal Scrapy.
""")

    st.info("""
**Why not just use curl_cffi alone like Day 3?**

curl_cffi handles one URL at a time. You write the loop, the pagination logic, the retry logic yourself.
Scrapy handles all of that automatically — you just write what to extract.
When a site has 50+ pages behind Cloudflare, you want both.
""")
