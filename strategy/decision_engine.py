import logging
import statistics

class DecisionEngine:
    def __init__(self, historical_data, sentiment_score, volume_data=None, market_factors=None):
        self.historical_data = historical_data
        self.sentiment_score = sentiment_score
        self.volume_data = volume_data  # Optional: Integrate volume data
        self.market_factors = market_factors  # Optional: Include broader market sentiment

    def evaluate_stock(self):
        logging.info("Evaluating stock based on historical data, sentiment, and additional factors")

        # Calculate average price and standard deviation to assess volatility
        avg_price = sum(self.historical_data) / len(self.historical_data)
        price_volatility = statistics.stdev(self.historical_data)
        logging.info(f"Average historical price: {avg_price}")
        logging.info(f"Price volatility (std dev): {price_volatility}")
        logging.info(f"Sentiment score: {self.sentiment_score}")

        # Dynamic thresholds based on volatility
        buy_threshold = avg_price + 0.5 * price_volatility
        sell_threshold = avg_price - 0.5 * price_volatility

        logging.info(f"Dynamic Buy threshold: {buy_threshold}")
        logging.info(f"Dynamic Sell threshold: {sell_threshold}")

        # Evaluate decision
        if avg_price > buy_threshold and self.sentiment_score > 0.2:
            return "Buy"
        elif avg_price < sell_threshold and self.sentiment_score < -0.2:
            return "Sell"
        else:
            return "Hold"

# Debugging Instructions:
# - Test with different historical data and sentiment scores to see how the decision changes.
# - Ensure that the logic reflects the intended strategy (e.g., buy when sentiment is positive and prices are high).
# - Use the test script to validate the decision-making process.