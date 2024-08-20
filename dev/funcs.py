import yfinance as yf
import re
import requests
from bs4 import BeautifulSoup

def extract_keywords(text):
    # Simple function to split text into keywords
    keywords = re.findall(r'\b\w+\b', text)
    return list(set(keywords))  # Remove duplicates

def search_wikipedia(company_name):
    search_url = f"https://en.wikipedia.org/w/index.php?search={company_name}&title=Special:Search&fulltext=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the first relevant search result (usually within the first 'mw-search-result-heading' class)
    first_result = soup.find('div', class_='mw-search-result-heading')
    if first_result:
        link = first_result.find('a')['href']
        return f"https://en.wikipedia.org{link}"
    return None

def scrape_wikipedia_for_keywords(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract the summary paragraph from the page
    paragraphs = soup.find_all('p')
    summary = " ".join([para.text for para in paragraphs[:2]])  # Extract the first two paragraphs
    return extract_keywords(summary)

def generate_keywords(ticker):
    # Fetch company info from yfinance
    stock = yf.Ticker(ticker)
    company_info = stock.info
    
    # Get the company name
    company_name = company_info.get('longName', '')
    
    # Get the company summary
    summary = company_info.get('longBusinessSummary', '')
    
    # Extract keywords from the company summary
    summary_keywords = extract_keywords(summary)
    
    # Search Wikipedia and extract keywords
    wikipedia_url = search_wikipedia(company_name)
    wikipedia_keywords = []
    if wikipedia_url:
        wikipedia_keywords = scrape_wikipedia_for_keywords(wikipedia_url)
    
    # Combine all keywords
    keywords = set(summary_keywords + wikipedia_keywords)  # Use a set to avoid duplicates
    if company_name:
        keywords.add(company_name)
    
    # Convert back to a list and return
    return list(keywords)

if __name__ == '__main__':
    ticker = 'MSFT'
    keywords = generate_keywords(ticker)
    print(keywords)
