import calendar
import pandas as pd
import requests

POWER_MONTHLY_POINT = "https://power.larc.nasa.gov/api/temporal/monthly/point"

def _month_name(m: int) -> str:
    return calendar.month_abbr[m]

def fetch_monthly_climate(lat: float, lon: float, startyear: int, endyear: int) -> pd.DataFrame:
    """
    NASA POWER monthly climate:
      - RH2M: Relative Humidity at 2m (%)
      - QV2M: Specific Humidity at 2m (kg/kg or often represented as g/kg in many datasets)
      - PRECTOTCORR: Precipitation corrected (mm/day as average daily rate)
    """
    params = {
        "community": "RE",
        "parameters": "RH2M,QV2M,PRECTOTCORR",
        "latitude": lat,
        "longitude": lon,
        "start": startyear,
        "end": endyear,
        "format": "JSON",
    }

    r = requests.get(POWER_MONTHLY_POINT, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    props = data.get("properties", {})
    parameter = props.get("parameter", {})

    rh_map = parameter.get("RH2M", {}) or {}
    qv_map = parameter.get("QV2M", {}) or {}
    pr_map = parameter.get("PRECTOTCORR", {}) or {}

    rows = []
    for m in range(1, 13):
        rh_vals, qv_vals, pr_vals = [], [], []
        for y in range(startyear, endyear + 1):
            key = f"{y}{m:02d}"
            if key in rh_map and rh_map[key] is not None:
                rh_vals.append(rh_map[key])
            if key in qv_map and qv_map[key] is not None:
                qv_vals.append(qv_map[key])
            if key in pr_map and pr_map[key] is not None:
                pr_vals.append(pr_map[key])

        rows.append({
            "Month": _month_name(m),
            "RH2M (%)": (sum(rh_vals) / len(rh_vals)) if rh_vals else None,
            "QV2M (g/kg)": (sum(qv_vals) / len(qv_vals)) if qv_vals else None,
            "PRECTOTCORR (mm/day)": (sum(pr_vals) / len(pr_vals)) if pr_vals else None,
        })

    return pd.DataFrame(rows)
