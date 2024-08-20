import asyncpraw
import logging
import sqlite3
import asyncio
import time
import config
from collections import defaultdict
from aiolimiter import AsyncLimiter

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Switch to DEBUG level
logger = logging.getLogger("NewsDataCollectionBot")

# Rate limiter (60 requests per minute)
rate_limiter = AsyncLimiter(60, 60)

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
async def check_rate_limit(reddit):
    async with rate_limiter:
        remaining = int(reddit.auth.limits.get('remaining', 1))
        reset_time = reddit.auth.limits.get('reset_timestamp', time.time() + 60)
        current_time = time.time()

        if remaining < 10:
            sleep_duration = max(reset_time - current_time, 1)
            logger.info(f"Rate limit close to being exhausted. Sleeping for {sleep_duration} seconds.")
            await asyncio.sleep(sleep_duration + 5)  # Add a buffer to the sleep duration
            return True
        return False

# Fetch and process Reddit comments for a specific post
async def fetch_comments(post, conn, progress):
    c = conn.cursor()
    comment_data = []
    comments_fetched = 0
    comments_skipped = 0

    await post.comments.replace_more(limit=None)

    async for comment in post.comments.list():
        if comments_fetched >= 10:  # Limit to top 10 comments
            break
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
async def log_progress(progress_dict):
    while True:
        await asyncio.sleep(30)
        for ticker, progress in progress_dict.items():
            logger.info(f"Progress for {ticker} in the last 30 seconds:\n"
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
async def fetch_historical_data(ticker, progress):
    conn = setup_database()
    logger.info(f"Fetching historical data for {ticker}")

    reddit = asyncpraw.Reddit(
        client_id=config.API_KEYS['reddit_client_id'],
        client_secret=config.API_KEYS['reddit_client_secret'],
        user_agent=config.API_KEYS['reddit_user_agent']
    )

    subreddits = ['investing', 'stocks', 'news', 'finance', 'technology', 'cryptocurrency']
    queries = config.SETTINGS['tickers_and_keywords'][ticker]

    try:
        for subreddit_name in subreddits:
            subreddit = await reddit.subreddit(subreddit_name)
            
            c = conn.cursor()
            c.execute("SELECT last_fetched FROM progress WHERE ticker=?", (ticker,))
            last_fetched = c.fetchone()
            last_fetched = last_fetched[0] if last_fetched else 0

            for query in queries:
                logger.debug(f"Searching in subreddit {subreddit_name} with query '{query}'")
                async for post in subreddit.search(query, sort='new', time_filter='all'):
                    logger.debug(f"Found post: {post.title} (ID: {post.id})")
                    if post.created_utc <= last_fetched:
                        logger.debug(f"Skipping post {post.id}, older than last fetched time.")
                        continue

                    if await check_rate_limit(reddit):
                        continue

                    c.execute("SELECT id FROM news WHERE id=?", (post.id,))
                    if c.fetchone():
                        logger.debug(f"Post {post.id} already in database, skipping.")
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

                        await fetch_comments(post, conn, progress)

                        c.execute("INSERT OR REPLACE INTO progress (ticker, last_fetched) VALUES (?, ?)",
                                  (ticker, post.created_utc))
                        conn.commit()
    except Exception as e:
        logger.error(f"Error fetching historical data for {ticker}: {e}")
    finally:
        conn.close()

# Fetch real-time data from Reddit
async def fetch_realtime_data(ticker, progress):
    conn = setup_database()
    c = conn.cursor()

    try:
        logger.info(f"Fetching real-time data for {ticker}")

        reddit = asyncpraw.Reddit(
            client_id=config.API_KEYS['reddit_client_id'],
            client_secret=config.API_KEYS['reddit_client_secret'],
            user_agent=config.API_KEYS['reddit_user_agent']
        )

        subreddits = ['investing', 'stocks', 'news', 'finance', 'technology', 'cryptocurrency']
        queries = config.SETTINGS['tickers_and_keywords'][ticker]

        for subreddit_name in subreddits:
            subreddit = await reddit.subreddit(subreddit_name)

            async for post in subreddit.stream.submissions():
                if await check_rate_limit(reddit):
                    continue

                if any(query.lower() in post.title.lower() for query in queries):
                    logger.debug(f"Matching post found: {post.title} (ID: {post.id})")
                    c.execute("SELECT id FROM news WHERE id=?", (post.id,))
                    if c.fetchone():
                        logger.debug(f"Post {post.id} already in database, skipping.")
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

                        await fetch_comments(post, conn, progress)
    except Exception as e:
        logger.error(f"Error fetching real-time data for {ticker}: {e}")
    finally:
        conn.close()

# Main function to run the bot
async def main():
    tickers = config.SETTINGS['tickers_and_keywords'].keys()
    progress_dict = defaultdict(lambda: {'posts_fetched': 0, 'posts_skipped': 0, 'comments_fetched': 0, 'comments_skipped': 0})

    tasks = []
    for ticker in tickers:
        tasks.append(fetch_realtime_data(ticker, progress_dict[ticker]))
        await asyncio.sleep(1)  # Staggered start to reduce load

    for ticker in tickers:
        tasks.append(fetch_historical_data(ticker, progress_dict[ticker]))
        await asyncio.sleep(1)

    # Start logging progress
    log_task = asyncio.create_task(log_progress(progress_dict))
    tasks.append(log_task)

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
