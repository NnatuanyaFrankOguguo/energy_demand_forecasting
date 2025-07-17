


import pandas as pd
from check_missing import check_missing_values
from check_outliers import check_temperature_outliers, check_energy_outliers
from check_freshness import check_data_freshness
from loggerInfo import get_logger
import os
from datetime import datetime


logger = get_logger("quality_dashboard")

# This is the command center that pulls everything together and gives you a readable report

def run_quality_checks(df: pd.DataFrame):
    """
    Run all quality checks and print the results.
    """
    logger.info(" Running Data Quality Checks...")
    
    os.makedirs("data/quality_reports", exist_ok=True)
    log_file = f"data/quality_reports/quality_log.txt"
    
    with open(log_file, "a") as f:
        f.write(f'\n=== Quality Check Run on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ===\n')
    
        #1. Missing Value Check
        missing_summary = check_missing_values(df)
        if not missing_summary.empty:
            logger.info("Missing Values Found:")
            logger.info(missing_summary)
            f.write("[Missing Values]\n")
            f.write(missing_summary.to_string())
            f.write("\n")
        else:
            logger.info("No missing values found.")
            f.write("[No Missing Values]\n")
        
        #2. Temperature Outlier Check
        temp_outliers = check_temperature_outliers(df)
        if not temp_outliers.empty:
            logger.info(f"Temperature Outliers Found: {len(temp_outliers)} rows")
            logger.info(temp_outliers)
            f.write(f"[Temp Outliers] {len(temp_outliers)} rows\n")
        else:
            logger.info(" No temperature outliers found.")
        
        #3. Energy Outlier Check
        energy_outliers = check_energy_outliers(df)
        if not energy_outliers.empty:
            logger.info(f"Negative Energy Values Found: {len(energy_outliers)} rows")
            logger.info(energy_outliers)
            f.write(f"[Negative Energy] {len(energy_outliers)} rows\n")
        else:
            logger.info(" No energy outliers found.")
            
        # 4. Freshness Check
        try: 
            is_stale = check_data_freshness(df)
            if is_stale:
                logger.info(" Data is stale. Please refresh the data.")
                f.write("[Data Freshness] Stale\n" if is_stale else "[Data Freshness] Fresh\n")
            else:
                logger.info(" Data is fresh and up-to-date.")
                f.write("[Data Freshness] Fresh\n")
        except Exception as e:
            logger.error(f"An error occurred during data freshness check: {e}")
            logger.error("Please check your data and try again.")
            f.write(f"[Freshness Error] {e}\n")
    
    logger.info(" Quality Checks Completed.")
    