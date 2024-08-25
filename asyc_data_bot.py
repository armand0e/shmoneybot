import praw
import logging
import sqlite3
import random
import time
import threading
import config
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NewsDataCollectionBot")

# Setup and initialize the SQLite database
def setup_database():
    conn = sqlite3.connect('news_data.db')
    c = conn.cursor()
    
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
    
    try:
        c.execute("ALTER TABLE news ADD COLUMN last_fetched REAL")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            raise

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

    c.execute('''CREATE TABLE IF NOT EXISTS progress
                 (ticker TEXT PRIMARY KEY,
                  last_fetched REAL)''')

    conn.commit()
    return conn

# Check the rate limit and sleep if necessary
def check_rate_limit(reddit, backoff=2):
    remaining = int(reddit.auth.limits.get('remaining', 1))
    reset_time = reddit.auth.limits.get('reset_timestamp', time.time() + 60)
    current_time = time.time()
    
    if remaining < 10:
        sleep_duration = max(reset_time - current_time, 1)
        logger.info(f"Rate limit close to being exhausted. Sleeping for {sleep_duration} seconds.")
        time.sleep(sleep_duration + 5 + (backoff ** 2))
        return True
    return False

# Fetch and process Reddit comments for a specific post
def fetch_comments(post, conn, progress):
    c = conn.cursor()
    comment_data = []
    comments_fetched = 0
    comments_skipped = 0
    
    post.comments.replace_more(limit=None)
    
    for comment in post.comments.list()[:10]:
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
    
    progress['comments_fetched'] += comments_fetched
    progress['comments_skipped'] += comments_skipped

# Periodic logging of progress
def log_progress(progress_dict):
    while True:
        time.sleep(30)
        for ticker, progress in progress_dict.items():
            logger.debug(f"Progress for {ticker} in the last 30 seconds:\n"
                         f" - Posts Fetched: {progress['posts_fetched']}\n"
                         f" - Posts Skipped: {progress['posts_skipped']}\n"
                         f" - Comments Fetched: {progress['comments_fetched']}\n"
                         f" - Comments Skipped: {progress['comments_skipped']}")
            # Reset progress counters
            progress['posts_fetched'] = 0
            progress['posts_skipped'] = 0
            progress['comments_fetched'] = 0
            progress['comments_skipped'] = 0

# Fetch historical data from Reddit
def fetch_historical_data(ticker, subreddit_name, progress):
    conn = setup_database()
    logger.info(f"Fetching historical data for {ticker} from {subreddit_name}")
    
    reddit = praw.Reddit(
        client_id=config.API_KEYS['reddit_client_id'],
        client_secret=config.API_KEYS['reddit_client_secret'],
        user_agent=config.API_KEYS['reddit_user_agent']
    )
    
    queries = config.SETTINGS['tickers_and_keywords'][ticker]

    backoff = 2

    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        c = conn.cursor()
        c.execute("SELECT last_fetched FROM progress WHERE ticker=?", (ticker,))
        last_fetched = c.fetchone()
        last_fetched = last_fetched[0] if last_fetched else 0

        for query in queries:
            for post in subreddit.search(query, sort='new', time_filter='all'):
                #if post.created_utc <= last_fetched:
                #    continue

                if check_rate_limit(reddit, backoff):
                    backoff += 1
                else:
                    backoff = 2
                
                c.execute("SELECT id FROM news WHERE id=?", (post.id,))
                if c.fetchone():
                    progress['posts_skipped'] += 1
                    continue
                
                if not post.stickied:
                    news_data = [{
                        'id': post.id,
                        'ticker': ticker,
                        'timestamp': post.created_utc,
                        'title': post.title,
                        'text': post.selftext,
                        'score': post.score,
                        'comments': post.num_comments,
                        'last_fetched': post.created_utc
                    }]
                    
                    c.executemany('''INSERT INTO news (id, ticker, timestamp, title, text, score, comments, last_fetched)
                                     VALUES (:id, :ticker, :timestamp, :title, :text, :score, :comments, :last_fetched)''', news_data)
                    conn.commit()
                    progress['posts_fetched'] += 1
                    logger.info(f'Fetched 1 post for {ticker}')
                    fetch_comments(post, conn, progress)
                    
                    c.execute("INSERT OR REPLACE INTO progress (ticker, last_fetched) VALUES (?, ?)",
                              (ticker, post.created_utc))
                    conn.commit()
    except Exception as e:
        logger.error(f"Error fetching historical data for {ticker}: {e}")
    finally:
        conn.close()

# Fetch real-time data from Reddit
def fetch_realtime_data(ticker, subreddit_name, progress):
    conn = setup_database()
    c = conn.cursor()
    backoff = 1

    try:
        logger.info(f"Fetching real-time data for {ticker} from {subreddit_name}")
        
        reddit = praw.Reddit(
            client_id=config.API_KEYS['reddit_client_id'],
            client_secret=config.API_KEYS['reddit_client_secret'],
            user_agent=config.API_KEYS['reddit_user_agent']
        )
        
        queries = config.SETTINGS['tickers_and_keywords'][ticker]

        subreddit = reddit.subreddit(subreddit_name)
        
        for post in subreddit.stream.submissions():
            if check_rate_limit(reddit, backoff):
                backoff += 1
            else:
                backoff = 1
            
            if any(query.lower() in post.title.lower() for query in queries):
                c.execute("SELECT id FROM news WHERE id=?", (post.id,))
                if c.fetchone():
                    progress['posts_skipped'] += 1
                    continue
                
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
                    progress['posts_fetched'] += 1
                    logger.info(f'Fetched 1 post for {ticker}')
                    
                    fetch_comments(post, conn, progress)
    except Exception as e:
        logger.error(f"Error fetching real-time data for {ticker}: {e}")
    finally:
        conn.close()

# Main function to run the bot
def main():
    tickers = list(config.SETTINGS['tickers_and_keywords'].keys())
    subreddits = ['investing', 'stocks', 'news', 'finance', 'technology', 'cryptocurrency']
    progress_dict = defaultdict(lambda: {'posts_fetched': 0, 'posts_skipped': 0, 'comments_fetched': 0, 'comments_skipped': 0})
    
    # Start logging thread
    logging_thread = threading.Thread(target=log_progress, args=(progress_dict,))
    logging_thread.daemon = True  # Daemon thread will exit when the main program exits
    logging_thread.start()

    while True:
        ticker = random.choice(tickers)
        subreddit_name = random.choice(subreddits)

        # Fetch real-time data
        # fetch_realtime_data(ticker, subreddit_name, progress_dict[ticker])

        # Fetch historical data
        fetch_historical_data(ticker, subreddit_name, progress_dict[ticker])

        # Adjust the sleep duration to control the frequency of selecting a new ticker and subreddit
        #time.sleep(1)
if __name__ == "__main__":
    main()
