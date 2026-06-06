"""Road Damage Detection page."""

import streamlit as st

from frontend.components.analytics_modules import render_road_damage_module
from frontend.utils import apply_theme, render_city_selector


def render():
    apply_theme()
    city = render_city_selector("road_damage")
    st.markdown('<p class="section-header">Road Damage Detection</p>', unsafe_allow_html=True)
    st.caption("YOLOv8 computer vision — potholes, cracks, severity scoring")
    render_road_damage_module(city, full_page=True)
