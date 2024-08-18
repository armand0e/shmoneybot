
import logging
import config

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, config.SETTINGS['logging_level']))

class RiskManagement:
    def __init__(self, stop_loss_pct=0.05, take_profit_pct=0.10):
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    def evaluate(self, portfolio, ticker, purchase_price, current_price):
        """Evaluate whether to trigger stop-loss or take-profit based on current price."""
        change_pct = (current_price - purchase_price) / purchase_price

        if change_pct <= -self.stop_loss_pct:
            logger.info(f"Stop-Loss triggered for {ticker} - Selling")
            return -1  # Sell Signal
        elif change_pct >= self.take_profit_pct:
            logger.info(f"Take-Profit triggered for {ticker} - Selling")
            return 1  # Sell Signal
        return 0  # No Action
