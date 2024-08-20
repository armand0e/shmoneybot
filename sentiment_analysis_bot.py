import os
import sqlite3
import numpy as np
from transformers import pipeline
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress TensorFlow informational messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentimentAnalysisBot")

# Setup the sentiment analysis pipeline
sentiment_analyzer = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

# Function to fetch posts and comments from the database
def fetch_posts_and_comments(ticker, conn):
    c = conn.cursor()

    # Fetch posts and their associated comments
    c.execute('''SELECT n.id, n.ticker, n.title, n.text, n.timestamp, n.score, c.body, c.score
                 FROM news n
                 LEFT JOIN comments c ON n.id = c.post_id
                 WHERE n.ticker = ?
                 ORDER BY n.timestamp DESC''', (ticker,))
    
    rows = c.fetchall()
    
    posts = {}
    for row in rows:
        post_id = row[0]
        if post_id not in posts:
            posts[post_id] = {
                "ticker": row[1],  # Include the ticker in the dictionary
                "title": row[2],
                "text": row[3],
                "timestamp": row[4],
                "score": row[5],
                "comments": []
            }
        if row[6] is not None:  # If there is a comment
            posts[post_id]["comments"].append({"body": row[6], "score": row[7]})
    
    return posts

# Function to analyze sentiment for a single text
def analyze_sentiment(text):
    result = sentiment_analyzer(text[:512])[0]
    score = 1 if result['label'] == 'POSITIVE' else -1
    return score

# Function to calculate sentiment for a single post
def calculate_post_sentiment(post):
    post_score = analyze_sentiment(post["text"])

    # Use ThreadPoolExecutor to analyze comment sentiments in parallel
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(analyze_sentiment, comment["body"]): comment for comment in post["comments"]}
        
        weighted_comment_scores = []
        for future in as_completed(futures):
            comment = futures[future]
            comment_sentiment = future.result()
            weighted_score = comment_sentiment * comment["score"]
            weighted_comment_scores.append(weighted_score)
    
    total_comment_score = np.sum([comment["score"] for comment in post["comments"]])
    
    if total_comment_score > 0:
        weighted_average = np.sum(weighted_comment_scores) / total_comment_score
        overall_sentiment = (post_score + weighted_average) / 2
    else:
        overall_sentiment = post_score

    return overall_sentiment

# Function to aggregate sentiment for a ticker using parallel processing and normalize it
def aggregate_ticker_sentiment(posts):
    total_posts = len(posts)
    valid_posts = 0
    disregarded_posts = 0

    sentiments = []
    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(calculate_post_sentiment, post) for post in posts.values()]
        
        for future in as_completed(futures):
            sentiment = future.result()
            if sentiment != 0.0:  # Assuming that 0.0 sentiment is disregarded
                sentiments.append(sentiment)
                valid_posts += 1
            else:
                disregarded_posts += 1

    if sentiments:
        min_sentiment = np.min(sentiments)
        max_sentiment = np.max(sentiments)
        range_sentiment = max_sentiment - min_sentiment
        overall_ticker_sentiment = (np.mean(sentiments) - min_sentiment) / range_sentiment * 2 - 1
    else:
        overall_ticker_sentiment = 0.0

    ticker = list(posts.values())[0]['ticker']
    overall_ticker_reliability = np.std(sentiments) if sentiments else 0.0  # Reliability based on the std of sentiments

    logger.info(f"Ticker Analysis for {ticker}:\n"
                f" - Normalized Overall Sentiment: {overall_ticker_sentiment}\n"
                f" - Overall Reliability (std): {overall_ticker_reliability}\n"
                f" - Total Posts Gathered: {total_posts}\n"
                f" - Posts Disregarded: {disregarded_posts}\n"
                f" - Valid Posts Analyzed: {valid_posts}")

    return overall_ticker_sentiment, overall_ticker_reliability

# Function to analyze and generate sentiment for a stock ticker
def analyze_and_generate_sentiment(ticker, conn):
    posts = fetch_posts_and_comments(ticker, conn)
    ticker_sentiment, ticker_reliability = aggregate_ticker_sentiment(posts)
    return ticker_sentiment, ticker_reliability

if __name__ == "__main__":
    conn = sqlite3.connect('news_data.db')
    # Dynamically generate tickers list from the database
    c = conn.cursor()
    c.execute('SELECT DISTINCT ticker FROM news')
    tickers = [row[0] for row in c.fetchall()]
    logger.info(f"Tickers found in database: {tickers}")
    for ticker in tickers:
        sentiment, reliability = analyze_and_generate_sentiment(ticker, conn)
    conn.close()
