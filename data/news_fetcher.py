
import praw
import requests
import logging

logger = logging.getLogger('NewsFetcher')

class RedditNewsFetcher:
    def __init__(self, reddit_api_keys, posts_limit=20):
        self.reddit = praw.Reddit(
            client_id=reddit_api_keys['client_id'],
            client_secret=reddit_api_keys['client_secret'],
            user_agent=reddit_api_keys['user_agent']
        )
        self.posts_limit = posts_limit
        logger.info("RedditNewsFetcher initialized")

    def fetch_reddit_posts(self, company_name):
        try:
            subreddit = self.reddit.subreddit(company_name.lower())
            posts = [post.title for post in subreddit.hot(limit=self.posts_limit)]
            logger.info(f"Fetched {len(posts)} Reddit posts for {company_name}")
            return posts
        except Exception as e:
            logger.error(f"Failed to fetch Reddit posts for {company_name}: {str(e)}")
            return []

class GDELTFetcher:
    def __init__(self, gnews_api_key):
        self.gnews_api_key = gnews_api_key
        logger.info("GDELTFetcher initialized")

    def fetch_news(self, keywords):
        try:
            # Example API call, adjust as needed
            url = f'https://api.gdeltproject.org/api/v2/doc/docsearch?query={"+".join(keywords)}&mode=artlist&format=json&key={self.gnews_api_key}'
            response = requests.get(url)
            response.raise_for_status()
            news_data = response.json()
            logger.info(f"Fetched news data for keywords: {keywords}")
            return news_data
        except Exception as e:
            logger.error(f"Failed to fetch news data for keywords {keywords}: {str(e)}")
            return {}
