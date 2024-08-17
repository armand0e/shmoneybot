import json
from data.data_fetcher import DataFetcher
from data.news_fetcher import NewsFetcher
from data.database import Database
from models.sentiment_model import SentimentModel
from models.technical_model import TechnicalModel
from strategies.trading_strategy import TradingStrategy
from strategies.risk_management import RiskManager
from utils.logger import get_logger

logger = get_logger('Main')

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

    data_fetcher = DataFetcher(config['twitter_api_keys'], config['reddit_api_keys'])
    news_fetcher = NewsFetcher(config['gnews_api_key'])
    database = Database()
    sentiment_model = SentimentModel(config['model_paths']['sentiment_model'])
    technical_model = TechnicalModel()
    risk_manager = RiskManager()
    trading_strategy = TradingStrategy(sentiment_model, technical_model, risk_manager)

    for ticker in config['tickers']:
        logger.info(f"Processing ticker: {ticker}")
        stock_data = data_fetcher.fetch_stock_data(ticker)
        logger.debug(f"Stock data for {ticker}: {stock_data}")
        social_data = data_fetcher.fetch_social_media_data(ticker)
        logger.debug(f"Social data for {ticker}: {social_data}")

        if stock_data and social_data:
            if trading_strategy.evaluate_stock(stock_data, social_data):
                trading_strategy.execute_trade(ticker, config['investment_amount'], config['portfolio_value'])
        else:
            logger.warning(f"Failed to fetch data for ticker: {ticker}")

    logger.info("Completed processing all tickers.")

if __name__ == "__main__":
    main()