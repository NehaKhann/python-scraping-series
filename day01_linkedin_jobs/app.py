"""
Day 1 — LinkedIn Job Scraper UI
Run with: streamlit run app.py
"""

import asyncio
import json
import threading
import queue
import time
import os
import pandas as pd
import streamlit as st

from scraper import scrape
from locations import (
    all_countries, cities_for, get_geo_id, get_location_string,
    get_reliability, get_reliability_note,
)

# ─── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="LinkedIn Job Scraper",
    page_icon="💼",
    layout="wide",
)

# ─── Header ──────────────────────────────────────────────────────────────────

st.title("💼 LinkedIn Job Scraper")
st.caption("No browser. No Selenium. Uses LinkedIn's internal guest API.")
st.divider()

# ─── Sidebar — Controls ──────────────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Search Settings")

    keyword = st.text_input(
        "Job title / keyword",
        value="Software Engineer",
        placeholder="e.g. Data Engineer, Product Manager",
    )

    st.markdown("**Location**")

    country = st.selectbox(
        "Country",
        options=all_countries(),
        index=all_countries().index("Saudi Arabia"),
    )

    city_options = cities_for(country)
    if city_options:
        city = st.selectbox(
            "City",
            options=["All cities"] + city_options,
        )
        city = "" if city == "All cities" else city
    else:
        city = ""
        if country != "Remote / Worldwide":
            st.caption("No city data for this country — will search country-wide")

    # Build final location values
    location  = get_location_string(country, city)
    geo_id    = get_geo_id(country, city)

    st.caption(f"📍 Searching: **{location}**")
    if geo_id:
        st.caption(f"🔑 GeoID: `{geo_id}`")
    else:
        st.caption("🔑 GeoID: none (Remote search)")

    # Reliability warning
    reliability = get_reliability(country)
    note        = get_reliability_note(country)
    if reliability == "✅":
        st.success(f"✅ Reliable region — results should be accurate.")
    elif reliability == "⚠️":
        st.warning(f"⚠️ Partial support — results may include jobs from other countries. Run `python find_geoid.py \"{country}\"` to verify geoId.")
    elif reliability == "❌":
        st.error(
            f"❌ **LinkedIn's guest API does not reliably support {country}.**\n\n"
            f"You will likely see US/UK jobs instead. "
            f"To scrape {country} jobs, you need LinkedIn's official API or a paid scraping service."
        )

    st.divider()

    max_jobs = st.slider(
        "Max jobs",
        min_value=5,
        max_value=100,
        value=25,
        step=5,
    )

    fetch_details = st.toggle(
        "Fetch full details",
        value=True,
        help="Gets salary, description, seniority level. Slower but richer.",
    )

    st.divider()
    st.caption("**Stack:** httpx · BeautifulSoup4 · Streamlit")
    st.caption("Day 1 of 14 — Scraping Series")

# ─── Session state ────────────────────────────────────────────────────────────

for key, default in {
    "results":          [],
    "logs":             [],
    "running":          False,
    "finished":         False,
    "searched_country": "",   # ← store what country was actually scraped
    "searched_keyword": "",
    "searched_location": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Run button ───────────────────────────────────────────────────────────────

run_btn = st.button(
    "▶ Start Scraping",
    type="primary",
    disabled=st.session_state.running,
    use_container_width=False,
)

# ─── Scraping logic ───────────────────────────────────────────────────────────

if run_btn:
    st.session_state.results           = []
    st.session_state.logs              = []
    st.session_state.running           = True
    st.session_state.finished          = False
    # Save exactly what was searched so mismatch detection is always accurate
    st.session_state.searched_country  = country
    st.session_state.searched_keyword  = keyword
    st.session_state.searched_location = location

    progress_q = queue.Queue()
    log_q      = queue.Queue()
    result_q   = queue.Queue()

    def run_scraper():
        def log(msg):
            log_q.put(str(msg))

        def on_progress(done, total, message):
            progress_q.put((done, total, message))

        output_dir  = os.path.dirname(os.path.abspath(__file__))
        output_json = os.path.join(output_dir, "jobs.json")
        output_csv  = os.path.join(output_dir, "jobs.csv")

        results = asyncio.run(scrape(
            keyword           = keyword,
            location          = location,
            geo_id            = geo_id,
            max_jobs          = max_jobs,
            fetch_details     = fetch_details,
            output_json       = output_json,
            output_csv        = output_csv,
            progress_callback = on_progress,
            log               = log,
        ))
        result_q.put(results)

    thread = threading.Thread(target=run_scraper, daemon=True)
    thread.start()

    # ── Live status UI ────────────────────────────────────────────────────────
    st.divider()

    status_box   = st.empty()
    progress_bar = st.progress(0)
    job_label    = st.empty()

    # Show only the last meaningful log line — no wall of text
    while thread.is_alive() or not result_q.empty():
        # Drain log queue — show only the latest line
        latest_log = None
        while not log_q.empty():
            latest_log = log_q.get_nowait()
        if latest_log:
            status_box.info(f"**{latest_log}**")

        # Update progress bar
        while not progress_q.empty():
            done, total, message = progress_q.get_nowait()
            pct = done / total if total > 0 else 0
            progress_bar.progress(pct)
            job_label.caption(f"({done}/{total}) {message}")

        time.sleep(0.15)

    # Done
    jobs = result_q.get() if not result_q.empty() else []
    st.session_state.results  = jobs
    st.session_state.running  = False
    st.session_state.finished = True

    # Clear the live widgets — replace with a single success message
    status_box.empty()
    job_label.empty()
    progress_bar.empty()

    st.rerun()

# ─── Results ─────────────────────────────────────────────────────────────────

if st.session_state.finished and st.session_state.results:
    jobs = st.session_state.results

    # Use the country that was ACTUALLY searched — not whatever is in the sidebar now
    searched_country   = st.session_state.searched_country
    searched_keyword   = st.session_state.searched_keyword
    searched_location  = st.session_state.searched_location

    # Mismatch detection — check if returned jobs match the searched country
    if searched_country and searched_country != "Remote / Worldwide":
        jobs_with_location = [j for j in jobs if j.get("location")]
        mismatched = [
            j for j in jobs_with_location
            if searched_country.lower() not in j.get("location", "").lower()
        ]

        if jobs_with_location:
            mismatch_pct = len(mismatched) / len(jobs_with_location)
        else:
            mismatch_pct = 0

        if mismatch_pct > 0.4:
            st.error(
                f"❌ **Wrong country results detected.**\n\n"
                f"You searched **{searched_country}** but "
                f"**{len(mismatched)} of {len(jobs_with_location)} jobs** "
                f"are from a different country.\n\n"
                f"**Why this happens:** LinkedIn's guest API is designed for US/UK markets. "
                f"For {searched_country}, it ignores the geoId and returns US/UK jobs instead.\n\n"
                f"**What you can do:**\n"
                f"- Use LinkedIn directly (logged in) to search {searched_country} jobs\n"
                f"- Use a paid service (Apify, BrightData) that supports authenticated scraping\n"
                f"- Run `python find_geoid.py \"{searched_country}\"` to verify the geoId is correct"
            )
        elif mismatch_pct > 0:
            st.warning(
                f"⚠️ **Partial mismatch:** {len(mismatched)}/{len(jobs_with_location)} jobs "
                f"may not be in {searched_country}. Verify results below."
            )
            st.success(f"✅ Scraped **{len(jobs)} jobs** for *{searched_keyword}* in *{searched_location}*")
        else:
            st.success(f"✅ Scraped **{len(jobs)} jobs** for *{searched_keyword}* in *{searched_location}*")
    else:
        st.success(f"✅ Scraped **{len(jobs)} jobs** for *{searched_keyword}* in *{searched_location}*")
    st.divider()

    # ── Filters ──────────────────────────────────────────────────────────────
    with st.expander("🔎 Filter results", expanded=True):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            f_company  = st.text_input("Company", "")
        with fc2:
            f_location = st.text_input("Location", "")
        with fc3:
            type_options = ["All"] + sorted({j.get("employment_type","") for j in jobs if j.get("employment_type")})
            f_type = st.selectbox("Employment type", type_options)

    filtered = jobs
    if f_company:
        filtered = [j for j in filtered if f_company.lower() in j.get("company","").lower()]
    if f_location:
        filtered = [j for j in filtered if f_location.lower() in j.get("location","").lower()]
    if f_type != "All":
        filtered = [j for j in filtered if j.get("employment_type") == f_type]

    # ── Metrics ──────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Jobs found",       len(filtered))
    m2.metric("Unique companies", len({j.get("company","") for j in filtered}))
    m3.metric("With salary",      sum(1 for j in filtered if j.get("pay_range")))
    m4.metric("With description", sum(1 for j in filtered if j.get("description")))

    st.divider()

    # ── Table ─────────────────────────────────────────────────────────────────
    df = pd.DataFrame(filtered)[
        ["title","company","location","date_posted","pay_range","seniority_level","employment_type"]
    ]
    df.columns = ["Title","Company","Location","Date","Salary","Seniority","Type"]
    st.dataframe(df, use_container_width=True, height=380)

    # ── Job cards ─────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Job Cards")

    for i in range(0, min(len(filtered), 10), 2):
        pair = filtered[i:i+2]
        cols = st.columns(2)
        for col, job in zip(cols, pair):
            with col:
                with st.container(border=True):
                    st.markdown(f"### {job.get('title','—')}")
                    st.markdown(f"**🏢 {job.get('company','—')}**")
                    info_parts = []
                    if job.get("location"):       info_parts.append(f"📍 {job['location']}")
                    if job.get("pay_range"):      info_parts.append(f"💰 {job['pay_range']}")
                    if job.get("seniority_level"):info_parts.append(f"📊 {job['seniority_level']}")
                    if job.get("employment_type"):info_parts.append(f"⏱️ {job['employment_type']}")
                    if job.get("date_posted"):    info_parts.append(f"📅 {job['date_posted']}")
                    for part in info_parts:
                        st.markdown(part)
                    if job.get("job_url"):
                        st.link_button("View on LinkedIn →", job["job_url"])
                    if job.get("description"):
                        with st.expander("Description"):
                            desc = job["description"]
                            st.text(desc[:600] + "..." if len(desc) > 600 else desc)

    # ── Downloads ─────────────────────────────────────────────────────────────
    st.divider()
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "⬇️ Download JSON",
            data=json.dumps(filtered, indent=2, ensure_ascii=False),
            file_name=f"jobs_{keyword.replace(' ','_')}_{country}.json",
            mime="application/json",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "⬇️ Download CSV",
            data=pd.DataFrame(filtered).to_csv(index=False),
            file_name=f"jobs_{keyword.replace(' ','_')}_{country}.csv",
            mime="text/csv",
            use_container_width=True,
        )

elif st.session_state.finished and not st.session_state.results:
    st.warning(f"No jobs found for **{keyword}** in **{location}**. Try a broader keyword or a different country.")

elif not st.session_state.running:
    st.info("👈 Set your keyword and location in the sidebar, then click **▶ Start Scraping**")
    with st.expander("How it works"):
        st.markdown("""
        1. Calls LinkedIn's internal guest API to collect job cards (25 per page)
        2. Fetches each job's detail page for salary, description, and seniority
        3. Uses random delays (2–4s) and retry logic to avoid 429 rate limits
        4. Exports clean JSON + CSV automatically

        **Why some locations return fewer jobs:**
        LinkedIn's guest API is most reliable for US/UK markets.
        For Middle East and South Asia, this scraper uses LinkedIn's internal
        `geoId` codes which significantly improves results.
        Login-required jobs and salary-undisclosed listings are not accessible.
        """)
