import numpy as np
from scipy.stats import zscore
from utils.logger import get_logger

logger = get_logger('TechnicalModel')

class TechnicalModel:
    def __init__(self):
        pass  # No need for complex initialization

    def analyze_technical(self, stock_data):
        try:
            rsi = self._calculate_rsi(stock_data['history'])
            sma = self._calculate_sma(stock_data['history'])
            technical_score = self._combine_technical_scores(rsi, sma)
            normalized_score = np.mean(zscore(technical_score))
            reliability = np.std(technical_score)
            logger.info(f"Technical analysis completed with score {normalized_score} and reliability {reliability}")
            return normalized_score, reliability
        except Exception as e:
            logger.error(f"Technical analysis failed: {str(e)}")
            return None, None

    def _calculate_rsi(self, history):
        delta = history['Close'].diff()
        gain = (delta.where(delta > 0, 0)).mean()
        loss = (-delta.where(delta < 0, 0)).mean()
        rs = gain / loss if loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        logger.debug(f"RSI calculated: {rsi}")
        return rsi

    def _calculate_sma(self, history, period=14):
        sma = history['Close'].rolling(window=period).mean().iloc[-1]
        logger.debug(f"SMA calculated: {sma}")
        return sma

    def _combine_technical_scores(self, rsi, sma):
        return [rsi, sma]

logger.info("TechnicalModel module initialized")