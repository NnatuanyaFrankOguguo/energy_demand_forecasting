# 90-day historical
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# %%
import pandas as pd
from datetime import datetime, timedelta
from pipeline.config import CITY_CONFIG
from fetch_energy import fetch_energy_data
from fetch_weather import fetch_weather_data
from transform import merge_weather_and_energy
from save import save_data, save_raw_data
from common.loggerInfo import get_logger
from quality.quality_dashboard import run_quality_checks

# %%

logger = get_logger("fetch_historical")

def fetch_90_day_history():
    # today = datetime.now().date()
    # end_date = today - timedelta(days=30)     # Avoid requesting today's data
    # start_date = end_date - timedelta(days=90)
    
    end_date = datetime.now().date() - timedelta(days=2) # Avoid requesting today's data but 2 days ago
    start_date = end_date - timedelta(days=90)
    
    all_data = []
    
    for city, codes in CITY_CONFIG.items():
        logger.info(f"Fetching data for {city}...")
        weather_df = fetch_weather_data(city, codes["station"], start_date.isoformat(), end_date.isoformat())
        energy_df = fetch_energy_data(codes["eia"], start_date, end_date, city)
        merged_df = merge_weather_and_energy(weather_df, energy_df)
        
        save_raw_data(weather_df, city, "weather", start_date.isoformat(), end_date.isoformat())
        save_raw_data(energy_df, city, "energy", start_date, end_date)
        
        all_data.append(merged_df)
        
    final_df = pd.concat(all_data, ignore_index=True)
    run_quality_checks(final_df)  # Just run the checks
    save_data(final_df, historical=True) # Save the actual data
    
if __name__ == "__main__":
    fetch_90_day_history()


# %%
