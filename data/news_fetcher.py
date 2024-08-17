import requests
from utils.logger import get_logger

logger = get_logger('NewsFetcher')

class NewsFetcher:
    def __init__(self, gnews_api_key):
        self.api_key = gnews_api_key
        self.endpoint = "https://gnews.io/api/v4/search"

    def fetch_market_news(self, query="stock market", lang="en", country="us"):
        try:
            params = {
                'q': query,
                'lang': lang,
                'country': country,
                'token': self.api_key,
                'max': 100
            }
            response = requests.get(self.endpoint, params=params)
            response.raise_for_status()
            news_data = response.json().get('articles', [])
            logger.info(f"Fetched {len(news_data)} news articles for query: {query}")
            return news_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch market news: {str(e)}")
            return []

logger.info("NewsFetcher module initialized")