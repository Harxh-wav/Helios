import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import plotly.express as px

from pvgis_client import fetch_monthly_ghi

st.set_page_config(page_title="Solar Radiation Finder", layout="wide")

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def geocode(query: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "addressdetails": 1, "limit": 8}
    headers = {"User-Agent": "solar-ghi-college-project/1.0 (educational)"}
    r = requests.get(url, params=params, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()

def parse_int_or_none(s: str):
    s = s.strip()
    return int(s) if s else None

@st.cache_data(show_spinner=False)
def cached_fetch(lat, lon, sy, ey):
    return fetch_monthly_ghi(lat, lon, startyear=sy, endyear=ey)

st.markdown(
    """
    <style>
      .app-hero {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: #f8fafc;
        padding: 24px 28px;
        border-radius: 18px;
        margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.2);
        animation: fadeUp 600ms ease-out;
      }
      .app-hero h1 {
        margin: 0;
        font-size: 2.2rem;
        letter-spacing: 0.5px;
      }
      .app-hero p {
        margin: 6px 0 0 0;
        font-size: 0.9rem;
        color: #cbd5f5;
      }
      .section-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 16px 18px;
        border-radius: 16px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
      }
      @keyframes fadeUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
    </style>
    <div class="app-hero">
      <h1>☀️ <strong>Helios</strong></h1>
      <p>by Harsh — Solar radiation insights in a cleaner, calmer layout.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Search a place, adjust settings, and get monthly global solar radiation (GHI).")

tab_overview, tab_about = st.tabs(["Overview", "About"])

with tab_overview:
    # Session state defaults
    if "lat" not in st.session_state:
        st.session_state.lat = 28.6139
    if "lon" not in st.session_state:
        st.session_state.lon = 77.2090
    if "zoom" not in st.session_state:
        st.session_state.zoom = 6
    if "results" not in st.session_state:
        st.session_state.results = []

    # Layout
    left, right = st.columns([1.05, 1])

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📍 Location")
        query = st.text_input("Search place (e.g., New Delhi, Jaipur, Chennai, IIT Bombay)", value="")
        search = st.button("Search", use_container_width=True)

        if search and query.strip():
            try:
                st.session_state.results = geocode(query.strip())
            except Exception as e:
                st.error(f"Search failed: {e}")

        results = st.session_state.get("results", [])
        if results:
            labels = []
            for r in results:
                name = r.get("display_name", "Unknown")
                labels.append(name)
            picked = st.selectbox("Select result", labels)
            r = results[labels.index(picked)]
            st.session_state.lat = float(r["lat"])
            st.session_state.lon = float(r["lon"])
            st.session_state.zoom = 10

        st.write(f"**Selected:** lat={st.session_state.lat:.6f}, lon={st.session_state.lon:.6f}")
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("🗺️ Map (optional)", expanded=False):
            m = folium.Map(
                location=[st.session_state.lat, st.session_state.lon],
                zoom_start=st.session_state.zoom,
                tiles="CartoDB positron",
            )
            folium.CircleMarker(
                [st.session_state.lat, st.session_state.lon],
                radius=6,
                color="#2563eb",
                fill=True,
                fill_opacity=0.9,
                tooltip="Selected location",
            ).add_to(m)

            map_out = st_folium(m, height=360, width=None)
            if map_out and map_out.get("last_clicked"):
                st.session_state.lat = float(map_out["last_clicked"]["lat"])
                st.session_state.lon = float(map_out["last_clicked"]["lng"])

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("⚙️ Settings")
        units = st.selectbox("Units", ["kWh/m²/month", "kWh/m²/day", "MJ/m²/day"], index=0)
        month = st.selectbox("Highlight month", ["All"] + MONTHS, index=0)
        with st.expander("Advanced: Year range", expanded=False):
            sy = st.text_input("Start year (optional)", value="")
            ey = st.text_input("End year (optional)", value="")

        run = st.button("Calculate", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📊 Results")

    if run:
        try:
            starty = parse_int_or_none(sy)
            endy = parse_int_or_none(ey)

            with st.spinner("Fetching PVGIS data..."):
                res = cached_fetch(st.session_state.lat, st.session_state.lon, starty, endy)

            df = res.climatology.copy()
            df["month_name"] = df["month"].apply(lambda m: MONTHS[m-1])

            if units == "kWh/m²/month":
                col = "ghi_kwh_m2_month"
                label = "GHI (kWh/m²/month)"
            elif units == "kWh/m²/day":
                col = "ghi_kwh_m2_day"
                label = "GHI (kWh/m²/day)"
            else:
                col = "ghi_mj_m2_day"
                label = "GHI (MJ/m²/day)"

            # Highlight selected month
            if month != "All":
                mi = MONTHS.index(month) + 1
                val = float(df.loc[df["month"] == mi, col].iloc[0])
                st.metric(month, f"{val:.3f} ({label})")

            st.dataframe(
                df[["month_name", col]].rename(columns={"month_name":"Month", col:label}),
                width="stretch"
            )

            fig = px.line(
                df,
                x="month_name",
                y=col,
                markers=True,
                height=260,
                width=420,
                labels={"month_name": "Month", col: label},
            )
            fig.update_traces(line={"color": "#2563eb"}, marker={"size": 7})
            fig.update_layout(
                margin={"l": 40, "r": 20, "t": 20, "b": 40},
                transition={"duration": 500},
            )
            st.plotly_chart(fig, use_container_width=False)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, "monthly_ghi.csv", "text/csv")

        except Exception as e:
            st.error(str(e))
    else:
        st.info("Search a place or click the map, then press **Calculate**.")

with tab_about:
    st.subheader("About this app")

    st.write(
        "This application estimates monthly global solar radiation (GHI) "
        "for any location using long-term meteorological data."
    )

    st.markdown(
        """
        **Data Source**
        - PVGIS MRcalc API
        - Dataset: PVGIS-ERA5 (ERA5 reanalysis)

        **Method**
        - Monthly global horizontal irradiation `H(h)_m` (kWh/m²/month)
        - Long-term monthly averages computed across available years
        - Daily averages and MJ values derived for convenience

        **Use Case**
        - Academic projects
        - Preliminary solar resource assessment
        """
    )
