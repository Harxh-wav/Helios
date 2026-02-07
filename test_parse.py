from pvgis_client import fetch_monthly_ghi

res = fetch_monthly_ghi(28.6139, 77.2090)  # New Delhi
print(res.climatology)

