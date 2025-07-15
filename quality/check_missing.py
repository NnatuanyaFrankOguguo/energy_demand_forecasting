import pandas as pd
from loggerInfo import get_logger

logger = get_logger("check_missing")
#Identify which columns have missing values and how bad the issue is.
def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Checks for missing/null values in each column of the dataframe.
    Returns a summary dataframe showing count and percentage of missing.
    """
    logger.info("Checking for missing values...")
    
    missing_count = df.isnull().sum() #Count how many NaNs in each columns
    missing_percent = (missing_count / len(df)) * 100 # % of missing values per column
    
    logger.info(f"Missing values checked.{df}")
    
    #Build summary DataFrame
    summary = pd.DataFrame({
        'missing_count': missing_count,
        'missing_percent': missing_percent
    })
    
    logger.info(f"Missing values summary created.{summary}")
    
    return summary[summary['missing_percent'] > 0] # Return only rows with missing values