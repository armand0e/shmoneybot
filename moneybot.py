import argparse
import logging
import requests
import numpy as np
import yfinance as yf
import praw
import scipy as sc
from transformers import pipeline
import config

class Stock:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.company_name = self.get_company_name()
        self.historical_data = []
        self.news = []
        self.company_news = []
        self.market_news = []
        self.technical_score = None
        self.technical_reliability = None
        self.sentiment_score_company = None
        self.sentiment_reliability_company = None
        self.sentiment_score_company_news = None
        self.sentiment_reliability_company_news = None
        self.sentiment_score_market = None
        self.sentiment_reliability_market = None

        self.reddit = praw.Reddit(
            client_id=config.API_KEYS['reddit_client_id'],
            client_secret=config.API_KEYS['reddit_client_secret'],
            user_agent=config.API_KEYS['reddit_user_agent']
        )

        self.market_sentiment_model, self.company_sentiment_model = self.init_sentiment_models()

    def get_company_name(self):
        try:
            stock = yf.Ticker(self.ticker)
            company_name = stock.info.get('shortName')
            return company_name if company_name else "Unknown Company"
        except Exception as e:
            logging.error(f"Error fetching company name for {self.ticker}: {e}")
            return "Unknown Company"

    def init_sentiment_models(self):
        try:
            device = 0 if config.SETTINGS['use_gpu'] else -1

            # Initialize FinBERT for market and company-specific news sentiment
            market_sentiment_model = pipeline(
                "sentiment-analysis", 
                model="yiyanghkust/finbert-tone",  # FinBERT model for financial sentiment
                device=device
            )
            logging.info("Market and company news sentiment model (FinBERT) initialized successfully")

            # Initialize Twitter RoBERTa for Reddit/social sentiment
            company_sentiment_model = pipeline(
                "sentiment-analysis", 
                model="cardiffnlp/twitter-roberta-base-sentiment",  # Twitter RoBERTa model for social sentiment
                device=device
            )
            logging.info("Company sentiment model (Twitter RoBERTa) initialized successfully")

            return market_sentiment_model, company_sentiment_model

        except Exception as e:
            logging.error(f"Error initializing sentiment models: {e}")
            return None, None

    def fetch_historical_data(self):
        try:
            stock = yf.Ticker(self.ticker)
            self.historical_data = stock.history(period=config.SETTINGS['historical_data_length'])['Close'].tolist()
            logging.info(f"Fetched historical data for {self.ticker}")
        except Exception as e:
            logging.error(f"Error fetching historical data for {self.ticker}: {e}")
            self.historical_data = []

    def fetch_news_with_retry(self, retries=3):
        for attempt in range(retries):
            self.fetch_news()
            if self.news or self.company_news or self.market_news:
                return  # Exit if we have any news
            logging.warning(f"Retrying news fetch for {self.ticker}... (attempt {attempt + 1})")
        logging.error(f"Failed to fetch news after {retries} attempts for {self.ticker}")

    def fetch_news(self):
        self.news = self.fetch_reddit_news()
        self.company_news = self.fetch_company_news_from_gdelt()
        self.market_news = self.fetch_market_news_from_gdelt()

        if not self.news:
            logging.warning(f"No Reddit news found for {self.company_name} ({self.ticker})")
        if not self.company_news:
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

            # Check if the response is in JSON format
            if 'application/json' in response.headers.get('Content-Type', ''):
                articles = response.json().get('articles', [])
                news = [article['title'] for article in articles]
                if news:
                    logging.info(f"Fetched {len(news)} articles from GDELT for {context}")
                else:
                    logging.warning(f"No articles found in GDELT for {context}")
                return news
            else:
                logging.error(f"Unexpected content type from GDELT: {response.headers['Content-Type']}")
                return []

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching GDELT news for {context}: {e}")
            return []

    def analyze_sentiment(self, texts, model_type='company'):
        if model_type == 'company' and not self.company_sentiment_model:
            logging.error("Company sentiment analysis model not initialized.")
            return 0, 0
        elif model_type == 'market' and not self.market_sentiment_model:
            logging.error("Market sentiment analysis model not initialized.")
            return 0, 0
        
        try:
            if model_type == 'company':
                results = self.company_sentiment_model(texts)
            else:  # market or company-specific news
                results = self.market_sentiment_model(texts)

            scores = []
            for result in results:
                label = result['label']
                if model_type == 'company':  # Twitter RoBERTa
                    if label == 'LABEL_2':  # Positive
                        scores.append(result['score'])
                    elif label == 'LABEL_0':  # Negative
                        scores.append(-result['score'])
                    else:  # Neutral
                        scores.append(0)
                else:  # FinBERT (Market or Company news)
                    if label == 'positive':
                        scores.append(result['score'])
                    elif label == 'negative':
                        scores.append(-result['score'])
                    else:  # Neutral
                        scores.append(0)

            weighted_average_score = sum(scores) / len(scores) if scores else 0
            weighted_avg_stds = np.std(scores) if scores else 0
            reliability = max(0, 100 - (weighted_avg_stds * 100))
            logging.debug(f"{scores}")
            return weighted_average_score, reliability
        except Exception as e:
            logging.error(f"Error analyzing {model_type} sentiment: {e}")
            return 0, 0

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

    def evaluate_technical(self):
        self.calculate_technical_score()
        if self.technical_reliability < config.SETTINGS['reliability_threshold']:
            logging.warning("Low technical reliability. Decision: Hold (Technical)")
            return "Hold"
        
        if self.technical_score > config.SETTINGS['buy_threshold']:
            return "Buy"
        elif self.technical_score < config.SETTINGS['sell_threshold']:
            return "Sell"
        else:
            return "Hold"

    def evaluate_company_sentiment(self):
        if self.news:
            self.sentiment_score_company, self.sentiment_reliability_company = self.analyze_sentiment(self.news, model_type='company')
        else:
            logging.error(f"No Reddit news data available to analyze company sentiment for {self.ticker}.")
            self.sentiment_score_company, self.sentiment_reliability_company = 0, 0

        if self.sentiment_reliability_company < config.SETTINGS['reliability_threshold']:
            logging.warning("Low company sentiment reliability. Decision: Hold (Company Sentiment)")
            return "Hold"
        
        if self.sentiment_score_company > config.SETTINGS['buy_threshold']:
            return "Buy"
        elif self.sentiment_score_company < config.SETTINGS['sell_threshold']:
            return "Sell"
        else:
            return "Hold"

    def evaluate_market_sentiment(self):
        if self.market_news:
            self.sentiment_score_market, self.sentiment_reliability_market = self.analyze_sentiment(self.market_news, model_type='market')
        else:
            logging.error(f"No market news data available to analyze market sentiment for {self.ticker}.")
            self.sentiment_score_market, self.sentiment_reliability_market = 0, 0

        if self.sentiment_reliability_market < config.SETTINGS['reliability_threshold']:
            logging.warning("Low market sentiment reliability. Decision: Hold (Market Sentiment)")
            return "Hold"
        
        if self.sentiment_score_market > config.SETTINGS['buy_threshold']:
            return "Buy"
        elif self.sentiment_score_market < config.SETTINGS['sell_threshold']:
            return "Sell"
        else:
            return "Hold"

    def final_evaluate(self, technical_decision, company_sentiment_decision, market_sentiment_decision, weights=None):
        if not weights:
            weights = {
                'technical': 0.4,
                'company_sentiment': 0.3,
                'market_sentiment': 0.3
            }
        
        decisions = {
            'Buy': 0,
            'Hold': 0,
            'Sell': 0
        }

        decisions[technical_decision] += weights['technical']
        decisions[company_sentiment_decision] += weights['company_sentiment']
        decisions[market_sentiment_decision] += weights['market_sentiment']

        final_decision = max(decisions, key=decisions.get)
        logging.info(f"Final weighted decision: {final_decision} (Buy: {decisions['Buy']}, Hold: {decisions['Hold']}, Sell: {decisions['Sell']})")
        return final_decision

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the trading bot for specific stock tickers.")
    parser.add_argument("symbols", nargs='+', help="Stock symbols to analyze")
    args = parser.parse_args()

    logging.basicConfig(level=config.SETTINGS['logging_level'])

    for symbol in args.symbols:
        stock = Stock(symbol)

        # Evaluate each aspect
        technical_decision = stock.evaluate_technical()
        company_sentiment_decision = stock.evaluate_company_sentiment()
        market_sentiment_decision = stock.evaluate_market_sentiment()

        # Get final decision
        final_decision = stock.final_evaluate(technical_decision, company_sentiment_decision, market_sentiment_decision)

        print(f"Final decision for {symbol}: {final_decision}")
