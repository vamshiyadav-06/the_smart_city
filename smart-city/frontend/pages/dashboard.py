"""Dashboard — city overview and analytics module selector."""

import streamlit as st

from frontend.components.analytics_modules import (
    render_parking_module,
    render_road_damage_module,
    render_traffic_module,
)
from frontend.utils import (
    api_get,
    apply_theme,
    display_city_images,
    kpi_card,
    render_city_selector,
)


def render():
    apply_theme()

    city = render_city_selector("dashboard")

    st.markdown(
        '<p class="hero-title">Welcome to Smart City India</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="hero-sub">AI-Powered Urban Intelligence and Monitoring Platform</p>',
        unsafe_allow_html=True,
    )

    meta = api_get(f"/cities/{city}")

    if meta:
        st.markdown(
            f"""
            <div class="city-info">
                <strong>{city}</strong> · {meta["state"]} · Population {meta["population"]}
                <br>
                <em>Famous for:</em> {meta["famous_for"]}
                <br>
                {meta["description"]}
            </div>
            """,
            unsafe_allow_html=True,
        )
        display_city_images(city, meta.get("image_paths"))

    overview = api_get(f"/cities/{city}/overview")

    if overview:
        st.markdown(
            '<p class="section-header">City Overview</p>',
            unsafe_allow_html=True,
        )

        row1 = st.columns(3)

        kpi_card(
            overview["population"],
            "Population",
            row1[0],
        )

        kpi_card(
            overview["area"],
            "Area",
            row1[1],
        )

        kpi_card(
            overview["climate_summary"][:28] + "…",
            "Climate Summary",
            row1[2],
        )

        row2 = st.columns(3)

        kpi_card(
            overview["major_industries"][:28] + "…",
            "Major Industries",
            row2[0],
        )

        kpi_card(
            overview["tourist_importance"][:28] + "…",
            "Tourist Importance",
            row2[1],
        )

        kpi_card(
            overview["transport_infrastructure"][:28] + "…",
            "Transport Infrastructure",
            row2[2],
        )

    st.divider()

    module = st.selectbox(
        "Choose Analytics Module",
        [
            "Traffic Analysis",
            "Smart Parking",
            "Road Damage Analysis",
        ],
        key="dash_module",
    )

    st.markdown(
        f'<p class="section-header">{module}</p>',
        unsafe_allow_html=True,
    )

    if module == "Traffic Analysis":
        render_traffic_module(city, full_page=False)

    elif module == "Smart Parking":
        render_parking_module(city, full_page=False)

    else:
        render_road_damage_module(city, full_page=False)