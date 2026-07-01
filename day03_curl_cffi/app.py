"""
Day 3 — curl_cffi TLS Fingerprint Demo
Target: scrapingcourse.com/cloudflare-challenge
"""

import json
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title = "Day 3 — curl_cffi Demo",
    page_icon  = "🔒",
    layout     = "wide",
)

st.title("🔒 Cloudflare Bypass with curl_cffi")
st.caption("Day 3 of 14 · Python Scraping Series · Stack: curl_cffi + BeautifulSoup4")

try:
    from scraper import scrape
    SCRAPER_OK = True
except ImportError as e:
    SCRAPER_OK = False
    st.error(f"Missing dependency: {e}. Run: pip install curl_cffi beautifulsoup4 httpx")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("What this demos")
    st.markdown("""
**Target site:** scrapingcourse.com/cloudflare-challenge

A site protected by real Cloudflare — specifically designed to demonstrate TLS fingerprint bypass.

---
**httpx** → 403 Forbidden
*(Python's TLS fingerprint = detected as bot)*

**curl_cffi** → 200 OK
*(Impersonates Chrome's exact TLS fingerprint)*

---
**What curl_cffi does:**
- Bypasses standard Cloudflare (TLS check)

**What it does NOT do:**
- Execute JavaScript
- Bypass Cloudflare Bot Management
  *(Trustpilot + G2 use this — even a fresh IP gets blocked)*
- Bypass CAPTCHAs
""")

    run = st.button("Run Demo", type="primary", disabled=not SCRAPER_OK)

# ── Session state ─────────────────────────────────────────────────────────────
if "products" not in st.session_state:
    st.session_state.products = []
if "ran" not in st.session_state:
    st.session_state.ran = False

# ── Run scraper ───────────────────────────────────────────────────────────────
if run and SCRAPER_OK:
    log_lines    = []
    progress_bar = st.progress(0, text="Starting...")
    log_box      = st.empty()

    def log(msg: str):
        log_lines.append(msg)
        log_box.code("\n".join(log_lines[-15:]))

    def on_progress(done, total, label):
        progress_bar.progress(1.0, text=label)

    try:
        with st.spinner("Running curl_cffi demo..."):
            data = scrape(
                output_json       = "products.json",
                output_csv        = "products.csv",
                progress_callback = on_progress,
                log               = log,
            )
        st.session_state.products = data
        st.session_state.ran      = True

        if data:
            st.success(f"✅ Scraped {len(data)} products — curl_cffi bypassed Cloudflare")
        else:
            st.warning("curl_cffi was also blocked. The site may have upgraded protection beyond TLS fingerprinting.")
    except Exception as e:
        st.error(f"Error: {e}")
        st.exception(e)

# ── Results ───────────────────────────────────────────────────────────────────
data = st.session_state.products

if data:
    df = pd.DataFrame(data)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Products scraped", len(df))
    with col2:
        prices = df["price"].str.replace(r"[^\d.]", "", regex=True)
        prices = pd.to_numeric(prices, errors="coerce")
        st.metric("Avg price", f"${prices.mean():.2f}" if not prices.isna().all() else "—")

    st.divider()
    st.subheader("Products")
    st.dataframe(df[["name", "price"]], use_container_width=True)

    st.download_button(
        "Download JSON",
        data      = json.dumps(data, indent=2),
        file_name = "products.json",
        mime      = "application/json",
    )

elif st.session_state.ran:
    st.info("No products found. Click Run Demo to try again.")

else:
    # Empty state — explain the concept
    st.divider()
    st.subheader("How TLS Fingerprinting Works")

    col_a, col_b = st.columns(2)

    with col_a:
        st.error("❌ httpx — Blocked")
        st.code("""import httpx

resp = httpx.get(
    "https://www.scrapingcourse.com"
    "/cloudflare-challenge"
)
print(resp.status_code)
# 403 Forbidden
# Cloudflare detects Python's
# TLS fingerprint""", language="python")

    with col_b:
        st.success("✅ curl_cffi — Works")
        st.code("""from curl_cffi import requests

session = requests.Session(
    impersonate="chrome124"
)
resp = session.get(
    "https://www.scrapingcourse.com"
    "/cloudflare-challenge"
)
print(resp.status_code)
# 200 OK""", language="python")

    st.info("""
**What happens during a TLS handshake:**

Before any webpage loads, your client and the server negotiate how to encrypt the connection.
Your client announces which cipher suites it supports — in a specific order. This creates a fingerprint.

Python's `httpx` has a fingerprint Cloudflare recognises as a bot.
`curl_cffi` sends Chrome's exact fingerprint — same cipher suites, same order, same HTTP/2 settings.
Cloudflare sees Chrome. You're in.

**Why Trustpilot and G2 still blocked us:**
Those sites use Cloudflare *Bot Management* — a paid enterprise tier that also runs JavaScript
challenges and behaviour analysis on top of TLS. curl_cffi can't execute JavaScript.
Even a fresh IP (mobile hotspot) gets blocked because the JS challenge fails.
That requires a real browser — Playwright (Day 8).
""")
