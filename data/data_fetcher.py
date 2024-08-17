
import yfinance as yf
import logging

logger = logging.getLogger('DataFetcher')

class FinancialDataFetcher:
    def __init__(self, historical_data_length="5y"):
        self.historical_data_length = historical_data_length
        logger.info("FinancialDataFetcher initialized")

    def fetch_real_time_data(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            real_time_data = stock.info
            logger.info(f"Fetched real-time data for {ticker}")
            return real_time_data
        except Exception as e:
            logger.error(f"Failed to fetch real-time data for {ticker}: {str(e)}")
            return None

    def fetch_historical_data(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            historical_data = stock.history(period=self.historical_data_length)
            logger.info(f"Fetched historical data for {ticker}")
            return historical_data
        except Exception as e:
            logger.error(f"Failed to fetch historical data for {ticker}: {str(e)}")
            return None

    def fetch_financial_data(self, ticker):
        real_time_data = self.fetch_real_time_data(ticker)
        historical_data = self.fetch_historical_data(ticker)

        if real_time_data and historical_data:
            financial_data = {
                'ticker': ticker,
                'info': real_time_data,
                'history': historical_data
            }
            return financial_data
        else:
            logger.warning(f"Incomplete financial data for {ticker}")
            return None
