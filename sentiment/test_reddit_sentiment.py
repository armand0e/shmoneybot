# sentiment/test_reddit_sentiment.py

from reddit_sentiment import RedditSentimentAnalyzer

def test_reddit_sentiment_analyzer():
    # Create an instance of RedditSentimentAnalyzer for a sample stock symbol
    analyzer = RedditSentimentAnalyzer("AAPL")

    # Analyze the Reddit sentiment
    score = analyzer.analyze_reddit_sentiment()

    # Perform basic assertions to verify the sentiment score
    assert isinstance(score, float), "Sentiment score should be a float"
    assert -1.0 <= score <= 1.0, "Sentiment score should be between -1.0 and 1.0"

    # Output test result
    print(f"RedditSentimentAnalyzer test passed with score: {score}")

if __name__ == "__main__":
    test_reddit_sentiment_analyzer()

# Debugging Instructions:
# - Run this script to test the Reddit sentiment analysis functionality.
# - Check the assertions to ensure the sentiment score is within the expected range.
# - Modify the stock symbol to test different subreddits and observe sentiment score changes.