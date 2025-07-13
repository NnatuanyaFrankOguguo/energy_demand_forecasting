# %%
import os
from dotenv import load_dotenv
from loggerInfo import get_logger 
# %%
load_dotenv()
logger = get_logger("config")

logger.info("Loading environment variables...")

NOAA_API_KEY = os.getenv("NOAA_API_KEYS")
EIA_API_KEY = os.getenv("EIA_API_KEYS")

logger.info("Environment variables loaded.")

CITY_CONFIG = {
    "New York": {"station": "GHCND:USW00094728", "eia": "NYIS"},
    "Chicago": {"station": "GHCND:USW00094846", "eia": "PJM"},
    "Houston": {"station": "GHCND:USW00012960", "eia": "ERCO"},
    "Phoenix": {"station": "GHCND:USW00023183", "eia": "AZPS"},
    "Seattle": {"station": "GHCND:USW00024233", "eia": "SCL"},
}

logger.info("City config loaded.")

# %%