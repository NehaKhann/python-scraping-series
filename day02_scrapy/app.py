"""
Day 2 — Book Price Tracker UI
Run with: streamlit run app.py   (from the day02_scrapy/ directory)

Architecture note:
  Scrapy uses Twisted (its own async framework). Streamlit has its own
  event loop. Running Scrapy directly inside a Streamlit thread causes a
  "ReactorNotRestartable" error on the second run.

  Fix: run Scrapy as a subprocess. Clean separation, no reactor conflicts.
"""

import json
import os
import subprocess
import sys
import time

import pandas as pd
import streamlit as st

# ── Paths ─────────────────────────────────────────────────────────────────────

HERE           = os.path.dirname(os.path.abspath(__file__))
SCRAPY_DIR     = os.path.join(HERE, "booktracker")   # where scrapy.cfg lives
OUTPUT_JSON    = os.path.join(SCRAPY_DIR, "books.json")

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Book Price Tracker",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Book Price Tracker")
st.caption("Powered by Scrapy · books.toscrape.com")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Scrape Settings")

    max_books = st.slider("Max books to scrape", 10, 500, 100, step=10)

    category_input = st.text_input(
        "Filter by category (optional)",
        placeholder="e.g. Mystery, Travel, Science",
        help="Leave empty to scrape all categories",
    )

    st.divider()
    st.caption("**Stack:** Scrapy · Streamlit · pandas")
    st.caption("Day 2 of 14 — Scraping Series")

# ── Session state ─────────────────────────────────────────────────────────────

for key, default in {
    "results":  [],
    "running":  False,
    "finished": False,
    "error":    "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Run button ────────────────────────────────────────────────────────────────

run_btn = st.button(
    "▶ Start Scraping",
    type="primary",
    disabled=st.session_state.running,
)

# ── Scraping logic ────────────────────────────────────────────────────────────

if run_btn:
    st.session_state.results  = []
    st.session_state.running  = True
    st.session_state.finished = False
    st.session_state.error    = ""

    st.divider()
    status  = st.empty()
    spinner = st.empty()

    status.info("🕷️ Spider started — scraping books.toscrape.com...")

    # Build scrapy crawl command
    cmd = [
        sys.executable, "-m", "scrapy", "crawl", "books",
        "-s", f"CLOSESPIDER_ITEMCOUNT={max_books}",
    ]
    if category_input.strip():
        cmd += ["-a", f"category={category_input.strip()}"]

    with spinner.container():
        with st.spinner(f"Scraping up to {max_books} books... (this takes ~30–60s)"):
            try:
                result = subprocess.run(
                    cmd,
                    cwd     = SCRAPY_DIR,
                    capture_output = True,
                    text    = True,
                    timeout = 300,
                )
            except subprocess.TimeoutExpired:
                st.session_state.error   = "Scrape timed out after 5 minutes."
                st.session_state.running  = False
                st.session_state.finished = True
                st.rerun()

    # Read output
    if os.path.exists(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, encoding="utf-8") as f:
                books = json.load(f)
            st.session_state.results = books
        except Exception as e:
            st.session_state.error = f"Failed to read output: {e}"
    else:
        stderr_snippet = result.stderr[-500:] if result.stderr else "No output"
        st.session_state.error = f"books.json not found.\n\nScrapy stderr:\n{stderr_snippet}"

    st.session_state.running  = False
    st.session_state.finished = True
    st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────

if st.session_state.error:
    st.error(st.session_state.error)

elif st.session_state.finished and st.session_state.results:
    books = st.session_state.results
    st.success(f"✅ Scraped **{len(books)} books** from books.toscrape.com")
    st.divider()

    df = pd.DataFrame(books)

    # ── Filters ───────────────────────────────────────────────────────────────
    with st.expander("🔎 Filter results", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
            f_cat = st.selectbox("Category", categories)

        with col2:
            f_min_rating = st.slider("Min rating", 1, 5, 1)

        with col3:
            max_p = float(df["price"].max()) if len(df) else 100.0
            f_max_price = st.slider("Max price (£)", 0.0, max_p, max_p)

    filtered = df.copy()
    if f_cat != "All":
        filtered = filtered[filtered["category"] == f_cat]
    filtered = filtered[filtered["rating"] >= f_min_rating]
    filtered = filtered[filtered["price"] <= f_max_price]

    # ── Metrics ───────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Books shown",       len(filtered))
    m2.metric("Categories",        filtered["category"].nunique())
    m3.metric("Avg price (£)",     f"{filtered['price'].mean():.2f}" if len(filtered) else "—")
    m4.metric("Avg rating",        f"{filtered['rating'].mean():.1f}" if len(filtered) else "—")

    st.divider()

    # ── Charts ────────────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Price distribution")
        price_hist = (
            filtered["price"]
            .value_counts(bins=10, sort=False)
            .reset_index()
        )
        price_hist.columns = ["Price range", "Count"]
        st.bar_chart(filtered["price"], height=200)

    with c2:
        st.subheader("Books per category")
        cat_counts = filtered["category"].value_counts().head(10)
        st.bar_chart(cat_counts, height=200)

    st.divider()

    # ── Table ─────────────────────────────────────────────────────────────────
    display_df = filtered[["title", "category", "price", "rating", "availability"]].copy()
    display_df.columns = ["Title", "Category", "Price (£)", "Rating", "Availability"]
    display_df = display_df.sort_values("Price (£)")
    st.dataframe(display_df, use_container_width=True, height=400)

    st.divider()

    # ── Book cards (cheapest 6) ────────────────────────────────────────────────
    st.subheader("Cheapest books")
    cheapest = filtered.nsmallest(6, "price").to_dict("records")

    for i in range(0, len(cheapest), 3):
        row = cheapest[i:i+3]
        cols = st.columns(3)
        for col, book in zip(cols, row):
            with col:
                with st.container(border=True):
                    st.markdown(f"**{book.get('title', '—')}**")
                    st.markdown(f"📂 {book.get('category', '—')}")
                    st.markdown(f"💰 £{book.get('price', 0):.2f}")
                    st.markdown(f"⭐ {'★' * book.get('rating', 0)}{'☆' * (5 - book.get('rating', 0))}")
                    st.markdown(f"{'✅' if book.get('availability') == 'In stock' else '❌'} {book.get('availability', '—')}")
                    if book.get("url"):
                        st.link_button("View book →", book["url"])

    st.divider()

    # ── Downloads ────────────────────────────────────────────────────────────
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "⬇️ Download JSON",
            data      = json.dumps(filtered.to_dict("records"), indent=2),
            file_name = "books.json",
            mime      = "application/json",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "⬇️ Download CSV",
            data      = filtered.to_csv(index=False),
            file_name = "books.csv",
            mime      = "text/csv",
            use_container_width=True,
        )

elif not st.session_state.running:
    st.info("👈 Set how many books to scrape, then click **▶ Start Scraping**")
    with st.expander("How it works"):
        st.markdown("""
        1. Runs a Scrapy spider as a **subprocess** (avoids Twisted reactor conflicts with Streamlit)
        2. Spider crawls books.toscrape.com — 50 books per page, follows pagination
        3. Detail page fetched per book for category + description
        4. Item pipeline cleans price (£12.99 → 12.99), rating ("Three" → 3), availability
        5. Results saved to `books.json`, loaded into the UI

        **Why subprocess?**
        Scrapy uses Twisted (its own async framework). Running it inside a Streamlit thread
        causes a "ReactorNotRestartable" error on the second scrape. Subprocess sidesteps this entirely.
        """)
