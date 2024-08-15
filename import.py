
import os

# Define the new project structure
project_name = "TradingBot"
dirs = [
    f"{project_name}/",
    f"{project_name}/data/",
    f"{project_name}/news/",
    f"{project_name}/sentiment/",
    f"{project_name}/strategy/",
    f"{project_name}/ethics/"
]

# Create directories
for dir in dirs:
    os.makedirs(dir, exist_ok=True)

# Create a configuration file
config_content = """
API_KEYS = {
    'interactive_brokers': 'your_ib_key_here',
    'news_api': 'your_news_api_key_here'
}

SETTINGS = {
    'historical_data_length': '1y',
    'news_articles_limit': 100
}
"""

# Sample files with more modular and testable code
files = {
    f"{project_name}/config.py": config_content,
    f"{project_name}/data/data_fetcher.py": """
import logging

class DataFetcher:
    def __init__(self, stock_symbol):
        self.stock_symbol = stock_symbol

    def get_historical_data(self):
        logging.info(f"Fetching historical data for {self.stock_symbol}")
        # Replace with actual IB API calls or mock data for testing
        return [100, 102, 101, 105, 110]

""",
    f"{project_name}/data/test_data_fetcher.py": """
from data_fetcher import DataFetcher

def test_data_fetcher():
    fetcher = DataFetcher("AAPL")
    data = fetcher.get_historical_data()
    assert len(data) > 0
    print("DataFetcher test passed.")

if __name__ == "__main__":
    test_data_fetcher()
""",
    f"{project_name}/news/news_fetcher.py": """
import logging

class NewsFetcher:
    def __init__(self, stock_symbol):
        self.stock_symbol = stock_symbol

    def get_news(self):
        logging.info(f"Fetching news for {self.stock_symbol}")
        # Replace with actual News API calls or mock data for testing
        return [
            "The company had a great quarter with profits exceeding expectations.",
            "The stock has seen a lot of volatility recently."
        ]
""",
    f"{project_name}/news/test_news_fetcher.py": """
from news_fetcher import NewsFetcher

def test_news_fetcher():
    fetcher = NewsFetcher("AAPL")
    news = fetcher.get_news()
    assert len(news) > 0
    print("NewsFetcher test passed.")

if __name__ == "__main__":
    test_news_fetcher()
""",
    f"{project_name}/sentiment/sentiment_analyzer.py": """
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_sentiment(self, news_articles):
        logging.info("Analyzing sentiment of news articles")
        scores = [self.analyzer.polarity_scores(article)["compound"] for article in news_articles]
        return sum(scores) / len(scores)
""",
    f"{project_name}/sentiment/test_sentiment_analyzer.py": """
from sentiment_analyzer import SentimentAnalyzer

def test_sentiment_analyzer():
    analyzer = SentimentAnalyzer()
    test_news = [
        "This is the best product ever.",
        "Terrible company with bad management."
    ]
    score = analyzer.analyze_sentiment(test_news)
    assert isinstance(score, float)
    print("SentimentAnalyzer test passed.")

if __name__ == "__main__":
    test_sentiment_analyzer()
""",
    f"{project_name}/strategy/decision_engine.py": """
import logging

class DecisionEngine:
    def __init__(self, historical_data, sentiment_score):
        self.historical_data = historical_data
        self.sentiment_score = sentiment_score

    def evaluate_stock(self):
        logging.info("Evaluating stock based on historical data and sentiment")
        avg_price = sum(self.historical_data) / len(self.historical_data)
        if avg_price > 105 and self.sentiment_score > 0.2:
            return "Buy"
        elif avg_price < 95 and self.sentiment_score < -0.2:
            return "Sell"
        else:
            return "Hold"
""",
    f"{project_name}/strategy/test_decision_engine.py": """
from decision_engine import DecisionEngine

def test_decision_engine():
    engine = DecisionEngine([100, 102, 101, 105, 110], 0.3)
    decision = engine.evaluate_stock()
    assert decision in ["Buy", "Sell", "Hold"]
    print(f"DecisionEngine test passed with decision: {decision}")

if __name__ == "__main__":
    test_decision_engine()
""",
    f"{project_name}/ethics/ethics_checker.py": """
import logging

class EthicsChecker:
    def __init__(self, sentiment_score):
        self.sentiment_score = sentiment_score

    def check_for_ethical_issues(self):
        logging.info("Performing ethics check")
        if self.sentiment_score > 0.5:
            print("Warning: High positive sentiment. Ensure this is not due to manipulative reporting.")
        elif self.sentiment_score < -0.5:
            print("Warning: High negative sentiment. Avoid trading on potentially false or manipulative news.")
""",
    f"{project_name}/ethics/test_ethics_checker.py": """
from ethics_checker import EthicsChecker

def test_ethics_checker():
    checker = EthicsChecker(0.6)
    checker.check_for_ethical_issues()
    print("EthicsChecker test passed.")

if __name__ == "__main__":
    test_ethics_checker()
""",
    f"{project_name}/cli.py": """
import argparse
import logging
from data.data_fetcher import DataFetcher
from news.news_fetcher import NewsFetcher
from sentiment.sentiment_analyzer import SentimentAnalyzer
from strategy.decision_engine import DecisionEngine
from ethics.ethics_checker import EthicsChecker

logging.basicConfig(level=logging.INFO)

def main(stock_symbol):
    logging.info(f"Running trading bot for {stock_symbol}")
    
    # Fetch historical data
    data_fetcher = DataFetcher(stock_symbol)
    historical_data = data_fetcher.get_historical_data()
    
    # Fetch news data
    news_fetcher = NewsFetcher(stock_symbol)
    news_articles = news_fetcher.get_news()
    
    # Analyze sentiment
    sentiment_analyzer = SentimentAnalyzer()
    sentiment_score = sentiment_analyzer.analyze_sentiment(news_articles)
    
    # Perform ethics check
    ethics_checker = EthicsChecker(sentiment_score)
    ethics_checker.check_for_ethical_issues()
    
    # Make trading decision
    decision_engine = DecisionEngine(historical_data, sentiment_score)
    decision = decision_engine.evaluate_stock()
    
    print(f"Trading decision for {stock_symbol}: {decision}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trading Bot CLI")
    parser.add_argument("symbol", type=str, help="Stock symbol to analyze")
    args = parser.parse_args()
    main(args.symbol)
""",
    f"{project_name}/utils.py": """
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    return logger
"""
}

# Create files with the new modular and testable content
for path, content in files.items():
    with open(path, "w") as file:
        file.write(content)

'''# Creating a zip file of the project
zip_filename = f"{project_name}.zip"
with zipfile.ZipFile(zip_filename, 'w') as zipf:
    for root, dirs, files in os.walk(project_name):
        for file in files:
            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), project_name))

zip_filename'''