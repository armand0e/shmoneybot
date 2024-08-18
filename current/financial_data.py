import yfinance as yf
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class StockFinancialData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = None

    def fetch_data(self):
        logger.info(f"Fetching financial data for {self.ticker}")
        self.data = yf.Ticker(self.ticker).info

    def get_financial_data(self):
        if not self.data:
            self.fetch_data()
        financial_data = {
            'current_volume': self.data.get('volume'),
            'pe_ratio': self.data.get('forwardPE'),
            'eps': self.data.get('trailingEps'),
            'market_cap': self.data.get('marketCap'),
            'revenue': self.data.get('totalRevenue'),
            'open_interest_calls': None,  # Placeholder for future extension
            'open_interest_puts': None,  # Placeholder for future extension
        }
        logger.info(f"Financial data for {self.ticker}: {financial_data}")
        return financial_data

    def get_income_statement(self):
        logger.info(f"Fetching income statement for {self.ticker}")
        income_stmt = yf.Ticker(self.ticker).financials
        logger.info(f"Income statement data for {self.ticker}: {income_stmt}")
        return income_stmt

# Example usage
if __name__=='__main__':
    apple_financials = StockFinancialData('AAPL').get_financial_data()
    print(apple_financials)
    apple_income_stmt = StockFinancialData('AAPL').get_income_statement()
    print(apple_income_stmt)