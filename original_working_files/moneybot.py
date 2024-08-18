#!/usr/bin/env python3
import config
import logging
import requests
import numpy as np
import yfinance as yf
from news import RedditNewsFetcher, GDELTFetcher
from sentiment import AdvancedSentimentAnalyzer

def get_company_name(symbol):
    pass


class FinancialDataFetcher:
    def __init__(self, ticker):
        self.ticker = ticker

    def get_realtime_data(self):
        try:
            logging.info(f"Fetching real-time data for {self.ticker}")
            stock = yf.Ticker(self.ticker)
            data = stock.history(period="1d").iloc[0].to_dict()
            logging.info(f"Real-time data fetched successfully for {self.ticker}")
            return data
        except Exception as e:
            logging.error(f"Error fetching real-time data for {self.ticker}: {e}")
            return {}

    def get_historical_data(self, period=None):
        period = period if period else config.SETTINGS['historical_data_length']
        try:
            logging.info(f"Fetching historical data for {self.ticker} for period: {period}")
            stock = yf.Ticker(self.ticker)
            hist = stock.history(period=period)
            historical_data = hist['Close'].tolist()  # Fetching closing prices
            logging.info(f"Historical data fetched successfully for {self.ticker}")
            return historical_data
        except Exception as e:
            logging.error(f"Error fetching historical data for {self.ticker}: {e}")
            return []

class Stock:
    def __init__(self, ticker, company_name):
        self.ticker = ticker
        self.company_name = company_name
        self.sentiment_score = None
        self.sentiment_reliability = None
        self.technical_score = None
        self.technical_reliability = None
        self.news = []
        self.historical_data = []
        self.market_news = []
        self.overall_reliability = None

    def fetch_historical_data(self):
        financial_fetcher = FinancialDataFetcher(self.ticker)
        self.historical_data = financial_fetcher.get_historical_data()
        if not self.historical_data:
            logging.error(f"No historical data found for {self.ticker}")
        else:
            logging.info(f"Historical data for {self.ticker} fetched successfully")

    def fetch_news(self):
        reddit_fetcher = RedditNewsFetcher(self.company_name)
        self.news = reddit_fetcher.fetch_reddit_news()
        logging.info(f"News for {self.company_name} fetched successfully")

    def fetch_world_news(self):
        gdelt_fetcher = GDELTFetcher()
        self.market_news = gdelt_fetcher.fetch_gdelt_news()
        logging.info(f"Market news related to world events fetched successfully")

    def calculate_sentiment_score(self):
        adv_sentiment_analyzer = AdvancedSentimentAnalyzer()
        self.sentiment_score, self.sentiment_reliability = adv_sentiment_analyzer.analyze_sentiment(self.news)
        logging.info(f"Sentiment score for {self.ticker}: {self.sentiment_score}")
        logging.info(f"Sentiment reliability for {self.ticker}: {self.sentiment_reliability}%")

    def calculate_technical_score(self):
        if not self.historical_data or len(self.historical_data) < 2:
            logging.error(f"Not enough historical data to calculate technical score for {self.ticker}.")
            self.technical_score = 0
            self.technical_reliability = 0
            return

        self.technical_score = sum(self.historical_data) / len(self.historical_data) if self.historical_data else 0
        try:
            self.technical_reliability = max(0, 100 - (np.std(self.historical_data, ddof=1) * 100))
        except Exception as e:
            logging.error(f"Error calculating standard deviation for {self.ticker}: {e}")
            self.technical_reliability = 0

        logging.info(f"Technical score for {self.ticker}: {self.technical_score}")
        logging.info(f"Technical reliability for {self.ticker}: {self.technical_reliability}%")

    def calculate_overall_reliability(self):
        self.overall_reliability = (self.sentiment_reliability + self.technical_reliability) / 2
        logging.info(f"Overall reliability for {self.ticker}: {self.overall_reliability}%")

    def evaluate(self):
        # Fetch and calculate all necessary data
        self.fetch_historical_data()
        self.fetch_news()
        self.fetch_world_news()
        self.calculate_sentiment_score()
        self.calculate_technical_score()
        self.calculate_overall_reliability()

        logging.info("Evaluating stock based on historical data, sentiment, and overall reliability")

        # Ensure historical data is available
        if not self.historical_data:
            logging.error("Historical data is empty. Unable to evaluate stock.")
            return "Hold"

        # Calculate the average price
        avg_price = sum(self.historical_data) / len(self.historical_data)
        logging.info(f"Average historical price: {avg_price}")
        logging.info(f"Sentiment score: {self.sentiment_score}")
        logging.info(f"Overall reliability: {self.overall_reliability}%")

        # Use thresholds from config
        if self.overall_reliability < config.SETTINGS['reliability_threshold']:
            logging.warning("Low reliability score. Decision: Hold")
            return "Hold"
        
        if avg_price > 105 and self.sentiment_score > config.SETTINGS['buy_threshold']:
            return "Buy"
        elif avg_price < 95 and self.sentiment_score < config.SETTINGS['sell_threshold']:
            return "Sell"
        else:
            return "Hold"

def main(stock_symbol):
    # Fetch the company name using the get_symbol function
    company_name = get_company_name(stock_symbol)

    # Initialize the Stock object
    stock = Stock(stock_symbol, company_name)

    # Evaluate the stock (this will fetch data, calculate scores, and return a decision)
    decision = stock.evaluate()

    # Log and print the final decision
    logging.info(f"Final decision for {stock_symbol}: {decision}")
    print(f"Trading decision for {stock_symbol}: {decision}")

if __name__ == "__main__":
    import argparse

    # Set up argument parsing for the stock symbol
    parser = argparse.ArgumentParser(description="Run the trading bot for a specific stock.")
    parser.add_argument("symbol", help="Stock symbol to analyze")
    args = parser.parse_args()

    # Configure logging level
    logging.basicConfig(level=config.SETTINGS['logging_level'])

    # Run the main function with the provided stock symbol
    main(args.symbol)
