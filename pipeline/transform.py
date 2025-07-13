# Normalization,
# %%
import pandas as pd
from loggerInfo import get_logger

logger = get_logger("transform")

def merge_weather_and_energy(weather_df, energy_df):
    """
    Merges structured weather and energy dataframes on date and city.
    Returns a combined DataFrame with aligned rows for modeling.
    """
    if weather_df.empty:
        logger.error("Weather data is empty. Cannot perform merge.")
        return pd.DataFrame()
    
    if energy_df.empty:
        logger.error("Energy data is empty. Cannot perform merge.")
        return pd.DataFrame()
    
    try:
        weather_df["date"] = pd.to_datetime(weather_df["date"])
        energy_df["date"] = pd.to_datetime(energy_df["date"])
        
        merged_df = pd.merge(weather_df, energy_df, on=["date", "city"], how="inner")
        
        if merged_df.empty:
            logger.warning("Merge completed but returned no rows.")
        
        logger.info(f"Merged dataset contains {len(merged_df)} rows.")
        return merged_df
    
    except Exception as e:
        logger.error(f"Error during merging: {e}")
        return pd.DataFrame()