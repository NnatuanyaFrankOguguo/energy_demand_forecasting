import pandas as pd
from loggerInfo import get_logger
from datetime import datetime, timedelta

logger = get_logger("check_freshness")
    
#Warn you if your data is outdated (e.g., last update was a week ago).
def check_data_freshness(df: pd.DataFrame, freshness_threshold_days=2) -> bool:
    """
    Checks if the dataframe is fresh enough based on the last date.
    Checks if the latest available data is recent.
    Returns True if the data is stale, False otherwise.
    
    """
    
    if 'date' not in df.columns:
        raise ValueError("DataFrame must have a 'date' column for freshness check.")
    
    logger.info("Checking data freshness...")
    
    # Get the most recent date in the data
    latest_date = pd.to_datetime(df['date']).max()
    today = datetime.today()
    
    # How old is the most recent record?
    days_old = (today - latest_date).days
    
    logger.info(f"Data freshness checked. Most recent data is {days_old} days old.")
    
    # Return True if it's older than the freshness threshold
    return days_old > freshness_threshold_days
    
