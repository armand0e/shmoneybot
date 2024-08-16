import logging
import praw
import requests
import config

class RedditNewsFetcher:
    def __init__(self, company_name):
        self.company_name = company_name
        self.reddit = praw.Reddit(
            client_id=config.API_KEYS['reddit_client_id'],
            client_secret=config.API_KEYS['reddit_client_secret'],
            user_agent=config.API_KEYS['reddit_user_agent']
        )

    def fetch_reddit_news(self):
        try:
            subreddit = self.reddit.subreddit(self.company_name)
            posts = subreddit.hot(limit=config.SETTINGS['reddit_posts_limit'])
            news = [post.title for post in posts if not post.stickied]
            logging.info(f"Fetched {len(news)} posts from r/{self.company_name}")
            return news
        except Exception as e:
            logging.error(f"Error fetching Reddit news for {self.company_name}: {e}")
            return []

class GDELTFetcher:
    def fetch_gdelt_news(self):
        gdelt_url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={'+OR+'.join(config.SETTINGS['global_market_keywords'])}&mode=artlist&format=json"
        try:
            response = requests.get(gdelt_url)
            response.raise_for_status()
            articles = response.json().get('articles', [])
            news = [article['title'] for article in articles]
            logging.info(f"Fetched {len(news)} articles from GDELT")
            return news
        except Exception as e:
            logging.error(f"Error fetching GDELT news: {e}")
            return []