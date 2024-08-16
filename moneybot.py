import argparse
import logging
import requests
import numpy as np
import yfinance as yf
import praw
from transformers import pipeline
import config

class Stock:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.company_name = self.get_company_name()
        self.historical_data = []
        self.news = []
        self.market_news = []
        self.sentiment_score_company = None
        self.sentiment_reliability_company = None
        self.sentiment_score_market = None
        self.sentiment_reliability_market = None
        self.technical_score = None
        self.technical_reliability = None
        self.overall_reliability = None

        self.reddit = praw.Reddit(
            client_id=config.API_KEYS['reddit_client_id'],
            client_secret=config.API_KEYS['reddit_client_secret'],
            user_agent=config.API_KEYS['reddit_user_agent']
        )

        self.sentiment_model = self.init_sentiment_model()

    def get_company_name(self):
        try:
            stock = yf.Ticker(self.ticker)
            company_name = stock.info.get('shortName')
            return company_name if company_name else "Unknown Company"
        except Exception as e:
            logging.error(f"Error fetching company name for {self.ticker}: {e}")
            return "Unknown Company"

    def init_sentiment_model(self):
        try:
            device = 0 if config.SETTINGS['use_gpu'] else -1
            sentiment_model = pipeline(
                "sentiment-analysis", 
                model=config.SETTINGS['sentiment_model_name'], 
                device=device
            )
            logging.info("Sentiment model initialized successfully")
            return sentiment_model
        except Exception as e:
            logging.error(f"Error initializing sentiment model: {e}")
            return None

    def fetch_historical_data(self):
        try:
            stock = yf.Ticker(self.ticker)
            self.historical_data = stock.history(period=config.SETTINGS['historical_data_length'])['Close'].tolist()
            logging.info(f"Fetched historical data for {self.ticker}")
        except Exception as e:
            logging.error(f"Error fetching historical data for {self.ticker}: {e}")
            self.historical_data = []

    def fetch_news(self):
        self.news = self.fetch_reddit_news() + self.fetch_company_news_from_gdelt()
        self.market_news = self.fetch_market_news_from_gdelt()

        if not self.news:
            logging.warning(f"No company-specific news found for {self.company_name} ({self.ticker})")
        if not self.market_news:
            logging.warning(f"No market news found for {self.ticker}")

    def fetch_reddit_news(self):
        try:
            subreddit = self.reddit.subreddit(self.ticker.lower())
            posts = subreddit.hot(limit=config.SETTINGS['reddit_posts_limit'])
            news = [post.title for post in posts if not post.stickied]
            logging.info(f"Fetched {len(news)} posts from r/{self.ticker.lower()}")
            return news
        except Exception as e:
            logging.error(f"Error fetching Reddit news for {self.ticker}: {e}")
            return []

    def fetch_company_news_from_gdelt(self):
        return self._fetch_news_from_gdelt(query=self.company_name, context=f"company-specific news for {self.company_name}")

    def fetch_market_news_from_gdelt(self):
        keywords_query = '+OR+'.join(config.SETTINGS['global_market_keywords'])
        return self._fetch_news_from_gdelt(query=keywords_query, context="global market news")

    def _fetch_news_from_gdelt(self, query, context):
        gdelt_url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={query}&mode=artlist&format=json"
        try:
            response = requests.get(gdelt_url)
            response.raise_for_status()
            articles = response.json().get('articles', [])
            news = [article['title'] for article in articles]
            if news:
                logging.info(f"Fetched {len(news)} articles from GDELT for {context}")
            else:
                logging.warning(f"No articles found in GDELT for {context}")
            return news
        except Exception as e:
            logging.error(f"Error fetching GDELT news for {context}: {e}")
            return []

    def analyze_sentiment(self, texts):
        if not self.sentiment_model:
            logging.error("Sentiment analysis model not initialized.")
            return 0, 0
        
        max_length = config.SETTINGS['sentiment_max_length']
        truncated_texts = [text[:max_length] for text in texts]

        try:
            results = self.sentiment_model(truncated_texts)
            scores = [result['score'] if result['label'] == 'POSITIVE' else -result['score'] for result in results]
            weighted_average_score = sum(scores) / len(scores) if scores else 0
            weighted_avg_stds = np.std(scores) if scores else 0
            reliability = max(0, 100 - (weighted_avg_stds * 100))
            return weighted_average_score, reliability
        except Exception as e:
            logging.error(f"Error analyzing sentiment: {e}")
            return 0, 0

    def calculate_sentiment_score(self):
        if self.news:
            self.sentiment_score_company, self.sentiment_reliability_company = self.analyze_sentiment(self.news)
        else:
            logging.error(f"No news data available to analyze company sentiment for {self.ticker}.")
            self.sentiment_score_company, self.sentiment_reliability_company = 0, 0
        
        if self.market_news:
            self.sentiment_score_market, self.sentiment_reliability_market = self.analyze_sentiment(self.market_news)
        else:
            logging.error(f"No market news data available to analyze market sentiment for {self.ticker}.")
            self.sentiment_score_market, self.sentiment_reliability_market = 0, 0

    def calculate_technical_score(self):
        if not self.historical_data or len(self.historical_data) < 14:
            logging.error(f"Not enough historical data to calculate technical score for {self.ticker}.")
            self.technical_score = 0
            self.technical_reliability = 0
            return
        
        sma_period = 14
        sma = np.mean(self.historical_data[-sma_period:])
        
        delta = np.diff(self.historical_data)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)

        avg_gain = np.mean(gain[-sma_period:])
        avg_loss = np.mean(loss[-sma_period:])

        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        self.technical_score = (sma + rsi) / 2
        self.technical_reliability = max(0, 100 - np.std(self.historical_data))

        logging.info(f"Technical score for {self.ticker}: {self.technical_score}")
        logging.info(f"Technical reliability for {self.ticker}: {self.technical_reliability}%")

    def evaluate(self):
        self.fetch_historical_data()
        self.fetch_news()
        self.calculate_sentiment_score()
        self.calculate_technical_score()

        logging.info(f"Technical score: {self.technical_score}, Technical reliability: {self.technical_reliability}%")
        logging.info(f"Company sentiment score: {self.sentiment_score_company}, Reliability: {self.sentiment_reliability_company}%")
        logging.info(f"Market sentiment score: {self.sentiment_score_market}, Reliability: {self.sentiment_reliability_market}%")

        overall_score = (
            self.technical_score * 0.4 + 
            self.sentiment_score_company * 0.3 + 
            self.sentiment_score_market * 0.3
        )
        overall_reliability = (
            self.technical_reliability * 0.4 + 
            self.sentiment_reliability_company * 0.3 + 
            self.sentiment_reliability_market * 0.3
        )
        
        self.overall_reliability = overall_reliability

        logging.info(f"Overall reliability: {self.overall_reliability}%")
        logging.info(f"Overall score: {overall_score}")

        if overall_reliability < config.SETTINGS['reliability_threshold']:
            logging.warning("Low reliability score. Decision: Hold")
            return "Hold"
        
        if overall_score > config.SETTINGS['buy_threshold']:
            return "Buy"
        elif overall_score < config.SETTINGS['sell_threshold']:
            return "Sell"
        else:
            return "Hold"

if __name__ == "__main__":
    # Set up argument parsing for the stock symbols
    parser = argparse.ArgumentParser(description="Run the trading bot for specific stock tickers.")
    parser.add_argument("symbols", nargs='+', help="Stock symbols to analyze")
    args = parser.parse_args()

    # Configure logging level
    logging.basicConfig(level=config.SETTINGS['logging_level'])

    # Analyze each stock symbol provided
    for symbol in args.symbols:
        stock = Stock(symbol)
        decision = stock.evaluate()
        print(f"Final decision for {symbol}: {decision}")
