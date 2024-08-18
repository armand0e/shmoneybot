import yfinance as yf
import pandas as pd
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class StockTechnicalData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.history = None

    def fetch_history(self):
        logger.info(f"Fetching historical data for {self.ticker}")
        self.history = yf.Ticker(self.ticker).history(period="1y")
        logger.info(f"Fetched {len(self.history)} data points")

    def calculate_sma(self, window=14):
        if self.history is None:
            self.fetch_history()
        logger.info(f"Calculating SMA for {self.ticker} with window {window}")
        sma = self.history['Close'].rolling(window=window).mean()
        logger.info(f"Calculated SMA for {self.ticker}")
        return sma

    def calculate_rsi(self, window=14):
        if self.history is None:
            self.fetch_history()
        logger.info(f"Calculating RSI for {self.ticker} with window {window}")
        delta = self.history['Close'].diff(1)
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        logger.info(f"Calculated RSI for {self.ticker}")
        return rsi

if __name__ == "__main__":
    ticker = 'AAPL'
    stock_technical = StockTechnicalData(ticker)
    
    sma = stock_technical.calculate_sma()
    rsi = stock_technical.calculate_rsi()
    
    # Print last 5 values to check results
    logger.info("Final SMA values:")
    print(sma.tail(5))
    
    logger.info("Final RSI values:")
    print(rsi.tail(5))  