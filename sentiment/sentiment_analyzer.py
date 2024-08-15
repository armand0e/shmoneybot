# sentiment/sentiment_analyzer.py

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_sentiment(self, news_articles):
        logging.info("Analyzing sentiment of news articles")
        # Calculate sentiment scores for each article
        scores = [self.analyzer.polarity_scores(article)["compound"] for article in news_articles]
        # Return the average sentiment score
        average_score = sum(scores) / len(scores) if scores else 0
        logging.info(f"Average sentiment score: {average_score}")
        return average_score

# Debugging Instructions:
# - Test with a variety of news articles to see how the sentiment score changes.
# - Use extreme positive or negative articles to ensure sentiment analysis reflects correctly.
# - Run the test script to validate the sentiment analysis.