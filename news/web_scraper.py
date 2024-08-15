import requests
from bs4 import BeautifulSoup
import logging

class WebScraper:
    def __init__(self, url):
        self.url = url

    def fetch_news(self):
        logging.info(f"Fetching news from {self.url}")
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract headlines and brief descriptions (example for CNBC)
            headlines = []
            for article in soup.find_all('div', class_='Card-titleContainer'):
                title = article.find('a').get_text().strip()
                description_tag = article.find_next('div', class_='Card-description')
                description = description_tag.get_text().strip() if description_tag else "No description available"
                headlines.append(f"{title}: {description}")
            
            logging.info(f"Fetched {len(headlines)} articles from {self.url}")
            return headlines

        except requests.exceptions.RequestException as e:
            logging.error(f"Request to {self.url} failed: {e}")
            return []

# Debugging Instructions:
# - Ensure that the target website's structure is stable (HTML elements).
# - Test the scraper with different URLs to ensure it captures the news data correctly.
# - Modify the scraper to target different websites or extract more detailed data as needed.