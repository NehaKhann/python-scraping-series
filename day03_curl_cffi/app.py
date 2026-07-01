"""
Day 3 — Trustpilot Review Scraper UI
Stack: Streamlit + curl_cffi + pandas
"""

import sys
import json
import os
import pandas as pd
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title  = "Day 3 — Trustpilot Scraper",
    page_icon   = "⭐",
    layout      = "wide",
)

st.title("⭐ Trustpilot Review Scraper")
st.caption("Day 3 of 14 · Python Scraping Series · Stack: curl_cffi + BeautifulSoup4")

# ── Import scraper ────────────────────────────────────────────────────────────
try:
    from scraper import scrape
    SCRAPER_OK = True
except ImportError as e:
    SCRAPER_OK = False
    st.error(f"Missing dependency: {e}. Run: pip install curl_cffi beautifulsoup4")

# ── Sidebar — controls ────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")
    company    = st.text_input("Company domain", value="apple.com", placeholder="e.g. airbnb.com")
    max_pages  = st.slider("Pages to scrape", min_value=1, max_value=10, value=2,
                           help="~10 reviews per page")
    st.caption("Tip: start with 1 page to verify it works, then go larger.")

    run = st.button("Scrape Reviews", type="primary", disabled=not SCRAPER_OK)

    st.divider()
    st.header("About curl_cffi")
    st.markdown("""
**What it does:**
- Impersonates Chrome's TLS fingerprint
- Gets past Cloudflare TLS-level blocks
- Still just HTTP — no JavaScript

**What it does NOT do:**
- Execute JavaScript (that's Day 8: Playwright)
- Solve CAPTCHAs
- Bypass login pages

**The tool:** `curl_cffi` (Python binding for curl-impersonate)
""")

# ── Session state ─────────────────────────────────────────────────────────────
if "reviews" not in st.session_state:
    st.session_state.reviews = []
if "company" not in st.session_state:
    st.session_state.company = ""

# ── Scrape on button press ────────────────────────────────────────────────────
if run and SCRAPER_OK:
    if not company.strip():
        st.error("Enter a company domain first.")
    else:
        clean_company = company.strip().lower()
        log_lines     = []
        progress_bar  = st.progress(0, text="Starting scrape…")
        log_box       = st.empty()

        def log(msg: str):
            log_lines.append(msg)
            log_box.code("\n".join(log_lines[-10:]))  # show last 10 lines

        def on_progress(done: int, total: int, label: str):
            pct = done / max(total, 1)
            progress_bar.progress(pct, text=label)

        output_json = f"reviews_{clean_company}.json"
        output_csv  = f"reviews_{clean_company}.csv"

        try:
            with st.spinner(f"Scraping {clean_company}…"):
                data = scrape(
                    company           = clean_company,
                    max_pages         = max_pages,
                    output_json       = output_json,
                    output_csv        = output_csv,
                    progress_callback = on_progress,
                    log               = log,
                )
            progress_bar.progress(1.0, text="Done!")
            st.session_state.reviews = data
            st.session_state.company = clean_company

            if data:
                st.success(f"Scraped {len(data)} reviews from {clean_company}")
            else:
                st.warning("No reviews found. The page structure may have changed — check the HTML and update the selectors.")
        except Exception as e:
            st.error(f"Scrape failed: {e}")
            st.exception(e)

# ── Display results ───────────────────────────────────────────────────────────
data = st.session_state.reviews

if data:
    df = pd.DataFrame(data)
    company_name = st.session_state.company

    # ── Metrics ───────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reviews", len(df))
    with col2:
        avg = df["rating"].mean()
        st.metric("Average Rating", f"{avg:.1f} ⭐")
    with col3:
        pct_verified = df["verified"].sum() / len(df) * 100
        st.metric("Verified", f"{pct_verified:.0f}%")
    with col4:
        countries = df["country"].nunique()
        st.metric("Countries", countries if countries > 1 else "—")

    st.divider()

    # ── Filters ───────────────────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        min_rating = st.select_slider("Min rating", options=[1,2,3,4,5], value=1)
    with col_b:
        verified_only = st.checkbox("Verified only")
    with col_c:
        sort_by = st.selectbox("Sort by", ["Date (newest)", "Rating (high→low)", "Rating (low→high)", "Helpful"])

    filtered = df[df["rating"] >= min_rating]
    if verified_only:
        filtered = filtered[filtered["verified"]]

    sort_map = {
        "Date (newest)":      ("date", False),
        "Rating (high→low)":  ("rating", False),
        "Rating (low→high)":  ("rating", True),
        "Helpful":            ("helpful", False),
    }
    col_sort, asc = sort_map[sort_by]
    if col_sort in filtered.columns:
        filtered = filtered.sort_values(col_sort, ascending=asc)

    st.caption(f"Showing {len(filtered)} of {len(df)} reviews")

    # ── Rating distribution ───────────────────────────────────────────────────
    st.subheader("Rating Distribution")
    rating_counts = df["rating"].value_counts().sort_index()
    chart_data    = pd.DataFrame({
        "Stars": [f"{'⭐'*i} ({i})" for i in rating_counts.index],
        "Count": rating_counts.values,
    }).set_index("Stars")
    st.bar_chart(chart_data)

    # ── Review cards ──────────────────────────────────────────────────────────
    st.subheader("Reviews")
    for _, row in filtered.iterrows():
        stars_str  = "⭐" * int(row["rating"]) if row["rating"] else "—"
        badge      = "✅ Verified" if row["verified"] else ""
        country    = f"🌍 {row['country']}" if row["country"] else ""

        with st.expander(f"{stars_str}  {row['title'] or '(no title)'}  {badge}"):
            meta = f"**{row['reviewer']}** {country} · {row['date']}"
            if row["helpful"]:
                meta += f" · 👍 {row['helpful']}"
            st.markdown(meta)
            if row["body"]:
                st.write(row["body"])

    # ── Export ────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Export")
    col_j, col_c2 = st.columns(2)
    with col_j:
        st.download_button(
            label    = "Download JSON",
            data     = json.dumps(data, indent=2, ensure_ascii=False),
            file_name = f"reviews_{company_name}.json",
            mime     = "application/json",
        )
    with col_c2:
        csv_str = filtered.to_csv(index=False)
        st.download_button(
            label     = "Download CSV (filtered)",
            data      = csv_str,
            file_name = f"reviews_{company_name}_filtered.csv",
            mime      = "text/csv",
        )

else:
    # ── Empty state ───────────────────────────────────────────────────────────
    st.info("Enter a company domain in the sidebar and click **Scrape Reviews** to start.")

    st.markdown("""
### How this works

Most sites block Python scrapers by checking the **TLS handshake** — the cryptographic greeting
your HTTP client sends before the connection is established.

Python's `httpx` sends a fingerprint that looks unmistakably like a bot.
`curl_cffi` impersonates **Chrome's exact TLS fingerprint** — same cipher suites,
same HTTP/2 settings, same header order — so Trustpilot's Cloudflare layer sees
what looks like a real browser.

```python
from curl_cffi import requests as cffi_requests

session = cffi_requests.Session(impersonate="chrome120")
resp = session.get("https://www.trustpilot.com/review/apple.com")
# 200 OK — with httpx you'd get 403
```

**The limit:** curl_cffi is still just HTTP. It cannot run JavaScript.
Trustpilot's initial HTML includes review data in a `<script id="__NEXT_DATA__">` JSON blob
(because it's a Next.js app that does server-side rendering for SEO).
We parse that JSON — no JS execution needed.

For infinite-scroll pages that only load via JS, that's Day 8: Playwright.
""")
