
import yfinance as yf
import logging

class FinancialDataFetcher:
    def __init__(self, stock_symbol):
        self.stock_symbol = stock_symbol

    def get_realtime_data(self):
        logging.info(f"Fetching real-time data for {self.stock_symbol}")
        stock = yf.Ticker(self.stock_symbol)
        data = stock.history(period="1d")
        if not data.empty:
            last_quote = data.iloc[-1].to_dict()
            logging.info(f"Data fetched successfully for {self.stock_symbol}")
            return last_quote
        else:
            logging.warning(f"No data found for {self.stock_symbol}")
            return None

# Debugging Instructions:
# - Ensure the yfinance library is installed and updated.
# - Test the API call with different stock symbols to ensure accuracy.
# - Modify the function to fetch different time periods or additional data points as needed.
