import logging

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class RiskManagement:
    def __init__(self, max_allocation_per_stock=0.1, max_allocation_per_sector=0.3):
        self.max_allocation_per_stock = max_allocation_per_stock
        self.max_allocation_per_sector = max_allocation_per_sector

    def evaluate_risk(self, portfolio, stock_info):
        logger.info(f"Evaluating risk for stock {stock_info['name']} in sector {stock_info['sector']}")

        # Calculate current allocations
        allocation_in_stock = portfolio.get(stock_info['name'], 0)
        allocation_in_sector = sum(
            allocation for stock, allocation in portfolio.items() if stock_info['sector'] in stock
        )

        if allocation_in_stock > self.max_allocation_per_stock:
            logger.warning(f"Overexposure to stock {stock_info['name']}")
            return False, "Overexposure to stock"

        if allocation_in_sector > self.max_allocation_per_sector:
            logger.warning(f"Overexposure to sector {stock_info['sector']}")
            return False, "Overexposure to sector"

        logger.info(f"Allocation is within risk parameters for stock {stock_info['name']}")
        return True, "Allocation is within risk parameters"

# Example usage
if __name__ == "__main__":
    # Example portfolio dictionary with stock allocations (in percentage of total portfolio)
    portfolio = {
        'AAPL': 0.15,  # 15% allocated to Apple
        'MSFT': 0.05,  # 5% allocated to Microsoft
        'GOOGL': 0.05  # 5% allocated to Google
    }

    # Example stock info
    stock_info = {'name': 'AAPL', 'sector': 'Technology'}

    # Initialize RiskManagement
    risk_manager = RiskManagement()

    # Evaluate risk
    risk_status = risk_manager.evaluate_risk(portfolio, stock_info)
    print(risk_status)