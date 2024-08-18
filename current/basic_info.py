import yfinance as yf
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class StockBasicInfo:
    def __init__(self, ticker):
        self.ticker = ticker
        self.info = None

    def fetch_info(self):
        logger.info(f"Fetching basic info for {self.ticker}")
        self.info = yf.Ticker(self.ticker).info

    def get_basic_info(self):
        if not self.info:
            self.fetch_info()
        basic_info = {
            'name': self.info.get('shortName'),
            'sector': self.info.get('sector'),
            'description': self.info.get('longBusinessSummary'),
            'market_cap_rank': self.info.get('marketCap')
        }
        logger.info(f"Basic info for {self.ticker}: {basic_info}")
        return basic_info

if __name__=='__main__':
    apple_info = StockBasicInfo('AAPL').get_basic_info()
    print(apple_info)