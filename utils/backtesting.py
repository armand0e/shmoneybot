from utils.logger import get_logger

logger = get_logger('Backtester')

class Backtester:
    def __init__(self, trading_strategy, historical_data):
        self.trading_strategy = trading_strategy
        self.historical_data = historical_data  # This should be a dictionary of stock data over time

    def run_backtest(self):
        logger.info("Starting backtest")
        portfolio_value = 100000  # Starting portfolio value for the backtest
        for date, daily_data in sorted(self.historical_data.items()):
            for ticker, data in daily_data.items():
                if self.trading_strategy.evaluate_stock(data['stock_data'], data['social_data']):
                    # Example: invest 1% of portfolio value in each viable stock
                    investment_amount = portfolio_value * 0.01
                    if self.trading_strategy.execute_trade(ticker, investment_amount, portfolio_value):
                        portfolio_value += self.simulate_trade_return(ticker, date)
        logger.info(f"Backtest completed with final portfolio value: {portfolio_value}")

    def simulate_trade_return(self, ticker, date):
        # Placeholder method to simulate returns from a trade
        return 100  # Example fixed return

logger.info("Backtester module initialized")