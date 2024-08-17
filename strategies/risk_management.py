from utils.logger import get_logger

logger = get_logger('RiskManager')

class RiskManager:
    def __init__(self, max_stock_allocation=0.05, max_sector_allocation=0.20):
        self.max_stock_allocation = max_stock_allocation
        self.max_sector_allocation = max_sector_allocation
        self.portfolio = {}  # This should be managed with a database or similar in production

    def is_viable(self, score):
        # Placeholder for risk-based evaluation of stock viability
        logger.debug(f"Evaluating stock viability with score {score}")
        return score >= 0.5  # Example threshold for viability

    def manage_risk(self, stock_ticker, stock_sector, investment_amount, portfolio_value):
        if self._exceeds_stock_allocation(stock_ticker, investment_amount, portfolio_value):
            logger.warning(f"Investment in {stock_ticker} exceeds maximum stock allocation")
            return False
        if self._exceeds_sector_allocation(stock_sector, investment_amount, portfolio_value):
            logger.warning(f"Investment in {stock_sector} sector exceeds maximum sector allocation")
            return False
        logger.info(f"Investment in {stock_ticker} approved under risk management strategy")
        return True

    def _exceeds_stock_allocation(self, ticker, amount, portfolio_value):
        current_investment = self.portfolio.get(ticker, 0)
        new_allocation = (current_investment + amount) / portfolio_value
        return new_allocation > self.max_stock_allocation

    def _exceeds_sector_allocation(self, sector, amount, portfolio_value):
        current_sector_investment = sum(value for key, value in self.portfolio.items() if key.startswith(sector))
        new_allocation = (current_sector_investment + amount) / portfolio_value
        return new_allocation > self.max_sector_allocation

logger.info("RiskManager module initialized")