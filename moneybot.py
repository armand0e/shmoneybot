#!/usr/bin/env python3
import config
import logging
import requests
import numpy as np
import yfinance as yf
from news import RedditNewsFetcher, GDELTFetcher
from sentiment import AdvancedSentimentAnalyzer

def get_company_name(symbol: str) -> str:
    try:
        stock = yf.Ticker(symbol)
        company_name = stock.info.get('shortName')
        if company_name:
            return company_name
        else:
            return "Unknown Company"
    except Exception as e:
        logging.error(f"Error fetching company name for {symbol}: {e}")
        return "Unknown Company"

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
        self.sentiment_score_company = None
        self.sentiment_reliability_company = None
        self.sentiment_score_market = None
        self.sentiment_reliability_market = None
        self.technical_score = None
        self.technical_reliability = None
        self.news = []
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
        gdelt_fetcher = GDELTFetcher(self.company_name)
        
        self.news = reddit_fetcher.fetch_reddit_news() + gdelt_fetcher.fetch_company_news()
        self.market_news = gdelt_fetcher.fetch_market_news()

        if not self.news:
            logging.warning(f"No company-specific news found for {self.company_name} ({self.ticker})")
        if not self.market_news:
            logging.warning(f"No market news found for {self.ticker}")

    def calculate_sentiment_score(self):
        adv_sentiment_analyzer = AdvancedSentimentAnalyzer()
        
        if self.news:
            self.sentiment_score_company, self.sentiment_reliability_company = adv_sentiment_analyzer.analyze_sentiment(self.news)
        else:
            logging.error(f"No news data available to analyze company sentiment for {self.ticker}.")
            self.sentiment_score_company, self.sentiment_reliability_company = 0, 0
        
        if self.market_news:
            self.sentiment_score_market, self.sentiment_reliability_market = adv_sentiment_analyzer.analyze_sentiment(self.market_news)
        else:
            logging.error(f"No market news data available to analyze market sentiment for {self.ticker}.")
            self.sentiment_score_market, self.sentiment_reliability_market = 0, 0

    def calculate_technical_score(self):
        if not self.historical_data or len(self.historical_data) < 14:  # Need at least 14 data points for RSI
            logging.error(f"Not enough historical data to calculate technical score for {self.ticker}.")
            self.technical_score = 0
            self.technical_reliability = 0
            return
        
        # Calculate Simple Moving Average (SMA)
        sma_period = 14
        sma = np.mean(self.historical_data[-sma_period:])
        
        # Calculate Relative Strength Index (RSI)
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
        
        # Technical Score Calculation (can be a combination of indicators)
        self.technical_score = (sma + rsi) / 2
        
        # Technical Reliability (we keep it simple for now)
        self.technical_reliability = max(0, 100 - np.std(self.historical_data))

        logging.info(f"Technical score for {self.ticker}: {self.technical_score}")
        logging.info(f"Technical reliability for {self.ticker}: {self.technical_reliability}%")

    def evaluate(self):
        # Fetch and calculate all necessary data
        self.fetch_historical_data()
        self.fetch_news()
        self.calculate_sentiment_score()
        self.calculate_technical_score()

        logging.info(f"Technical score: {self.technical_score}, Technical reliability: {self.technical_reliability}%")
        logging.info(f"Company sentiment score: {self.sentiment_score_company}, Reliability: {self.sentiment_reliability_company}%")
        logging.info(f"Market sentiment score: {self.sentiment_score_market}, Reliability: {self.sentiment_reliability_market}%")

        # Weighing technical score, company sentiment, and market sentiment
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

        # Decision based on thresholds
        if overall_reliability < config.SETTINGS['reliability_threshold']:
            logging.warning("Low reliability score. Decision: Hold")
            return "Hold"
        
        if overall_score > config.SETTINGS['buy_threshold']:
            return "Buy"
        elif overall_score < config.SETTINGS['sell_threshold']:
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
    print(f"Final decision for {stock_symbol}: {decision}")

if __name__ == "__main__":
    stock_symbol = input("Enter the stock ticker symbol: ").upper()
    main(stock_symbol)
