from sqlalchemy import create_engine, Column, String, Float, Integer, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.logger import get_logger

logger = get_logger('Database')

Base = declarative_base()

class StockData(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False)
    name = Column(String)
    sector = Column(String)
    description = Column(Text)
    market_cap = Column(Float)
    volume = Column(Float)
    pe_ratio = Column(Float)
    eps = Column(Float)
    revenue = Column(Float)
    rsi = Column(Float)
    sma = Column(Float)
    sentiment_score = Column(Float)
    date = Column(Date)

class Database:
    def __init__(self, db_url='sqlite:///trading_bot.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_stock_data(self, stock_data):
        session = self.Session()
        try:
            session.add(StockData(**stock_data))
            session.commit()
            logger.info(f"Stock data saved for {stock_data['ticker']}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save stock data: {str(e)}")
        finally:
            session.close()

    def load_stock_data(self, ticker):
        session = self.Session()
        try:
            stock = session.query(StockData).filter_by(ticker=ticker).all()
            logger.info(f"Loaded stock data for {ticker}")
            return stock
        except Exception as e:
            logger.error(f"Failed to load stock data for {ticker}: {str(e)}")
            return None
        finally:
            session.close()

logger.info("Database module initialized")