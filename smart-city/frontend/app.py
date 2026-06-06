"""Smart City India — main Streamlit application."""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from frontend.pages import ai_analysis, dashboard, parking, reports, road_damage, traffic
from frontend.utils import apply_theme, check_backend, init_session, BACKEND_URL

st.set_page_config(page_title="Smart City India", page_icon="🇮🇳", layout="wide", initial_sidebar_state="expanded")
apply_theme()
init_session()

PAGES = {
    "Dashboard": dashboard,
    "Traffic Analysis": traffic,
    "Smart Parking": parking,
    "Road Damage Detection": road_damage,
    "Real-Time AI Analysis": ai_analysis,
    "Reports": reports,
}

with st.sidebar:
    st.markdown("## 🇮🇳 Smart City India")
    st.caption("AI Urban Analytics Platform")
    st.divider()
    page = st.radio("Navigation", list(PAGES.keys()), label_visibility="collapsed")
    st.divider()
    st.caption("API: " + ("🟢 Online" if check_backend() else "🔴 Offline"))
    if not check_backend():
        st.code("uvicorn backend.main:app --reload", language="bash")

PAGES[page].render()
