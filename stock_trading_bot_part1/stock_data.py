
import yfinance as yf
import pandas as pd
import logging
import config

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, config.SETTINGS['logging_level']))

class StockData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = pd.DataFrame()

    def fetch_new_data(self):
        """Fetch new historical data and append it to the existing dataset."""
        try:
            logger.info(f"Fetching historical data for {self.ticker}")
            new_data = yf.Ticker(self.ticker).history(period=config.SETTINGS['historical_data_length'])
            if not new_data.empty:
                logger.info(f"Fetched {len(new_data)} new data points for {self.ticker}")
                self.data = pd.concat([self.data, new_data]).drop_duplicates().sort_index()
            else:
                logger.warning(f"No new data found for {self.ticker}")
        except Exception as e:
            logger.error(f"Error fetching historical data for {self.ticker}: {e}")

    def calculate_sma(self, window=14):
        """Calculate the Simple Moving Average (SMA) for the specified window."""
        if not self.data.empty:
            logger.info(f"Calculating SMA for {self.ticker} with window {window}")
            self.data[f'SMA_{window}'] = self.data['Close'].rolling(window=window).mean()
            logger.info(f"Calculated SMA for {self.ticker}")

    def calculate_rsi(self, window=14):
        """Calculate the Relative Strength Index (RSI) for the specified window."""
        if not self.data.empty:
            logger.info(f"Calculating RSI for {self.ticker} with window {window}")
            delta = self.data['Close'].diff(1)
            gain = delta.where(delta > 0, 0)
            loss = -delta.where delta < 0, 0)
            avg_gain = gain.rolling(window=window).mean()
            avg_loss = loss.rolling(window=window).mean()
            rs = avg_gain / avg_loss
            self.data[f'RSI_{window}'] = 100 - (100 / (1 + rs))
            logger.info(f"Calculated RSI for {self.ticker}")

    def get_latest_close(self):
        """Get the latest closing price of the stock."""
        if not self.data.empty:
            return self.data['Close'].iloc[-1]
        else:
            logger.warning(f"No data available for {self.ticker}")
            return None
