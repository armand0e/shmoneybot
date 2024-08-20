import praw
import logging
import sqlite3
import random
import time
import threading
import yfinance as yf
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NewsDataCollectionBot")

# Setup and initialize the SQLite database
def setup_database():
    conn = sqlite3.connect('news_data.db')
    c = conn.cursor()
    
    # Create table for news posts
    c.execute('''CREATE TABLE IF NOT EXISTS news
                 (id TEXT PRIMARY KEY,
                  ticker TEXT,
                  timestamp REAL,
                  title TEXT,
                  text TEXT,
                  score INTEGER,
                  comments INTEGER,
                  sentiment_label TEXT,
                  sentiment_value REAL)''')
    
    # Create table for comments
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (comment_id TEXT PRIMARY KEY,
                  post_id TEXT,
                  author TEXT,
                  body TEXT,
                  timestamp REAL,
                  score INTEGER,
                  permalink TEXT,
                  sentiment_label TEXT,
                  sentiment_value REAL,
                  FOREIGN KEY(post_id) REFERENCES news(id))''')
    
    conn.commit()
    return conn

# Get the latest timestamp for a specific ticker from the database
def get_latest_timestamp(ticker, conn):
    c = conn.cursor()
    c.execute('SELECT MAX(timestamp) FROM news WHERE ticker=?', (ticker,))
    result = c.fetchone()
    return result[0] if result[0] is not None else 0

# Expand the queries to include synonyms and related terms
def expand_queries(ticker):
    related_terms = {
        "AAPL": ["Apple", "iPhone", "MacBook", "Cupertino"],
        "MSFT": ["Microsoft", "Windows", "Azure", "Office"],
        "GOOGL": ["Google", "Alphabet", "YouTube", "Android"],
        "AMZN": ["Amazon", "AWS", "Prime", "Bezos"],
        "TSLA": ["Tesla", "Musk", "Model 3", "EV"]
    }
    return related_terms.get(ticker, [ticker])

# Fetch and process Reddit comments for a specific post
def fetch_comments(post, conn):
    c = conn.cursor()
    comment_data = []
    comments_fetched = 0
    comments_skipped = 0
    
    post.comments.replace_more(limit=None)  # Ensure all comments are fetched
    
    for comment in post.comments.list()[:10]:  # Limit to top 10 comments
        # Check if the comment already exists in the database
        c.execute("SELECT comment_id FROM comments WHERE comment_id=?", (comment.id,))
        if c.fetchone():
            comments_skipped += 1
            continue

        comment_data.append({
            'comment_id': comment.id,
            'post_id': post.id,
            'author': comment.author.name if comment.author else None,
            'body': comment.body,
            'timestamp': comment.created_utc,
            'score': comment.score,
            'permalink': comment.permalink
        })
        comments_fetched += 1
    
    if comment_data:
        c.executemany('''INSERT INTO comments (comment_id, post_id, author, body, timestamp, score, permalink)
                         VALUES (:comment_id, :post_id, :author, :body, :timestamp, :score, :permalink)''', comment_data)
        conn.commit()
    
    return comments_fetched, comments_skipped

# Fetch historical data from Reddit
def fetch_historical_data(ticker, conn):
    logger.info(f"Fetching historical data for {ticker}")
    
    reddit = praw.Reddit(
        client_id=config.API_KEYS['reddit_client_id'],
        client_secret=config.API_KEYS['reddit_client_secret'],
        user_agent=config.API_KEYS['reddit_user_agent']
    )
    
    subreddits = ['investing', 'stocks', 'news', 'finance', 'technology', 'cryptocurrency']
    queries = expand_queries(ticker)

    total_posts_fetched = 0
    total_posts_skipped = 0
    total_comments_fetched = 0
    total_comments_skipped = 0

    try:
        for subreddit_name in subreddits:
            subreddit = reddit.subreddit(subreddit_name)
            
            for query in queries:
                for post in subreddit.search(query, sort='new', time_filter='all'):
                    c = conn.cursor()
                    
                    # Skip posts already stored in the database
                    c.execute("SELECT id FROM news WHERE id=?", (post.id,))
                    if c.fetchone():
                        total_posts_skipped += 1
                        continue
                    
                    # Add new posts to the news data
                    if not post.stickied:
                        news_data = [{
                            'id': post.id,
                            'ticker': ticker,
                            'timestamp': post.created_utc,
                            'title': post.title,
                            'text': post.selftext,
                            'score': post.score,
                            'comments': post.num_comments
                        }]
                        
                        c.executemany('''INSERT INTO news (id, ticker, timestamp, title, text, score, comments)
                                         VALUES (:id, :ticker, :timestamp, :title, :text, :score, :comments)''', news_data)
                        conn.commit()
                        total_posts_fetched += 1
                        
                        # Fetch and store comments for the post
                        comments_fetched, comments_skipped = fetch_comments(post, conn)
                        total_comments_fetched += comments_fetched
                        total_comments_skipped += comments_skipped
    except Exception as e:
        logger.error(f"Error fetching historical data for {ticker}: {e}")

    logger.info(f"Historical Data Collection for {ticker}:\n"
                f" - Total Posts Fetched: {total_posts_fetched}\n"
                f" - Total Posts Skipped: {total_posts_skipped}\n"
                f" - Total Comments Fetched: {total_comments_fetched}\n"
                f" - Total Comments Skipped: {total_comments_skipped}")

# Fetch real-time data from Reddit
def fetch_realtime_data(ticker):
    conn = sqlite3.connect('news_data.db')
    c = conn.cursor()  # Create cursor outside the loop
    total_posts_fetched = 0
    total_posts_skipped = 0
    total_comments_fetched = 0
    total_comments_skipped = 0

    try:
        logger.info(f"Fetching real-time data for {ticker}")
        
        reddit = praw.Reddit(
            client_id=config.API_KEYS['reddit_client_id'],
            client_secret=config.API_KEYS['reddit_client_secret'],
            user_agent=config.API_KEYS['reddit_user_agent']
        )
        
        subreddits = ['investing', 'stocks', 'news', 'finance', 'technology', 'cryptocurrency']
        queries = expand_queries(ticker)

        for subreddit_name in subreddits:
            subreddit = reddit.subreddit(subreddit_name)
            
            for post in subreddit.stream.submissions():
                # Check if the post title contains any of the query terms
                if any(query.lower() in post.title.lower() for query in queries):
                    # Skip posts already stored in the database
                    c.execute("SELECT id FROM news WHERE id=?", (post.id,))
                    if c.fetchone():
                        total_posts_skipped += 1
                        continue
                    
                    # Add new posts to the news data
                    if not post.stickied:
                        news_data = [{
                            'id': post.id,
                            'ticker': ticker,
                            'timestamp': post.created_utc,
                            'title': post.title,
                            'text': post.selftext,
                            'score': post.score,
                            'comments': post.num_comments
                        }]
                        
                        c.executemany('''INSERT INTO news (id, ticker, timestamp, title, text, score, comments)
                                         VALUES (:id, :ticker, :timestamp, :title, :text, :score, :comments)''', news_data)
                        conn.commit()
                        total_posts_fetched += 1
                        
                        # Fetch and store comments for the post
                        comments_fetched, comments_skipped = fetch_comments(post, conn)
                        total_comments_fetched += comments_fetched
                        total_comments_skipped += comments_skipped
    except Exception as e:
        logger.error(f"Error fetching real-time data for {ticker}: {e}")
    finally:
        logger.info(f"Real-Time Data Collection for {ticker}:\n"
                    f" - Total Posts Fetched: {total_posts_fetched}\n"
                    f" - Total Posts Skipped: {total_posts_skipped}\n"
                    f" - Total Comments Fetched: {total_comments_fetched}\n"
                    f" - Total Comments Skipped: {total_comments_skipped}")
        conn.close()
              
# Main function to run the bot
def main():
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    # Start threads for real-time data collection
    threads = []
    for ticker in tickers:
        thread = threading.Thread(target=fetch_realtime_data, args=(ticker,))
        threads.append(thread)
        thread.start()

    # Fetch historical data first
    conn = setup_database()
    for ticker in tickers:
        fetch_historical_data(ticker, conn)
        time.sleep(2)  # Small sleep to avoid hitting rate limits
    conn.close()
    
    # Join threads to ensure all complete
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
