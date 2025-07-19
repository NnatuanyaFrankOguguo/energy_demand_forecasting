import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import schedule
import time
from common.loggerInfo import get_logger
import subprocess


logger = get_logger("scheduler")

logger.info("Scheduler started.")

def run_fetch_historical():
    """
    Runs the fetch_historical script to collect 90-day historical data.
    """
    logger.info("Running fetch_historical script...")
    try:
        subprocess.run(["python", "pipeline/fetch_historical.py"], check=True)
        logger.info("fetch_historical script completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running fetch_historical script: {e}")
        

# Run every day at 06:00 AM
schedule.every().day.at("06:00").do(run_fetch_historical)

while True:
    schedule.run_pending()
    time.sleep(60)  # Wait for one minute before checking again
    logger.info("Scheduler is running...")  # Log that the scheduler is active