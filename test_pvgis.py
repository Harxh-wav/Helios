import requests
import json

lat, lon = 28.6139, 77.2090  # New Delhi
url = "https://re.jrc.ec.europa.eu/api/MRcalc"
params = {"lat": lat, "lon": lon, "horirrad": 1, "outputformat": "json"}

r = requests.get(url, params=params, timeout=30)
r.raise_for_status()
data = r.json()

print("Top-level keys:", list(data.keys()))

# Print a readable preview so we can find monthly values
print("\n--- JSON preview (trimmed) ---")
print(json.dumps(data, indent=2)[:2000])
