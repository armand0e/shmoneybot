from utils.logger import get_logger

logger = get_logger('TradingStrategy')

class TradingStrategy:
    def __init__(self, sentiment_model, technical_model, risk_manager):
        self.sentiment_model = sentiment_model
        self.technical_model = technical_model
        self.risk_manager = risk_manager
        self.viable_stocks = []

    def evaluate_stock(self, stock_data, social_data):
        sentiment_score, sentiment_reliability = self.sentiment_model.analyze_sentiment(social_data)
        technical_score, technical_reliability = self.technical_model.analyze_technical(stock_data)

        if sentiment_score is None or technical_score is None:
            logger.error(f"Failed to evaluate stock {stock_data['info']['ticker']}")
            return False

        overall_score = (sentiment_score + technical_score) / 2
        logger.info(f"Evaluated stock {stock_data['info']['ticker']} with overall score {overall_score}")

        if self.risk_manager.is_viable(overall_score):
            self.viable_stocks.append(stock_data['info']['ticker'])
            logger.info(f"Stock {stock_data['info']['ticker']} is viable for trading")
            return True
        return False

    def execute_trade(self, ticker, investment_amount, portfolio_value):
        stock_data = self.get_stock_data(ticker)  # Assume you have a method to get stock data
        stock_sector = stock_data['info']['sector']

        if self.risk_manager.manage_risk(ticker, stock_sector, investment_amount, portfolio_value):
            # Execute buy/sell trade based on the strategy
            logger.info(f"Trade executed for {ticker}")
            return True
        logger.warning(f"Trade not executed for {ticker} due to risk management constraints")
        return False

    def get_stock_data(self, ticker):
        # Placeholder method to fetch stock data; this should integrate with your data module
        pass

logger.info("TradingStrategy module initialized")