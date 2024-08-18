import yfinance as yf
import logging
import pandas as pd

logger = logging.getLogger('DataFetcher')

class FinancialDataFetcher:
    def __init__(self, historical_data_length="5y"):
        self.historical_data_length = historical_data_length
        logger.info("FinancialDataFetcher initialized")

    def get_basic_info(self, ticker):
        stock = yf.Ticker(ticker)
        info = stock.info
        basic_info = {
            'name': info.get('shortName'),
            'sector': info.get('sector'),
            'description': info.get('longBusinessSummary'),
            'market_cap_rank': info.get('marketCap')
        }
        return basic_info

    def get_financial_data(self, ticker):
        stock = yf.Ticker(ticker)
        financial_data = {
            'current_volume': stock.info.get('volume'),
            'p_e_ratio': stock.info.get('trailingPE'),
            'eps': stock.info.get('trailingEps'),
            'market_cap': stock.info.get('marketCap'),
            'revenue': stock.financials.loc['Total Revenue'].iloc[0] if not stock.financials.empty else None,
            'open_interest_calls': None,  # Needs to be gathered via an options-specific API
            'open_interest_puts': None,  # Needs to be gathered via an options-specific API
            'earnings_data': stock.earnings,
            'earnings_reports': stock.quarterly_earnings  # This might need refinement to get full reports
        }
        return financial_data

    def get_technical_indicators(self, ticker):
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        sma = hist['Close'].rolling(window=50).mean()
        
        return {
            'RSI': rsi.iloc[-1],
            'SMA': sma.iloc[-1]
        }

    def fetch_financial_data(self, ticker):
        basic_info = self.get_basic_info(ticker)
        financial_data = self.get_financial_data(ticker)
        technical_indicators = self.get_technical_indicators(ticker)
        
        return {
            'ticker': ticker,
            'basic_info': basic_info,
            'financial_data': financial_data,
            'technical_indicators': technical_indicators
        }