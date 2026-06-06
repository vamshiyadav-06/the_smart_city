"""Reports — PDF and CSV exports."""

import requests
import streamlit as st

from frontend.utils import apply_theme, get_backend_url, get_city, render_city_selector


def _download(endpoint: str, label: str, filename: str, city: str):
    try:
        resp = requests.get(f"{get_backend_url()}{endpoint}", params={"city": city}, timeout=90)
        if resp.status_code == 200:
            st.download_button(label, data=resp.content, file_name=filename, key=label)
        else:
            st.error(f"Failed: {label}")
    except Exception as exc:
        st.error(str(exc))


def render():
    apply_theme()
    city = render_city_selector("reports")
    st.markdown('<p class="section-header">Reports</p>', unsafe_allow_html=True)
    st.caption(f"Exports for **{city}** — traffic, parking, road damage, and AI analysis summary")

    left, right = st.columns(2)
    with left:
        st.markdown("#### CSV Reports")
        _download("/reports/traffic/csv", "Traffic CSV", f"traffic_{city}.csv", city)
        _download("/reports/parking/csv", "Parking CSV", f"parking_{city}.csv", city)
        _download("/reports/damage/csv", "Road Damage CSV", f"damage_{city}.csv", city)
    with right:
        st.markdown("#### PDF Report")
        _download("/reports/full/pdf", "Full PDF Report", f"smart_city_india_{city}.pdf", city)
        st.caption("Includes traffic, parking, road damage analytics, and AI analysis summary.")
