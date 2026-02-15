import streamlit as st
import pandas as pd
import altair as alt
import requests
import folium
import calendar

from streamlit_folium import st_folium
from pvgis_client import fetch_monthly_ghi
from nasa_power_client import fetch_monthly_climate

st.set_page_config(page_title="Helios · Solar & Climate Studio", layout="wide")

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

@st.cache_data(show_spinner=False)
def cached_fetch_climate(lat, lon, sy, ey):
    return fetch_monthly_climate(lat, lon, startyear=sy, endyear=ey)

# ---------- UI HEADER (V1 STYLE) ----------
st.markdown(
    """
    <style>
      .stApp { background: radial-gradient(circle at 15% -10%, #dbeafe 0%, #f8fafc 35%, #f8fafc 100%); }
      .app-hero {
        background: linear-gradient(125deg, #0f172a 0%, #1e293b 45%, #1d4ed8 100%);
        color: #f8fafc;
        padding: 28px;
        border-radius: 20px;
        margin-bottom: 14px;
        box-shadow: 0 14px 38px rgba(15, 23, 42, 0.24);
        animation: fadeUp 600ms ease-out;
      }
      .app-hero h1 { margin: 0; font-size: 2.1rem; letter-spacing: .3px; }
      .app-hero p { margin: 6px 0 0 0; color: #dbeafe; font-size: 0.95rem; }
      .app-chip {
        display: inline-block;
        padding: 4px 10px;
        border: 1px solid rgba(191, 219, 254, .45);
        border-radius: 999px;
        font-size: .76rem;
        margin-bottom: 10px;
        color: #bfdbfe;
        letter-spacing: .04em;
      }
      .section-card {
        background: rgba(255, 255, 255, .92);
        border: 1px solid #e2e8f0;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
        backdrop-filter: blur(3px);
      }
      .kpi-card {
        background: linear-gradient(150deg, #eff6ff, #f8fafc);
        border: 1px solid #bfdbfe;
        border-radius: 14px;
        padding: 14px;
      }
      .kpi-label { color: #475569; font-size: .8rem; }
      .kpi-value { color: #0f172a; font-size: 1.1rem; font-weight: 600; }
      @keyframes fadeUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
    </style>
    <div class="app-hero">
      <span class="app-chip">SOLAR ANALYTICS DASHBOARD</span>
      <h1>☀️ <strong>Helios Studio</strong></h1>
      <p>Professional-grade monthly solar radiation and climate insights for any location.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Search a place, fine-tune data preferences, and generate polished solar + climate reports instantly.")

tab_overview, tab_about = st.tabs(["Overview", "About"])

# ================== OVERVIEW TAB ==================
with tab_overview:
    if "lat" not in st.session_state:
        st.session_state.lat = 28.6139
    if "lon" not in st.session_state:
        st.session_state.lon = 77.2090
    if "zoom" not in st.session_state:
        st.session_state.zoom = 6
    if "results" not in st.session_state:
        st.session_state.results = []

    m1, m2, m3 = st.columns(3)
    m1.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Latitude</div><div class="kpi-value">{st.session_state.lat:.4f}</div></div>',
        unsafe_allow_html=True,
    )
    m2.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Longitude</div><div class="kpi-value">{st.session_state.lon:.4f}</div></div>',
        unsafe_allow_html=True,
    )
    m3.markdown(
        '<div class="kpi-card"><div class="kpi-label">Data Sources</div><div class="kpi-value">PVGIS + NASA POWER</div></div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 1])

    # ---------- LEFT: LOCATION ----------
    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📍 Location")

        query = st.text_input("Search place", value="", placeholder="e.g., New Delhi, Jaipur, IIT Bombay")
        search = st.button("Search", use_container_width=True)

        if search and query.strip():
            try:
                st.session_state.results = geocode(query.strip())
            except Exception as e:
                st.error(f"Search failed: {e}")

        results = st.session_state.get("results", [])
        if results:
            labels = [r.get("display_name", "Unknown") for r in results]
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
            ).add_to(m)

            map_out = st_folium(m, height=360, width=None)
            if map_out and map_out.get("last_clicked"):
                st.session_state.lat = float(map_out["last_clicked"]["lat"])
                st.session_state.lon = float(map_out["last_clicked"]["lng"])

    # ---------- RIGHT: SETTINGS ----------
    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("⚙️ Settings")

        # what to compute (app-like toggles)
        c1, c2, c3 = st.columns(3)
        with c1:
            do_solar = st.toggle("Solar (GHI)", value=True)
        with c2:
            do_humidity = st.toggle("Humidity", value=True)
        with c3:
            do_rain = st.toggle("Rainfall", value=True)

        st.divider()

        # solar settings
        units = st.selectbox("Solar units", ["kWh/m²/month", "kWh/m²/day", "MJ/m²/day"], index=0, disabled=not do_solar)
        month = st.selectbox("Highlight month (solar)", ["All"] + MONTHS, index=0, disabled=not do_solar)

        # climate settings
        humidity_mode = st.selectbox(
            "Humidity display",
            ["Relative (RH2M %)", "Specific (QV2M g/kg)"],
            index=0,
            disabled=not do_humidity,
        )
        rain_unit = st.selectbox(
            "Rainfall unit",
            ["mm/day (avg)", "mm/month (total)"],
            index=1,
            disabled=not do_rain,
        )

        with st.expander("Advanced: Year range", expanded=False):
            sy = st.text_input("Start year (optional)", value="")
            ey = st.text_input("End year (optional)", value="")

        run = st.button("Calculate", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📊 Results")

    if run:
        try:
            starty = parse_int_or_none(sy)
            endy = parse_int_or_none(ey)

            # Defaults for climate if user leaves blank
            climate_start = starty if starty else 2000
            climate_end = endy if endy else 2020

            # ================= SOLAR =================
            if do_solar:
                with st.spinner("Fetching PVGIS solar data..."):
                    res = cached_fetch(st.session_state.lat, st.session_state.lon, starty, endy)

                df = res.climatology.copy()
                df["Month"] = df["month"].apply(lambda m: MONTHS[m - 1])

                if units == "kWh/m²/month":
                    col = "ghi_kwh_m2_month"
                    label = "GHI (kWh/m²/month)"
                elif units == "kWh/m²/day":
                    col = "ghi_kwh_m2_day"
                    label = "GHI (kWh/m²/day)"
                else:
                    col = "ghi_mj_m2_day"
                    label = "GHI (MJ/m²/day)"

                st.markdown("### ☀️ Solar (GHI)")

                if month != "All":
                    mi = MONTHS.index(month) + 1
                    val = float(df.loc[df["month"] == mi, col].iloc[0])
                    st.metric(month, f"{val:.3f}", help=label, border=True)

                avg_ghi = df[col].mean()
                peak_month_idx = int(df[col].idxmax())
                peak_month = df.loc[peak_month_idx, "Month"]
                p1, p2 = st.columns(2)
                p1.metric("Yearly monthly average", f"{avg_ghi:.3f}")
                p2.metric("Peak month", peak_month)

                st.dataframe(df[["Month", col]].rename(columns={col: label}), width="stretch")

                chart_df = df[["Month", col]].rename(columns={col: "Value"})
                chart = (
                    alt.Chart(chart_df)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X("Month:N", sort=MONTHS, title="Month"),
                        y=alt.Y("Value:Q", title=label),
                        tooltip=[alt.Tooltip("Month:N"), alt.Tooltip("Value:Q", format=".3f", title=label)],
                    )
                    .interactive()
                    .properties(height=260)
                )
                st.altair_chart(chart, use_container_width=True)

                solar_csv = df[["Month", col]].rename(columns={col: label}).to_csv(index=False).encode("utf-8")
                st.download_button("Download Solar CSV", solar_csv, "monthly_ghi.csv", "text/csv")

            # ================= CLIMATE =================
            if do_humidity or do_rain:
                st.markdown("---")
                st.markdown("### 🌦️ Climate (NASA POWER)")
                st.caption(f"Years used: {climate_start}–{climate_end}")

                with st.spinner("Fetching climate data..."):
                    climate_df = cached_fetch_climate(
                        st.session_state.lat,
                        st.session_state.lon,
                        climate_start,
                        climate_end,
                    )

                # rainfall mm/month conversion using true days per month
                month_to_num = {calendar.month_abbr[i]: i for i in range(1, 13)}
                climate_df["MonthNum"] = climate_df["Month"].map(month_to_num)

                def _mm_month(row):
                    if pd.isna(row.get("PRECTOTCORR (mm/day)")) or pd.isna(row.get("MonthNum")):
                        return None
                    days = calendar.monthrange(2020, int(row["MonthNum"]))[1]
                    return row["PRECTOTCORR (mm/day)"] * days

                climate_df["Rainfall (mm/month)"] = climate_df.apply(_mm_month, axis=1)

                a, b = st.columns(2)

                if do_humidity:
                    with a:
                        if humidity_mode.startswith("Relative"):
                            st.caption("Relative Humidity (RH2M %)")
                            st.line_chart(climate_df.set_index("Month")["RH2M (%)"], height=260)
                        else:
                            st.caption("Specific Humidity (QV2M g/kg)")
                            st.line_chart(climate_df.set_index("Month")["QV2M (g/kg)"], height=260)
                else:
                    with a:
                        st.info("Humidity is turned off.")

                if do_rain:
                    with b:
                        if rain_unit.startswith("mm/day"):
                            st.caption("Rainfall (mm/day avg) — PRECTOTCORR")
                            st.line_chart(climate_df.set_index("Month")["PRECTOTCORR (mm/day)"], height=260)
                        else:
                            st.caption("Rainfall (mm/month total)")
                            st.line_chart(climate_df.set_index("Month")["Rainfall (mm/month)"], height=260)
                else:
                    with b:
                        st.info("Rainfall is turned off.")

                show_cols = ["Month"]
                if do_humidity:
                    show_cols.append("RH2M (%)" if humidity_mode.startswith("Relative") else "QV2M (g/kg)")
                if do_rain:
                    show_cols.append("PRECTOTCORR (mm/day)" if rain_unit.startswith("mm/day") else "Rainfall (mm/month)")

                st.dataframe(climate_df[show_cols], width="stretch")
                climate_csv = climate_df[show_cols].to_csv(index=False).encode("utf-8")
                st.download_button("Download Climate CSV", climate_csv, "monthly_climate.csv", "text/csv")

        except Exception as e:
            st.error(str(e))
    else:
        st.info("Search a place or click the map, choose settings, then press **Calculate**.")

# ================== ABOUT TAB ==================
with tab_about:
    st.subheader("About this app")
    st.write("Helios estimates monthly solar irradiation (GHI) and climate parameters for any location.")
    st.markdown(
        """
        **Solar Data**
        - PVGIS MRcalc API (ERA5 reanalysis)

        **Climate Data**
        - NASA POWER monthly point API
        - RH2M (Relative Humidity), QV2M (Specific Humidity), PRECTOTCORR (Precipitation corrected)
        """
    )
