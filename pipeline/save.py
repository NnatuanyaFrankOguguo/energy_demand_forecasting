# writes to CSV

# %%
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import os
from datetime import datetime
from common.loggerInfo import get_logger
import pandas as pd

# %%

logger = get_logger("save")

def save_data(df, historical=False):
    if df.empty:
        logger.error("No data to save.")
        return
    
    os.makedirs("data/processed", exist_ok=True)
    logger.info("Saving data...")
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"historical_data_{date_str}.csv" if historical else f"daily_data_{date_str}.csv"
    path = os.path.join("data/processed", filename)
    
    # Save the DataFrame to a CSV file
    df.to_csv(path, index=False)
    logger.info("Data saved successfully.")
# %%

# ===========================
# Save Raw API Response
# ===========================

def save_raw_data(df: pd.DataFrame, city: str, source: str, start_date: str, end_date: str):
    """
    Save raw API data (weather or energy) into /data/raw as CSV.
    - source: "weather" or "energy"
    """
    if df.empty:
        logger.warning(f"No raw {source} data to save for {city}.")
        return

    os.makedirs("data/raw", exist_ok=True)
    filename = f"{city}_{source}_{start_date}_to_{end_date}.csv"
    path = os.path.join("data/raw", filename)

    df.to_csv(path, index=False)
    logger.info(f"Raw {source} data saved for {city} at {path}.")