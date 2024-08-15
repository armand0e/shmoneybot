# news/test_reddit_news_fetcher.py

from reddit_news_fetcher import RedditNewsFetcher

def test_reddit_news_fetcher():
    # Create an instance of RedditNewsFetcher for a sample stock symbol
    fetcher = RedditNewsFetcher("AAPL")

    # Fetch the news posts
    news_posts = fetcher.fetch_reddit_news()

    # Perform basic assertions to verify the fetched news posts
    assert isinstance(news_posts, list), "News should be returned as a list"
    assert len(news_posts) > 0, "News list should not be empty"
    assert all(isinstance(post, str) for post in news_posts), "All elements in news list should be strings"

    # Output test result
    print(f"RedditNewsFetcher test passed. Fetched {len(news_posts)} posts.")

if __name__ == "__main__":
    test_reddit_news_fetcher()

# Debugging Instructions:
# - Run this script to test the Reddit news fetching functionality.
# - Check the assertions to ensure the news data is correctly formatted.
# - Replace the stock symbol and re-run to test with different inputs.