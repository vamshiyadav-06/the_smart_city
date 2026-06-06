"""Real-Time AI Analysis — Groq powered."""

from datetime import datetime

import requests
import streamlit as st

from frontend.utils import apply_theme, clear_caches, fetch_ai_analysis, get_backend_url, kpi_card, render_city_selector


def render():
    apply_theme()
    city = render_city_selector("ai")

    st.markdown('<p class="section-header">Real-Time AI Analysis</p>', unsafe_allow_html=True)
    st.caption(f"Comprehensive urban intelligence for **{city}**")

    refresh = st.button("Refresh Analysis", type="primary")
    if refresh:
        clear_caches()
        try:
            resp = requests.get(f"{get_backend_url()}/ai-analysis/{city}", params={"refresh": True}, timeout=90)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            st.error(str(exc))
            return
    else:
        try:
            data = fetch_ai_analysis(city)
        except Exception as exc:
            st.error(str(exc))
            return

    c1, c2, c3 = st.columns(3)
    kpi_card(city, "City", c1)
    kpi_card(f"{data.get('confidence', 0):.0%}", "AI Confidence", c2)
    ts = (data.get("timestamp") or datetime.utcnow().isoformat())[:19].replace("T", " ")
    kpi_card(ts, "Analysis Timestamp", c3)

    if data.get("cached"):
        st.info("Cached analysis (valid 1 hour). Use Refresh for latest.")

    st.markdown('<div class="ai-report">', unsafe_allow_html=True)
    st.markdown(data.get("analysis", ""))
    st.markdown("</div>", unsafe_allow_html=True)
