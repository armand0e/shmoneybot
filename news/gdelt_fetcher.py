import requests
import logging
from config import SETTINGS

class GDELTFetcher:
    def __init__(self, stock_symbol):
        self.stock_symbol = stock_symbol
        self.keywords = [stock_symbol] + SETTINGS['global_market_keywords']
        
    def fetch_gdelt_tone_chart(self):
        logging.info(f"Fetching GDELT tone chart for {self.stock_symbol}")
        base_url = "https://api.gdeltproject.org/api/v2/doc/doc?query="
        query = f'({" OR ".join(self.keywords)})'  # Surround OR conditions with parentheses
        url = f"{base_url}{query}&mode=tonechart"
        try:
            response = requests.get(url)
            response.raise_for_status()
            print(f"Raw GDELT response: {response.text}")
            tone_data = response.json()
            logging.info("GDELT tone chart data fetched successfully")
            return tone_data
        except ValueError as e:
            logging.error(f"Failed to parse JSON response: {e}")
            return {}

# Debugging Instructions:
# - Use this method to fetch tone chart data for your stock.
# - Modify the keywords as needed to focus on different aspects of market sentiment.