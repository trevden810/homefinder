import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database settings
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'properties.db')

# Scraper settings
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 2  # Seconds between requests to avoid rate limiting

# Default search parameters
DEFAULT_MIN_PRICE = 0
DEFAULT_MAX_PRICE = 1000000
DEFAULT_LOCATION = "Denver, CO"

# API Keys (store these in .env file, not in code)
ZILLOW_API_KEY = os.getenv('ZILLOW_API_KEY', '')
REALTOR_API_KEY = os.getenv('REALTOR_API_KEY', '')
