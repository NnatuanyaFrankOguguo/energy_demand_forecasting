import pandas as pd
from loggerInfo import get_logger

logger = get_logger("check_outliers")

# Ensure the values are within real-world bounds.

def check_temperature_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Checks for temperature outliers in the dataframe.
    Returns a summary dataframe showing count and percentage of outliers.
    """
    logger.info("Checking for temperature outliers...")
    
    # Check where either TMAX or TMIN is out of expected range 
    mask = ( (df['TMAX'] > 130 ) | (df['TMAX'] < -50) | (df['TMIN'] > 130 ) | (df['TMIN'] < -50) )
    
    logger.info(f"Temperature outliers checked.{mask}")
    
    return df[mask] # Return only the rows with issues

def check_energy_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects negative energy consumption values.
    Returns rows where consumption is below 0.
    """
    logger.info("Checking for energy outliers...")
    return df[df['consumption'] < 0]  # Negative usage doesn't make sense