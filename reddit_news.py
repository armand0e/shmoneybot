import yfinance as yf
import praw
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import json

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Set up basic logging
logging.basicConfig(level=config["general"].get("log_level", "INFO"))

class WikiData:
    def __init__(self, company_name):
        self.company_name = company_name
        self.social_media_links = {}
        self.update_wiki()

    def update_wiki(self):
        search_url = f"https://en.wikipedia.org/wiki/Special:Search?search={self.company_name}"
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check if the search returned any results
        first_link_div = soup.find('div', class_='mw-search-result-heading')
        if not first_link_div:
            logging.error(f"No Wikipedia page found for {self.company_name}")
            return
        
        first_link = first_link_div.find('a')
        if not first_link:
            logging.error(f"Could not find a Wikipedia page link for {self.company_name}")
            return
        
        wikipedia_url = f"https://en.wikipedia.org{first_link['href']}"
        
        response = requests.get(wikipedia_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        self.social_media_links = {}
        infobox = soup.find('table', class_='infobox vcard')
        if infobox:
            links = infobox.find_all('a', href=True)
            for link in links:
                url = link['href']
                if 'reddit.com' in url:
                    self.social_media_links['Reddit'] = url
                elif 'twitter.com' in url:
                    self.social_media_links['Twitter'] = url
                elif 'facebook.com' in url:
                    self.social_media_links['Facebook'] = url
                elif 'linkedin.com' in url:
                    self.social_media_links['LinkedIn'] = url
        
        logging.info(f"Fetched Wikipedia data for {self.company_name}")

class Finance:
    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol or config["yfinance"].get("default_ticker", "AAPL")
        self.company_name = None
        self.stock_info = None
        self.update_finance()

    def update_finance(self):
        stock = yf.Ticker(self.ticker_symbol)
        self.company_name = stock.info.get('shortName', None)
        self.stock_info = stock.info if self.company_name else {}
        logging.info(f"Updated financial data for {self.company_name}")


class RedditData:
    def __init__(self, company_name, reddit_url=None):
        self.company_name = company_name
        self.reddit_url = reddit_url
        self.reddit = praw.Reddit(
            client_id=config["reddit"]["client_id"],
            client_secret=config["reddit"]["client_secret"],
            user_agent=config["reddit"]["user_agent"]
        )
        self.news = []
        self.update_reddit()

    def update_reddit(self):
        try:
            if self.reddit_url:
                subreddit_name = self.reddit_url.split('/r/')[-1]
            else:
                subreddit_name = self.company_name

            subreddit = self.reddit.subreddit(subreddit_name)
            posts = subreddit.hot(limit=config["reddit"]["reddit_posts_limit"])
            self.news = []
            for post in posts:
                if not post.stickied:
                    post_obj = {
                        "title": post.title,
                        "message": post.selftext,
                        "date": datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        "author": post.author.name if post.author else "Unknown",
                        "comments": post.num_comments
                    }
                    self.news.append(post_obj)
            logging.info(f"Fetched {len(self.news)} posts from r/{subreddit_name}")
        except Exception as e:
            logging.error(f"Error fetching Reddit news for {self.company_name}: {e}")
            self.news = []


class TwitterData:
    def __init__(self, company_name, twitter_url=None):
        self.company_name = company_name
        self.twitter_url = twitter_url
        self.tweets = []
        self.update_twitter()

    def update_twitter(self):
        # Placeholder for future implementation
        logging.info(f"Twitter data fetching for {self.company_name} is not implemented yet.")
        self.tweets = []


class Stock:
    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol
        self.finance = Finance(ticker_symbol)
        self.wiki = WikiData(self.finance.company_name)
        self.reddit = RedditData(self.finance.company_name, reddit_url=self.wiki.social_media_links.get('Reddit'))
        self.twitter = TwitterData(self.finance.company_name, twitter_url=self.wiki.social_media_links.get('Twitter'))

    def update_all(self):
        logging.info(f"Updating all data for {self.ticker_symbol}")
        self.finance.update_finance()
        self.wiki.update_wiki()
        self.reddit.update_reddit()
        self.twitter.update_twitter()

