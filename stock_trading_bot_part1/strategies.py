
import logging
import config

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, config.SETTINGS['logging_level']))

class DollarCostAveragingStrategy:
    def __init__(self, investment_amount, interval_days):
        self.investment_amount = investment_amount
        self.interval_days = interval_days
        self.last_investment_date = None

    def should_invest(self, current_date):
        if self.last_investment_date is None or (current_date - self.last_investment_date).days >= self.interval_days:
            self.last_investment_date = current_date
            return True
        return False

    def execute(self, portfolio, ticker, price, current_date):
        if self.should_invest(current_date):
            shares_to_buy = self.investment_amount / price
            portfolio[ticker] = portfolio.get(ticker, 0) + shares_to_buy
            logger.info(f"Bought {shares_to_buy} shares of {ticker} at {price} on {current_date}")
        else:
            logger.info(f"No investment made for {ticker} on {current_date}")

class MovingAverageStrategy:
    def __init__(self, short_window=50, long_window=200):
        self.short_window = short_window
        self.long_window = long_window

    def execute(self, historical_data):
        short_ma = historical_data['Close'].rolling(window=self.short_window).mean()
        long_ma = historical_data['Close'].rolling(window=self.long_window).mean()
        
        signal = 0
        if short_ma.iloc[-1] > long_ma.iloc[-1]:
            signal = 1  # Golden Cross - Bullish
            logger.info("Golden Cross detected - Buy Signal")
        elif short_ma.iloc[-1] < long_ma.iloc[-1]:
            signal = -1  # Death Cross - Bearish
            logger.info("Death Cross detected - Sell Signal")
        return signal

class MeanReversionStrategy:
    def __init__(self, window=20, threshold=1.5):
        self.window = window
        self.threshold = threshold

    def execute(self, historical_data):
        mean = historical_data['Close'].rolling(window=self.window).mean()
        std = historical_data['Close'].rolling(window=self.window).std()
        last_price = historical_data['Close'].iloc[-1]

        if last_price > mean.iloc[-1] + self.threshold * std.iloc[-1]:
            logger.info("Price above mean + threshold - Consider Selling")
            return -1  # Sell Signal
        elif last_price < mean.iloc[-1] - self.threshold * std.iloc[-1]:
            logger.info("Price below mean - threshold - Consider Buying")
            return 1  # Buy Signal
        return 0  # No Signal
