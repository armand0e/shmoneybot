# sentiment/reddit_sentiment.py

import praw
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import API_KEYS, SETTINGS

class RedditSentimentAnalyzer:
    def __init__(self, stock_symbol):
        self.stock_symbol = stock_symbol
        self.analyzer = SentimentIntensityAnalyzer()
        self.reddit = praw.Reddit(
            client_id=API_KEYS['reddit_client_id'],
            client_secret=API_KEYS['reddit_client_secret'],
            user_agent=API_KEYS['reddit_user_agent']
        )
        self.subreddits = self.map_stock_to_subreddit(stock_symbol)

    def map_stock_to_subreddit(self, stock_symbol):
        # This function maps stock symbols to relevant subreddits.
        # You can expand this dictionary as needed.
        mapping = {
            'AAPL': 'apple',
            'TSLA': 'teslamotors',
            'GME': 'wallstreetbets'
        }
        return mapping.get(stock_symbol, None)

    def fetch_reddit_posts(self):
        logging.info(f"Fetching Reddit posts for {self.stock_symbol}")
        if not self.subreddits:
            logging.warning(f"No subreddit found for {self.stock_symbol}")
            return []

        posts = []
        subreddit = self.reddit.subreddit(self.subreddits)
        for post in subreddit.hot(limit=SETTINGS['reddit_posts_limit']):
            posts.append(post.title + " " + post.selftext)

        logging.info(f"Fetched {len(posts)} posts from r/{self.subreddits}")
        return posts

    def analyze_reddit_sentiment(self):
        posts = self.fetch_reddit_posts()
        if not posts:
            return 0  # Neutral sentiment if no posts are found

        scores = [self.analyzer.polarity_scores(post)["compound"] for post in posts]
        average_score = sum(scores) / len(scores)
        logging.info(f"Average Reddit sentiment score: {average_score}")
        return average_score

# Debugging Instructions:
# - Ensure you have valid Reddit API credentials in the config file.
# - Test with different stock symbols and check the mapped subreddits.
# - Use the test script to validate the Reddit sentiment analysis.