"""Traffic Analysis page."""

import streamlit as st

from frontend.components.analytics_modules import render_traffic_module
from frontend.utils import api_get, apply_theme, render_city_selector


def render():
    apply_theme()
    city = render_city_selector("traffic")
    st.markdown('<p class="section-header">Traffic Analysis</p>', unsafe_allow_html=True)

    weather = api_get(f"/traffic/{city}/weather")
    if weather:
        w = st.columns(3)
        w[0].metric("Weather", weather.get("condition", "—"))
        w[1].metric("Temperature", f"{weather.get('temperature', 0):.0f}°C")
        w[2].metric("Impact Factor", f"{weather.get('traffic_impact_factor', 1):.1f}x")

    render_traffic_module(city, full_page=True)
