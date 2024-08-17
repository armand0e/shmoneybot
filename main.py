from data.data_fetcher import DataFetcher
from data.news_fetcher import NewsFetcher
from data.database import Database
from models.sentiment_model import SentimentModel
from models.technical_model import TechnicalModel
from strategies.trading_strategy import TradingStrategy
from strategies.risk_management import RiskManager
from utils.backtesting import Backtester
from utils.logger import get_logger
import json

logger = get_logger('Main')

def load_config(config_file='config.json'):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config

def main():
    # Load configuration
    config = load_config()

    # Initialize components with config values
    data_fetcher = DataFetcher(config['twitter_api_keys'], config['reddit_api_keys'])
    news_fetcher = NewsFetcher(config['gnews_api_key'])
    database = Database()
    sentiment_model = SentimentModel(config['model_paths']['sentiment_model'])
    technical_model = TechnicalModel()
    risk_manager = RiskManager()
    trading_strategy = TradingStrategy(sentiment_model, technical_model, risk_manager)

    # Process each ticker in the config
    for ticker in config['tickers']:
        stock_data = data_fetcher.fetch_stock_data(ticker)
        social_data = data_fetcher.fetch_social_media_data(ticker)

        if stock_data and social_data:
            if trading_strategy.evaluate_stock(stock_data, social_data):
                trading_strategy.execute_trade(ticker, config['investment_amount'], config['portfolio_value'])

    # Backtesting
    historical_data = {}  # Load your historical data here
    backtester = Backtester(trading_strategy, historical_data)
    backtester.run_backtest()

if __name__ == "__main__":
    main()