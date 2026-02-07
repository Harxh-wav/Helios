import calendar
from dataclasses import dataclass
import requests
import pandas as pd

PVGIS_MRCALC_URL = "https://re.jrc.ec.europa.eu/api/v5_3/MRcalc"

@dataclass(frozen=True)
class MonthlyGHIResult:
    monthly_table: pd.DataFrame
    climatology: pd.DataFrame  # 12-month averages across years

def fetch_monthly_ghi(lat: float, lon: float, startyear: int | None = None, endyear: int | None = None) -> MonthlyGHIResult:
    params = {"lat": lat, "lon": lon, "horirrad": 1, "outputformat": "json"}
    if startyear is not None:
        params["startyear"] = int(startyear)
    if endyear is not None:
        params["endyear"] = int(endyear)

    r = requests.get(PVGIS_MRCALC_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    df = pd.DataFrame(data["outputs"]["monthly"])  # year, month, H(h)_m

    df["days_in_month"] = [calendar.monthrange(int(y), int(m))[1] for y, m in zip(df["year"], df["month"])]
    df["ghi_kwh_m2_day"] = df["H(h)_m"] / df["days_in_month"]
    df["ghi_mj_m2_day"] = df["ghi_kwh_m2_day"] * 3.6

    clim = (
        df.groupby("month", as_index=False)[["H(h)_m", "ghi_kwh_m2_day", "ghi_mj_m2_day"]]
        .mean()
        .rename(columns={"H(h)_m": "ghi_kwh_m2_month"})
    )

    return MonthlyGHIResult(monthly_table=df, climatology=clim)
