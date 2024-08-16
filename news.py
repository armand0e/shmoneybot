import logging
import praw
import config

class RedditNewsFetcher:
    def __init__(self, ticker):
        self.ticker = ticker.lower()  # Using the ticker symbol, typically in lowercase.
        self.reddit = praw.Reddit(
            client_id=config.API_KEYS['reddit_client_id'],
            client_secret=config.API_KEYS['reddit_client_secret'],
            user_agent=config.API_KEYS['reddit_user_agent']
        )

    def fetch_reddit_news(self):
        possible_subreddits = [self.ticker]

        # General fallback subreddits
        fallback_subreddits = ['stocks', 'investing']

        for subreddit_name in possible_subreddits + fallback_subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.hot(limit=config.SETTINGS['reddit_posts_limit'])
                news = [post.title for post in posts if not post.stickied]
                if news:
                    logging.info(f"Fetched {len(news)} posts from r/{subreddit_name}")
                    return news
            except Exception as e:
                logging.error(f"Error fetching Reddit news from r/{subreddit_name}: {e}")

        logging.warning(f"No relevant news found on Reddit for {self.ticker}")
        return []

class GDELTFetcher:
    def __init__(self, company_name):
        self.company_name = company_name

    def fetch_company_news(self):
        gdelt_url = (
            f"https://api.gdeltproject.org/api/v2/doc/doc"
            f"?query={self.company_name}&mode=artlist&format=json"
        )
        return self._fetch_news(gdelt_url, f"company-specific news for {self.company_name}")

    def fetch_market_news(self):
        gdelt_url = (
            f"https://api.gdeltproject.org/api/v2/doc/doc"
            f"?query={'+OR+'.join(config.SETTINGS['global_market_keywords'])}&mode=artlist&format=json"
        )
        return self._fetch_news(gdelt_url, "global market news")

    def _fetch_news(self, url, context):
        try:
            response = requests.get(url)
            response.raise_for_status()
            articles = response.json().get('articles', [])
            news = [article['title'] for article in articles]
            if news:
                logging.info(f"Fetched {len(news)} articles from GDELT for {context}")
            else:
                logging.warning(f"No articles found in GDELT for {context}")
            return news
        except Exception as e:
            logging.error(f"Error fetching GDELT news for {context}: {e}")
            return []
