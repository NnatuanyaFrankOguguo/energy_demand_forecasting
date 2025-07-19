# 🌎 Energy Demand Forecasting and Analysis Dashboard

This project provides a complete pipeline to fetch, process, check, and visualize energy consumption and weather data across five major U.S. cities. It includes data collection scripts, quality checks, a modular pipeline structure, and a powerful Streamlit dashboard for visualizing energy patterns.

## 🚀 Project Features

- ✅ **Automated data pipeline** for fetching daily and historical data
- 📊 **Streamlit dashboard** with 4 interactive visualizations
- 🧪 **Data quality system** (missing values, outliers, freshness)
- 📅 **Scheduler** for daily/periodic updates
- 🗂️ **Modular structure** with reusable Python modules

---

## 🗂️ Project Structure

```bash
energy_demand_forecasting/
├── data/                      # Raw and processed CSV data files
│   ├── weather/              # Weather data per city
│   └── energy/               # Energy consumption data
├── pipeline/                 # Core ETL & orchestration scripts
│   ├── fetch_daily.py        # Fetch current day's data
│   ├── fetch_historical.py   # Fetch historical data
│   ├── config.py             # City/station configuration
│   └── merge.py              # Merge weather and energy datasets
├── quality/                  # Data quality check modules
│   ├── check_missing.py
│   ├── check_outliers.py
│   ├── check_freshness.py
│   └── quality_dashboard.py  # Runs all checks and logs/report results
├── dashboard/                # Streamlit dashboard
│   └── app.py                # Interactive dashboard interface
├── scheduler.py              # Task scheduler (e.g., run daily fetch)
├── requirements.txt
└── README.md
📉 Dashboard Overview (Streamlit)
Launch the dashboard with:

bash
Copy
Edit
streamlit run dashboard/app.py
🔍 1. Geographic Overview
Map of all 5 cities

Current temperature, today’s energy usage, % change from yesterday

Color-coded: Red = high usage, Green = low

📈 2. Time Series Analysis
Dual-axis chart of temperature and energy (90 days)

Dropdown to select city or "All Cities"

Weekend shading, interactive legend

🔬 3. Correlation Analysis
Scatter plot: temperature vs. energy usage

Regression line, correlation stats

Hover for date, city, exact values

🔥 4. Usage Patterns Heatmap
Temperature range (y) × day of week (x)

Cell values = average energy usage

Color scale: Blue (low) → Red (high)

Filter by city

🏙️ Cities & Config
The pipeline and dashboard are built around these cities:

python
Copy
Edit
CITY_CONFIG = {
  "New York": {"station": "GHCND:USW00094728", "eia": "NYIS"},
  "Chicago": {"station": "GHCND:USW00094846", "eia": "PJM"},
  "Houston": {"station": "GHCND:USW00012960", "eia": "ERCO"},
  "Phoenix": {"station": "GHCND:USW00023183", "eia": "AZPS"},
  "Seattle": {"station": "GHCND:USW00024233", "eia": "SCL"},
}
⚙️ How It Works
1. Fetch Historical/Daily Data
Run either of:

bash
Copy
Edit
python pipeline/fetch_historical.py
python pipeline/fetch_daily.py
These will:

Retrieve energy usage from EIA

Get temperature from NOAA/NCEI

Save data in data/weather/ and data/energy/

2. Merge Weather and Energy Data
python
Copy
Edit
from pipeline.merge import merge_weather_and_energy
This merges data on date and city for analysis and modeling.

3. Run Quality Checks
python
Copy
Edit
from quality.quality_dashboard import run_quality_checks
run_quality_checks()
This checks for:

❌ Missing values

❗ Outliers

⏳ Stale data

4. Schedule Daily Updates
bash
Copy
Edit
python scheduler.py
Uses Python's schedule library to automate daily data refresh.

🧪 Installation
bash
Copy
Edit
git clone https://github.com/your-username/energy_demand_forecasting.git
cd energy_demand_forecasting
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
🖥️ Technologies Used
Python 🐍

Pandas / NumPy

Plotly + Streamlit

EIA API + NOAA API

Schedule (for automation)

📌 Future Improvements
✅ Deploy Streamlit dashboard online (e.g., Streamlit Cloud, HuggingFace Spaces)

⏱️ Add prediction model for future demand

🔐 Add authentication for private dashboard

📄 License
MIT License — feel free to use, extend, or contribute!

yaml
Copy
Edit

---

Let me know if you want:

- A sample `.env` file for API keys  
- Badges (like “last updated”, “Python version”, “License”)  
- A contribution section or a link to a demo deployment.







Ask ChatGPT
