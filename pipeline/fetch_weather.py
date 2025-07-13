
# %%
import requests 
import pandas as pd
from config import NOAA_API_KEY
from loggerInfo import get_logger

# %%

logger = get_logger("fetch_weather")


def fetch_weather_data(city, station_id, start_date, end_date):
    
    weather_base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    params = {
        "datasetid": "GHCND",
        "stationid": station_id,
        "startdate": start_date,
        "enddate": end_date,
        "datatypeid": "TMAX,TMIN",
        
    }
    
    headers = {"token" : NOAA_API_KEY}
    try:
        response = requests.get(weather_base_url, headers=headers, params=params)
        response.raise_for_status()
        logger.info(f"Successfully fetched weather data for {city} from {start_date} to {end_date}.")
        logger.info(f"Response status code: {response}")
        #Extract the 'results' list from the JSON response, or return an empty list if not present
        results = response.json().get("results", [])
        
        # converts the results into a pandas DataFrame
        df = pd.DataFrame(results)
        
        # if the Dataframe is empty (no results), return it as is
        if df.empty:
            logger.warning(f"No weather data found for {city}, {station_id} between {start_date} and {end_date}.")
            return df
        
         # Convert the 'date' field from string to a proper date object, removing the time component
        df["date"] = pd.to_datetime(df["date"]).dt.date
        
        # Reshape the DataFrame: 
        # - Use 'date' as the index
        # - Convert rows with 'datatype' (e.g., 'TMAX', 'TMIN') into columns
        # - Use 'value' as the cell content
        # - Keep only the first value if there are duplicates (aggfunc="first")
        df_pivot = df.pivot_table(
            index="date",
            columns="datatype",
            values="value",
            aggfunc="first"
        ).reset_index()

        # Add a new column to label each row with the city name
        df_pivot["city"] = city

        # Return a subset of the DataFrame with only the relevant columns
        return df_pivot[["date", "city", "TMAX", "TMIN"]]
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data for {city} from {start_date} to {end_date}: {e}")
        return pd.DataFrame()
        
        
# if __name__ == "__main__":
#     from datetime import datetime, timedelta

#     # Example parameters
#     city = "New York"
#     station_id = "GHCND:USW00094728"  # New York Independent System Operator
#     end_date = "2024-01-31"
#     start_date = "2024-01-01"

#     df = fetch_weather_data(city, station_id, start_date, end_date)

#     if not df.empty:
#         print(df.head())
#     else:
#         print("No data returned.")

    
# %%
