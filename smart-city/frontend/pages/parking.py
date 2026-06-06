"""Smart Parking page."""

import streamlit as st

from frontend.components.analytics_modules import render_parking_module
from frontend.utils import apply_theme, render_city_selector


def render():
    apply_theme()
    city = render_city_selector("parking")
    st.markdown('<p class="section-header">Smart Parking</p>', unsafe_allow_html=True)
    render_parking_module(city, full_page=True)
