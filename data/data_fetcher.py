import yfinance as yf
import tweepy
import praw
from utils.logger import get_logger

logger = get_logger('DataFetcher')

class DataFetcher:
    def __init__(self, twitter_api_keys, reddit_api_keys):
        self.twitter_api = self._init_twitter(twitter_api_keys)
        self.reddit_api = self._init_reddit(reddit_api_keys)

    def _init_twitter(self, api_keys):
        auth = tweepy.OAuthHandler(api_keys['api_key'], api_keys['api_secret'])
        auth.set_access_token(api_keys['access_token'], api_keys['access_secret'])
        return tweepy.API(auth, wait_on_rate_limit=True)

    def _init_reddit(self, api_keys):
        return praw.Reddit(
            client_id=api_keys['client_id'],
            client_secret=api_keys['client_secret'],
            user_agent=api_keys['user_agent']
        )

    def fetch_stock_data(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            return {
                'info': stock.info,
                'history': stock.history(period="5y"),
                'earnings': stock.earnings,
                'balance_sheet': stock.balance_sheet,
                'financials': stock.financials,
                'cashflow': stock.cashflow,
            }
        except Exception as e:
            logger.error(f"Failed to fetch data for {ticker}: {str(e)}")
            return None

    def fetch_social_media_data(self, ticker):
        try:
            reddit_posts = self._fetch_reddit_posts(ticker)
            twitter_posts = self._fetch_twitter_posts(ticker)
            return reddit_posts, twitter_posts
        except Exception as e:
            logger.error(f"Failed to fetch social media data for {ticker}: {str(e)}")
            return None, None

    def _fetch_reddit_posts(self, ticker):
        subreddit_name = self._find_subreddit(ticker)
        if subreddit_name:
            subreddit = self.reddit_api.subreddit(subreddit_name)
            return [{'title': post.title, 'date': post.created_utc} for post in subreddit.hot(limit=20)]
        else:
            logger.warning(f"No relevant subreddit found for {ticker}")
            return []

    def _fetch_twitter_posts(self, ticker):
        try:
            query = f'{ticker} -filter:retweets'
            tweets = tweepy.Cursor(self.twitter_api.search_tweets, q=query, tweet_mode='extended', lang='en').items(20)
            return [{'text': tweet.full_text, 'date': tweet.created_at} for tweet in tweets]
        except Exception as e:
            logger.error(f"Error fetching Twitter posts for {ticker}: {str(e)}")
            return []

    def _find_subreddit(self, ticker):
        # Implement logic to find the relevant subreddit for the stock ticker
        # For example, you might map known tickers to specific subreddits or search based on the company name
        # This is a placeholder function
        return ticker.lower()

logger.info("DataFetcher module initialized")