"""
Day 3 — G2 Review Scraper UI
Stack: Streamlit + curl_cffi + pandas
"""

import json
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title = "Day 3 — G2 Review Scraper",
    page_icon  = "⭐",
    layout     = "wide",
)

st.title("⭐ G2 Review Scraper")
st.caption("Day 3 of 14 · Python Scraping Series · Stack: curl_cffi + BeautifulSoup4")

try:
    from scraper import scrape
    SCRAPER_OK = True
except ImportError as e:
    SCRAPER_OK = False
    st.error(f"Missing dependency: {e}. Run: pip install curl_cffi beautifulsoup4")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")
    product   = st.text_input(
        "G2 product slug",
        value="notion",
        placeholder="e.g. notion, slack, figma",
        help="The slug from the G2 URL: g2.com/products/SLUG/reviews"
    )
    max_pages = st.slider("Pages to scrape", min_value=1, max_value=10, value=2,
                          help="~10 reviews per page")
    st.caption("Tip: start with 1 page to verify it works, then go larger.")
    run = st.button("Scrape Reviews", type="primary", disabled=not SCRAPER_OK)

    st.divider()
    st.header("About curl_cffi")
    st.markdown("""
**What it does:**
- Impersonates Chrome's TLS fingerprint
- Gets past standard Cloudflare blocks
- Still just HTTP — no JavaScript

**What it does NOT do:**
- Execute JavaScript (Day 8: Playwright)
- Bypass Cloudflare Bot Management
  *(that's what blocked Trustpilot)*
- Solve CAPTCHAs

**The tool:** `curl_cffi` (Python binding for curl-impersonate)
""")

# ── Session state ─────────────────────────────────────────────────────────────
if "reviews" not in st.session_state:
    st.session_state.reviews = []
if "product" not in st.session_state:
    st.session_state.product = ""

# ── Scrape ────────────────────────────────────────────────────────────────────
if run and SCRAPER_OK:
    if not product.strip():
        st.error("Enter a product slug first (e.g. notion, slack, figma).")
    else:
        slug      = product.strip().lower()
        log_lines = []
        progress_bar = st.progress(0, text="Starting…")
        log_box      = st.empty()

        def log(msg: str):
            log_lines.append(msg)
            log_box.code("\n".join(log_lines[-12:]))

        def on_progress(done, total, label):
            progress_bar.progress(done / max(total, 1), text=label)

        try:
            with st.spinner(f"Scraping {slug} on G2…"):
                data = scrape(
                    product           = slug,
                    max_pages         = max_pages,
                    output_json       = f"reviews_{slug}.json",
                    output_csv        = f"reviews_{slug}.csv",
                    progress_callback = on_progress,
                    log               = log,
                )
            progress_bar.progress(1.0, text="Done!")
            st.session_state.reviews = data
            st.session_state.product = slug

            if data:
                st.success(f"Scraped {len(data)} reviews for {slug}")
            else:
                st.warning("No reviews found. The product slug might be wrong, or G2's page structure changed.")
        except Exception as e:
            st.error(f"Scrape failed: {e}")
            st.exception(e)

# ── Display results ───────────────────────────────────────────────────────────
data = st.session_state.reviews

if data:
    df   = pd.DataFrame(data)
    slug = st.session_state.product

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Reviews", len(df))
    with col2:
        avg = df["rating"].mean()
        st.metric("Average Rating", f"{avg:.1f} ⭐")
    with col3:
        pct_v = df["verified"].sum() / len(df) * 100
        st.metric("Verified", f"{pct_v:.0f}%")

    st.divider()

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        min_rating = st.select_slider("Min rating", options=[1,2,3,4,5], value=1)
    with col_b:
        verified_only = st.checkbox("Verified only")
    with col_c:
        sort_by = st.selectbox("Sort by", ["Date (newest)", "Rating (high→low)", "Rating (low→high)"])

    filtered = df[df["rating"] >= min_rating]
    if verified_only:
        filtered = filtered[filtered["verified"]]

    sort_map = {
        "Date (newest)":     ("date",   False),
        "Rating (high→low)": ("rating", False),
        "Rating (low→high)": ("rating", True),
    }
    col_sort, asc = sort_map[sort_by]
    if col_sort in filtered.columns:
        filtered = filtered.sort_values(col_sort, ascending=asc)

    st.caption(f"Showing {len(filtered)} of {len(df)} reviews")

    st.subheader("Rating Distribution")
    rating_counts = df["rating"].value_counts().sort_index()
    chart_data    = pd.DataFrame({
        "Stars": [f"{'⭐'*i} ({i})" for i in rating_counts.index],
        "Count": rating_counts.values,
    }).set_index("Stars")
    st.bar_chart(chart_data)

    st.subheader("Reviews")
    for _, row in filtered.iterrows():
        stars_str = "⭐" * int(row["rating"]) if row["rating"] else "—"
        badge     = "✅ Verified" if row["verified"] else ""
        with st.expander(f"{stars_str}  {row['title'] or '(no title)'}  {badge}"):
            st.markdown(f"**{row['reviewer']}** · {row['date']}")
            if row["body"]:
                st.write(row["body"])

    st.divider()
    col_j, col_c2 = st.columns(2)
    with col_j:
        st.download_button(
            "Download JSON",
            data      = json.dumps(data, indent=2, ensure_ascii=False),
            file_name = f"reviews_{slug}.json",
            mime      = "application/json",
        )
    with col_c2:
        st.download_button(
            "Download CSV (filtered)",
            data      = filtered.to_csv(index=False),
            file_name = f"reviews_{slug}_filtered.csv",
            mime      = "text/csv",
        )

else:
    st.info("Enter a product slug in the sidebar and click **Scrape Reviews**.")
    st.markdown("""
### How this works

G2.com uses standard Cloudflare protection — it checks your TLS fingerprint during the
connection handshake. Python's `httpx` gets blocked. `curl_cffi` impersonates Chrome's
exact fingerprint and gets through.

```python
from curl_cffi import requests as cffi_requests

session = cffi_requests.Session(impersonate="chrome124")
resp = session.get("https://www.g2.com/products/notion/reviews")
# 200 OK — httpx would get 403
```

G2 also uses Schema.org `itemprop` markup on review cards for SEO, so the review data
is right there in the HTML — no JavaScript execution needed.

**Why not Trustpilot?**
Trustpilot uses Cloudflare *Bot Management* — a completely different tier that runs
JS challenges and behaviour analysis. TLS fingerprinting alone can't bypass it.
That's what Playwright (Day 8) is for.
""")
