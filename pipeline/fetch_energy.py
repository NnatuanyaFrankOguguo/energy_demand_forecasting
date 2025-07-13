
# %%
import requests 
import pandas as pd
from config import EIA_API_KEY
from loggerInfo import get_logger


logger = get_logger("fetch_energy")



# %%

def fetch_energy_data(eia_station_id, start_date, end_date):
    energy_base_url = "https://api.eia.gov/v2/electricity/rto/daily-region-data/data/"
    
    params = {
        "api_key": EIA_API_KEY,
        "frequency": "daily",
        "data[]": "value",
        "facets[respondent][]": eia_station_id,  # e.g., "NYIS"
        "start": start_date,
        "end": end_date
    }
    
    try:
        response = requests.get(energy_base_url, params=params)
        response.raise_for_status()
        logger.info(f"Successfully fetched energy data for {eia_station_id} from {start_date} to {end_date}.")
        logger.info(f"Response status code: {response}")
        
        # Extract the 'results' list from the JSON response, or return an empty list if not present
        results = response.json().get("response", {}).get("data", [])
        
        # converts the results into a pandas DataFrame
        df = pd.DataFrame(results)
        
        # if the Dataframe is empty (no results), return it as is
        if df.empty:
            logger.warning(f"No energy data found for {eia_station_id} between {start_date} and {end_date}.")
            return df
        
        # Convert the 'date' field from string to a proper date object, removing the time component
        df["period"] = pd.to_datetime(df["period"]).dt.date
        
        # Convert the 'value' field from string to a float
        df["value"] = df["value"].astype(float)
        
        # Rename the 'value' field to 'daily_consumption' and "period" to "date"
        df = df.rename(columns={"value": "energy_consumption", "period": "date"})
        
        df["city"] = eia_station_id
        
        logger.info(f"Successfully fetched energy data for {eia_station_id} from {start_date} to {end_date}.")
        
        return df[["date", "city", "energy_consumption"]]
        
       
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching energy data for {eia_station_id} from {start_date} to {end_date}: {e}")
        return pd.DataFrame()
# %%
if __name__ == "__main__":
    from datetime import datetime, timedelta

    # Example parameters
    eia_station_id = "NYIS"  # New York Independent System Operator
    end_date = datetime.now().date() - timedelta(days=30)
    start_date = end_date - timedelta(days=30)

    start_date_str = start_date.isoformat()
    end_date_str = end_date.isoformat()

    df = fetch_energy_data(eia_station_id, start_date_str, end_date_str)

    if not df.empty:
        print(df.head())
    else:
        print("No data returned.")
