
import logging

logging.basicConfig(level=logging.INFO)

class Backtesting:
    def __init__(self, historical_data):
        self.historical_data = historical_data

    def backtest_strategy(self, strategy):
        logging.info("Starting backtesting")
        performance = []  # Store performance metrics here
        for date, data in self.historical_data.iterrows():
            decision = strategy(data)
            logging.info(f"Backtesting on {date}: Decision - {decision}")
            performance.append(decision)

        logging.info("Backtesting completed")
        return performance

# Example usage
# historical_data = apple_technical.history
# backtester = Backtesting(historical_data)
# performance = backtester.backtest_strategy(lambda data: data['Close'] > data['Close'].shift(1))  # Simple strategy
# print(performance)
