#!/usr/bin/env python3
# cli.py

import argparse
import logging
from data.data_fetcher import DataFetcher

from data.financial_data_fetcher import FinancialDataFetcher

from news.reddit_news_fetcher import RedditNewsFetcher
from news.gdelt_fetcher import GDELTFetcher

from news.web_scraper import WebScraper

from sentiment.sentiment_analyzer import SentimentAnalyzer

from sentiment.advanced_sentiment_analyzer import AdvancedSentimentAnalyzer

from strategy.decision_engine import DecisionEngine
from ethics.ethics_checker import EthicsChecker

# Set up logging
logging.basicConfig(level=logging.INFO)

def main(stock_symbol):
    logging.info(f"Running trading bot for {stock_symbol}")

    # Step 1: Fetch historical data

    # Fetch real-time financial data
    financial_fetcher = FinancialDataFetcher(stock_symbol)
    real_time_data = financial_fetcher.get_realtime_data()
    logging.info(f"Real-time data: {real_time_data}")

    data_fetcher = DataFetcher(stock_symbol)
    historical_data = data_fetcher.get_historical_data()
    logging.info("Historical data fetched successfully")

    # Step 2: Fetch news data from Reddit

    ## Fetch live news using Web Scraper
    scraper = WebScraper("https://www.cnbc.com/world/?region=world")
    live_news = scraper.fetch_news()
    logging.info(f"Live news: {live_news}")

    # Fetch news data from Reddit
    reddit_fetcher = RedditNewsFetcher(stock_symbol)
    reddit_news = reddit_fetcher.fetch_reddit_news()
    logging.info("Reddit news fetched successfully")

    # Fetch GDELT tone chart
    gdelt_fetcher = GDELTFetcher(stock_symbol)
    gdelt_tone_chart = gdelt_fetcher.fetch_gdelt_tone_chart()
    logging.info("GDELT tone chart fetched successfully")

    # Analyze Reddit news sentiment with Advanced Sentiment Analyzer
    adv_sentiment_analyzer = AdvancedSentimentAnalyzer()
    reddit_sentiment_score = adv_sentiment_analyzer.analyze_sentiment(reddit_news)
    logging.info(f"Reddit sentiment score: {reddit_sentiment_score}")

    # Optionally, handle GDELT tone chart separately in a distinct manner
    # For example, the tone chart could be used as an additional factor in the decision engine
    gdelt_sentiment_analyzer = SentimentAnalyzer()  # Or create a specific analyzer for GDELT data
    gdelt_sentiment_score = gdelt_sentiment_analyzer.analyze_sentiment(gdelt_tone_chart)
    logging.info(f"GDELT sentiment score: {gdelt_sentiment_score}")
    
    news_sentiment_score = ( 0.6 * gdelt_sentiment_score ) + ( 0.4 * reddit_sentiment_score)

# Combine or compare sentiment scores as necessary
    # Step 5: Perform ethics check
    ethics_checker = EthicsChecker(news_sentiment_score)
    ethics_checker.check_for_ethical_issues()

    # Step 6: Make trading decision
    decision_engine = DecisionEngine(historical_data, news_sentiment_score)
    decision = decision_engine.evaluate_stock()
    logging.info(f"Trading decision: {decision}")

    # Output the decision
    print(f"Trading decision for {stock_symbol}: {decision}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trading Bot CLI")
    parser.add_argument("symbol", type=str, help="Stock symbol to analyze")
    args = parser.parse_args()
    main(args.symbol)

# Debugging Instructions:
# - Run the CLI with different stock symbols to ensure all steps execute correctly.
# - Check logs for detailed output at each step.
# - Test each module (data fetching, news, sentiment analysis, decision engine) independently using the provided test scripts.