"""Smart City India — shared frontend utilities."""

from typing import Any, Optional

import requests
import streamlit as st

BACKEND_URL = st.secrets["BACKEND_URL"].rstrip("/")

CITIES = [
    "Hyderabad",
    "Bengaluru",
    "Chennai",
    "Mumbai",
    "Delhi",
    "Kolkata",
    "Pune",
    "Ahmedabad",
    "Visakhapatnam",
    "Vijayawada",
    "Tirupati",
    "Warangal",
]

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    background: linear-gradient(160deg,#080810 0%,#12121f 45%,#0d1b2a 100%);
    font-family:'Inter',sans-serif;
    color:#e8e8f0;
}

[data-testid="stSidebar"] {
    background:#0e0e18;
    border-right:1px solid #2a2a3d;
}

.hero-title {
    font-size:2.1rem;
    font-weight:700;
    color:#ff9933;
    margin:0 0 .25rem 0;
}

.hero-sub {
    color:#9a9ab0;
    margin-bottom:1.25rem;
}

.kpi-card {
    background:linear-gradient(145deg,#161622,#1e1e2e);
    border:1px solid #333350;
    border-radius:12px;
    padding:1rem;
    text-align:center;
}

.kpi-value {
    font-size:1.45rem;
    font-weight:700;
    color:#ff9933;
    margin:0;
}

.kpi-label {
    font-size:.72rem;
    color:#8888a0;
    text-transform:uppercase;
    letter-spacing:.4px;
    margin-top:.35rem;
}

.city-info {
    background:#161622;
    border-left:4px solid #ff9933;
    padding:1rem 1.2rem;
    border-radius:0 10px 10px 0;
    margin:.75rem 0;
}

.section-header {
    font-size:1.35rem;
    font-weight:600;
    color:#f0f0f8;
    border-bottom:2px solid #ff993333;
    padding-bottom:.35rem;
    margin:1rem 0;
}

.ai-report {
    background:#161622;
    border:1px solid #333350;
    border-radius:12px;
    padding:1.25rem 1.5rem;
    line-height:1.75;
}

div[data-baseweb="select"] > div {
    background:#161622 !important;
    border-color:#333350 !important;
}

div[data-baseweb="select"] span {
    color:#e8e8f0 !important;
}

ul[role="listbox"] {
    background:#161622 !important;
}

ul[role="listbox"] li {
    color:#e8e8f0 !important;
    background:#161622 !important;
}

ul[role="listbox"] li:hover {
    background:#252538 !important;
    color:#ff9933 !important;
}

.stButton > button {
    background:linear-gradient(90deg,#ff9933,#e67e22);
    color:#0a0a10 !important;
    font-weight:600;
    border:none;
    border-radius:8px;
}

footer,
#MainMenu {
    visibility:hidden;
    height:0;
}
</style>
"""


def apply_theme():
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def init_session():
    defaults = {
        "city": "Hyderabad",
        "dash_module": "Traffic Analysis",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_city() -> str:
    return st.session_state.get("city", "Hyderabad")


def render_city_selector(location: str = "main") -> str:
    """Single city dropdown."""
    init_session()

    current_city = st.session_state.get("city", "Hyderabad")

    idx = CITIES.index(current_city) if current_city in CITIES else 0

    city = st.selectbox(
        "Select Indian City",
        CITIES,
        index=idx,
        key=f"city_{location}",
    )

    if city != current_city:
        st.session_state.city = city
        clear_caches()

    return city


def clear_caches():
    api_get_cached.clear()
    fetch_ai_analysis.clear()


def kpi_card(value: str, label: str, col):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <p class="kpi-value">{value}</p>
                <p class="kpi-label">{label}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


@st.cache_data(ttl=300, show_spinner=False)
def api_get_cached(endpoint: str, params: Optional[tuple] = None) -> Any:
    response = requests.get(
        f"{BACKEND_URL}{endpoint}",
        params=dict(params) if params else None,
        timeout=45,
    )

    response.raise_for_status()

    return response.json()


def api_get(endpoint: str, params: Optional[dict] = None) -> Any:
    try:
        key = tuple(sorted((params or {}).items()))

        return api_get_cached(
            endpoint,
            key if key else None,
        )

    except Exception as exc:
        st.error(f"API error: {exc}")
        return None


def api_post(
    endpoint: str,
    data: Optional[dict] = None,
    files: Optional[dict] = None,
) -> Any:
    try:
        if files:
            response = requests.post(
                f"{BACKEND_URL}{endpoint}",
                files=files,
                data=data,
                timeout=90,
            )
        else:
            response = requests.post(
                f"{BACKEND_URL}{endpoint}",
                json=data,
                timeout=60,
            )

        response.raise_for_status()

        clear_caches()

        return response.json()

    except Exception as exc:
        st.error(f"API error: {exc}")
        return None


@st.cache_data(ttl=3600, show_spinner="Generating AI analysis...")
def fetch_ai_analysis(city: str) -> Any:
    response = requests.get(
        f"{BACKEND_URL}/ai-analysis/{city}",
        timeout=90,
    )

    response.raise_for_status()

    return response.json()


def check_backend() -> bool:
    try:
        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=5,
        )

        return response.status_code == 200

    except Exception:
        return False