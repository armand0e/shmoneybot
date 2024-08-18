import requests
from bs4 import BeautifulSoup
import logging
import praw

class CompanyData:
    def __init__(self, company_name):
        self.company_name = company_name
        self.wikipedia_data = []
        self.reddit_subreddit = None
        self.twitter_handle = None
        self.reddit_news = []
        
        self.init_scraping()

    def google_search(self, query):
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a', href=True):
            url = link['href']
            if "url?q=" in url:
                # Extract the actual URL from the Google redirect URL
                start = url.find("/url?q=") + 7
                end = url.find("&", start)
                return url[start:end]

        return None

    def scrape_wikipedia(self):
        logging.info(f"Searching Wikipedia page for {self.company_name}")
        wiki_url = self.google_search(f"{self.company_name} Wikipedia")
        if not wiki_url:
            logging.error(f"Could not find a Wikipedia page for {self.company_name} through Google search")
            return
        
        response = requests.get(wiki_url)
        if response.status_code != 200:
            logging.error(f"Failed to access Wikipedia page for {self.company_name}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('div', class_='mw-parser-output')
        paragraphs = content.find_all('p')
        self.wikipedia_data = [p.get_text() for p in paragraphs if p.get_text().strip()]
        
        logging.info(f"Scraped Wikipedia data for {self.company_name}")

    def scrape_reddit(self):
        logging.info(f"Searching Reddit page for {self.company_name}")
        reddit_url = self.google_search(f"{self.company_name} Reddit")
        if not reddit_url:
            logging.error(f"Could not find a Reddit page for {self.company_name} through Google search")
            return
        
        # Extract subreddit name from URL
        if "/r/" in reddit_url:
            self.reddit_subreddit = reddit_url.split("/r/")[-1].split("/")[0]
            logging.info(f"Found subreddit for {self.company_name}: {self.reddit_subreddit}")
        else:
            logging.error(f"Could not extract subreddit from URL: {reddit_url}")

    def fetch_reddit_news(self):
        if not self.reddit_subreddit:
            logging.error(f"No subreddit found for {self.company_name}, cannot fetch news")
            return
        
        reddit = praw.Reddit(
            client_id='Up2_w6L851Kg_PsN_KJpWA',
            client_secret='bmM2To0THTLo_zL8FuHXUUfDjAcdqg',
            user_agent='moneybot -armand0e'
        )
        
        try:
            subreddit = reddit.subreddit(self.reddit_subreddit)
            posts = subreddit.hot(limit=50)
            self.reddit_news = []
            for post in posts:
                if not post.stickied:
                    post_obj = {
                        "title": post.title,
                        "message": post.selftext,
                        "date": post.created_utc,
                        "author": post.author.name if post.author else "Unknown",
                        "comments": post.num_comments
                    }
                    self.reddit_news.append(post_obj)
            logging.info(f"Fetched {len(self.reddit_news)} posts from r/{self.reddit_subreddit}")
        except Exception as e:
            logging.error(f"Error fetching Reddit news for {self.company_name}: {e}")

    def scrape_twitter(self):
        logging.info(f"Searching Twitter page for {self.company_name}")
        twitter_url = self.google_search(f"{self.company_name} Twitter")
        if not twitter_url:
            logging.error(f"Could not find a Twitter page for {self.company_name} through Google search")
            return
        
        # Extract Twitter handle from URL
        if "twitter.com" in twitter_url:
            self.twitter_handle = twitter_url.split("twitter.com/")[-1].split("/")[0]
            logging.info(f"Found Twitter handle for {self.company_name}: {self.twitter_handle}")
        else:
            logging.error(f"Could not extract Twitter handle from URL: {twitter_url}")

    def init_scraping(self):
        # Scrape data from various platforms
        self.scrape_wikipedia()
        self.scrape_reddit()
        self.scrape_twitter()
