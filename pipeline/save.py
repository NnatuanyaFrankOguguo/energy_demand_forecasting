# writes to CSV

# %%
import os
from datetime import datetime
from loggerInfo import get_logger

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
