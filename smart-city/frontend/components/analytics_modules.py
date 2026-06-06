"""Analytics module renderers — Traffic, Parking, Road Damage."""

import base64
import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from frontend.utils import api_get, api_post, kpi_card


def _plot_layout(fig, height=300):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=height)
    return fig


def _congestion_heatmap(df_z: pd.DataFrame):
    """1×N heatmap — x=zones, y=single row; dimensions always match."""
    zones = df_z["zone"].tolist()
    values = df_z["vehicles"].tolist()
    fig = px.imshow(
        [values],
        x=zones,
        y=["Vehicle Density"],
        labels=dict(x="Zone", y="", color="Vehicles"),
        color_continuous_scale=["#44cc44", "#ffaa00", "#ff4444"],
        title="Congestion Heatmap by Zone",
        aspect="auto",
    )
    return _plot_layout(fig)


def render_traffic_module(city: str, full_page: bool = False):
    data = api_get(f"/traffic/{city}/analytics")
    if not data:
        st.warning("Traffic data unavailable. Click Refresh to load data.")
        return

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card(data["congestion_level"], "Congestion Level", c1)
    kpi_card(f"{data['avg_speed']} km/h", "Average Speed", c2)
    peaks = ", ".join(f"{h}:00" for h in data.get("peak_hours", [])[:3])
    kpi_card(peaks or "—", "Peak Hours", c3)
    kpi_card(f"{data['density_score']}/100", "Density Score", c4)
    fc = data.get("forecast", {})
    kpi_card(fc.get("congestion_level", "—"), "Prediction", c5)

    if full_page and st.button("Refresh Traffic Data", key=f"tr_refresh_{city}"):
        api_post(f"/traffic/{city}/refresh")
        st.rerun()

    df_h = pd.DataFrame(data["hourly_data"])
    df_z = pd.DataFrame(data["zone_data"])

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(_plot_layout(px.line(df_h, x="hour", y="vehicles", title="Hourly Traffic Trend", markers=True, color_discrete_sequence=["#ff9933"])), use_container_width=True)
    with col2:
        if not df_z.empty:
            st.plotly_chart(_congestion_heatmap(df_z), use_container_width=True)

    if full_page:
        col3, col4 = st.columns(2)
        with col3:
            if not df_z.empty:
                st.plotly_chart(_plot_layout(px.bar(df_z, x="zone", y="vehicles", title="Vehicle Density Trend", color="vehicles", color_continuous_scale=["#44cc44", "#ff4444"])), use_container_width=True)
        with col4:
            prob = fc.get("congestion_probability", 0.5) * 100
            gauge = go.Figure(go.Indicator(mode="gauge+number", value=prob, title={"text": "Traffic Forecast (%)"}, gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#ff9933"}}))
            st.plotly_chart(_plot_layout(gauge, 280), use_container_width=True)

        insights = api_get(f"/traffic/{city}/ai-insights")
        if insights:
            st.markdown("#### Traffic Insights (Groq AI)")
            st.markdown(insights.get("insights", ""))


def render_parking_module(city: str, full_page: bool = False):
    data = api_get(f"/parking/{city}/analytics")
    if not data:
        st.warning("Parking data unavailable.")
        return

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(str(data["total_zones"]), "Parking Zones", c1)
    kpi_card(str(data["available_slots"]), "Available Spaces", c2)
    kpi_card(str(data["occupied_slots"]), "Occupied Spaces", c3)
    kpi_card(f"{data['utilization_pct']}%", "Utilization", c4)

    if full_page and st.button("Refresh Parking Data", key=f"pk_refresh_{city}"):
        api_post(f"/parking/{city}/refresh")
        st.rerun()

    lots = pd.DataFrame(data["lots"])
    hourly = pd.DataFrame(data["hourly_data"])
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(_plot_layout(px.pie(lots, names="parking_name", values="occupied_slots", hole=0.45, title="Parking Occupancy", color_discrete_sequence=px.colors.sequential.Oranges_r)), use_container_width=True)
    with col2:
        st.plotly_chart(_plot_layout(px.line(hourly, x="hour", y="utilization", title="Hourly Occupancy Graph", color_discrete_sequence=["#ff9933"])), use_container_width=True)

    if full_page:
        fc = data.get("forecast", {})
        st.markdown(f"**Parking Forecast:** {fc.get('occupancy_pct', 0):.0f}% expected occupancy · Peak **{fc.get('peak_hour', 12)}:00**")

    st.markdown("**AI Recommended Parking Areas**")
    for rec in data.get("recommendations", []):
        st.markdown(f"- {rec}")


def render_road_damage_module(city: str, full_page: bool = False):
    stats = api_get("/road-damage/stats", {"city": city}) or {"total": 0, "pothole_count": 0, "crack_count": 0, "high_severity": 0}

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(str(stats["pothole_count"]), "Potholes", c1)
    kpi_card(str(stats["crack_count"]), "Cracks", c2)
    kpi_card(str(stats["high_severity"]), "High Severity", c3)
    kpi_card(str(stats["total"]), "Total Reports", c4)

    if full_page:
        uploaded = st.file_uploader("Upload Road Image (jpg, jpeg, png)", type=["jpg", "jpeg", "png"], key=f"rd_up_{city}")
        loc = st.text_input("Location", placeholder=f"e.g. NH-44, {city}", key=f"rd_loc_{city}")
        if uploaded and st.button("Run YOLOv8 Detection", key=f"rd_btn_{city}"):
            with st.spinner("Analyzing…"):
                result = api_post("/road-damage/detect", data={"city": city, "location": loc}, files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)})
            if result:
                st.session_state[f"rd_result_{city}"] = result

        result = st.session_state.get(f"rd_result_{city}")
        if result:
            a, b = st.columns(2)
            with a:
                st.metric("Severity", result["severity"])
                st.metric("Confidence", f"{(result.get('confidence') or 0) * 100:.0f}%")
                st.metric("Potholes / Cracks", f"{result.get('pothole_count', 0)} / {result.get('crack_count', 0)}")
            with b:
                img = api_get(f"/road-damage/image/{result['id']}")
                if img and img.get("image_base64"):
                    st.image(Image.open(io.BytesIO(base64.b64decode(img["image_base64"]))), caption="Processed Image", use_container_width=True)

    reports = api_get("/road-damage", {"city": city, "limit": 15})
    if reports:
        st.markdown("**Recent Damage Reports**")
        df = pd.DataFrame(reports)[["damage_type", "severity", "pothole_count", "crack_count", "confidence", "location", "timestamp"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
