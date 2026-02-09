# ☀️ Helios — Solar & Climate Profiling Tool

Helios is a web-based analytical tool designed to estimate **monthly solar radiation (GHI)** and key **climate parameters** for any geographic location.  
It is intended for **academic use**, **research assistance**, and **preliminary site assessment** in solar and climate-related studies.

---

## 🎯 Objective

The goal of Helios is to provide a **simple, interactive interface** to access long-term:
- Solar resource data
- Atmospheric humidity
- Rainfall patterns

This helps researchers and students understand how **climatic conditions influence solar energy potential** at a given location.

---

## 📊 Parameters Supported

### ☀️ Solar (PVGIS)
- Global Horizontal Irradiance (GHI)
- Units supported:
  - kWh/m²/month
  - kWh/m²/day
  - MJ/m²/day
- Monthly climatological averages
- Optional year-range filtering

### 🌦️ Climate (NASA POWER)
- **Relative Humidity (RH2M)** — %
- **Specific Humidity (QV2M)** — g/kg
- **Rainfall (PRECTOTCORR)**:
  - Average (mm/day)
  - Total (mm/month)

Users can choose to calculate **only solar**, **only climate**, or **both**, depending on the use case.

---

## 🧠 Why Climate Parameters Matter

While solar irradiance determines energy availability, **humidity and rainfall directly affect**:
- Atmospheric clarity
- Panel efficiency
- Long-term performance degradation
- Seasonal variability in output

Including these parameters enables a **more realistic and research-oriented assessment** compared to solar-only tools.

---

## 🗺️ Data Sources

- **PVGIS (European Commission)**  
  - Dataset: ERA5 reanalysis  
  - Used for global horizontal irradiation (GHI)

- **NASA POWER API**  
  - Monthly point-based climatological data  
  - Parameters: RH2M, QV2M, PRECTOTCORR

Both datasets are widely used in **peer-reviewed academic research**.

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** (web interface)
- **Altair** (interactive charts)
- **Folium** (map-based location selection)
- **PVGIS API**
- **NASA POWER API**

---

## 🚀 Usage

1. Enter a location (city, region, or institute)
2. Select the desired parameters (Solar / Humidity / Rainfall)
3. Adjust units or year range if needed
4. Click **Calculate**
5. Visualize results and download CSV files

---

## 🎓 Academic Use Case

Helios is suitable for:
- College projects
- Research data exploration
- Feasibility studies
- Concept validation before detailed simulation

---

## 👤 Author

**Harsh**  
Undergraduate Engineering Student  
Project developed as part of academic exploration in renewable energy and data-driven analysis.

---

## 📌 Version

**v1.1** — Solar + Climate Profiling  
(Added humidity & rainfall parameters and refined UI)

