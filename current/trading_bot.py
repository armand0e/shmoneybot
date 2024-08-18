import schedule
import time
import logging

# Importing necessary modules from other scripts (assuming they are in the same directory)
from basic_info import StockBasicInfo
from financial_data import StockFinancialData
from technical_data import StockTechnicalData
from sentiment_analysis import SentimentAnalysis
from risk_management import RiskManagement

logging.basicConfig(level=logging.INFO)

class TradingBot:
    def __init__(self):
        self.portfolio = {}  # Placeholder for portfolio management

    def daily_update(self):
        logging.info("Starting daily update")

        # Example ticker
        ticker = 'AAPL'

        # Gather basic info
        logging.info("Gathering basic information")
        basic_info = StockBasicInfo(ticker)
        basic_info_data = basic_info.get_basic_info()
        logging.info(f"Basic Info: {basic_info_data}")

        # Gather financial data
        logging.info("Gathering financial data")
        financial_data = StockFinancialData(ticker)
        financial_data_info = financial_data.get_financial_data()
        logging.info(f"Financial Data: {financial_data_info}")

        # Gather technical data
        logging.info("Gathering technical data")
        technical_data = StockTechnicalData(ticker)
        sma = technical_data.calculate_sma()
        rsi = technical_data.calculate_rsi()
        logging.info(f"SMA: {sma.tail()}")
        logging.info(f"RSI: {rsi.tail()}")

        # Perform sentiment analysis
        logging.info("Performing sentiment analysis")
        sentiment_analyzer = SentimentAnalysis()
        texts = ["This stock is amazing!", "Terrible results, wouldn't buy."]
        sentiments = sentiment_analyzer.analyze_sentiment(texts)
        normalized_scores = sentiment_analyzer.normalize_scores(sentiments)
        logging.info(f"Sentiments: {sentiments}")
        logging.info(f"Normalized Scores: {normalized_scores}")

        # Evaluate risk (example with dummy portfolio data)
        logging.info("Evaluating risk")
        stock_info = {'name': ticker, 'sector': basic_info_data['sector']}
        risk_manager = RiskManagement()
        risk_status = risk_manager.evaluate_risk(self.portfolio, stock_info)
        logging.info(f"Risk Status: {risk_status}")

        logging.info("Daily update complete")

    def run(self):
        logging.info("Starting trading bot")
        schedule.every().day.at("09:00").do(self.daily_update)
        self.daily_update()  # Run once immediately for demonstration
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
    
    