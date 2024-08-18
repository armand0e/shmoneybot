import json
import logging
from data_fetcher import FinancialDataFetcher
from news_fetcher import RedditNewsFetcher, GDELTFetcher
from sentiment_model import AdvancedSentimentAnalyzer
from scipy.stats import zscore

def evaluate_stock_viability(sentiment_score, outlook_score, sentiment_threshold=60, outlook_threshold=60):
    normalized_sentiment_score = zscore([sentiment_score]) * 50 + 50  # Normalize to 0-100 scale
    normalized_outlook_score = zscore([outlook_score]) * 50 + 50

    if normalized_sentiment_score > sentiment_threshold and normalized_outlook_score > outlook_threshold:
        return True
    return False


logger = logging.getLogger('Main')

def load_config(config_file='config.json'):
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
        logger.info("Configuration loaded successfully")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file {config_file} not found.")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        raise

def main():
    config = load_config()

    data_fetcher = FinancialDataFetcher(historical_data_length=config['historical_data_length'])
    reddit_fetcher = RedditNewsFetcher(config['reddit_api_keys'], posts_limit=config['reddit_posts_limit'])
    gdelt_fetcher = GDELTFetcher(config['gdelt_api_key'])
    sentiment_analyzer = AdvancedSentimentAnalyzer(
        model_name=config['sentiment_analysis']['model_name'],
        device=config['sentiment_analysis']['device'], max_length=config['sentiment_analysis']['max_length'])
    viable_stocks = []

    for ticker in config['tickers']:
        logger.info(f"Processing ticker: {ticker}")

        # Fetch financial data
        financial_data = data_fetcher.fetch_financial_data(ticker)
        if not financial_data:
            logger.warning(f"Skipping {ticker} due to missing financial data")
            continue

        # Fetch and analyze social media data
        reddit_posts = reddit_fetcher.fetch_reddit_posts(ticker)
        sentiment_score, reliability = sentiment_analyzer.analyze_sentiment(reddit_posts)

        if sentiment_score is not None:
            logger.info(f"Ticker {ticker}: Sentiment Score: {sentiment_score}, Reliability: {reliability}")

        # Fetch global market news
        global_news = gdelt_fetcher.fetch_news(config['global_market_keywords'])
        logger.debug(f"Global market news: {global_news}")

        outlook_score = ...  # Future outlook analysis logic

        # Evaluate stock viability
        if evaluate_stock_viability(sentiment_score, outlook_score):
            viable_stocks.append(ticker)

    logger.info(f"Viable stocks: {viable_stocks}")
    logger.info("Completed processing all tickers.")