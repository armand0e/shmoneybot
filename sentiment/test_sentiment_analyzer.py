# sentiment/test_sentiment_analyzer.py

from advanced_sentiment_analyzer import AdvancedSentimentAnalyzer

def test_advanced_sentiment_analyzer():
    # Create an instance of AdvancedSentimentAnalyzer
    analyzer = AdvancedSentimentAnalyzer()

    # Test with sample news articles
    test_articles = [
        "The company reported record profits for the quarter.",
        "The stock price plummeted after the scandal broke.",
        "Investors are optimistic about the upcoming product launch."
    ]

    # Analyze the sentiment of the articles
    score = analyzer.analyze_sentiment(test_articles)

    # Perform basic assertions to verify the sentiment score
    assert isinstance(score, float), "Sentiment score should be a float"
    assert -1.0 <= score <= 1.0, "Sentiment score should be between -1.0 and 1.0"

    # Output test result
    print(f"AdvancedSentimentAnalyzer test passed with score: {score}")

if __name__ == "__main__":
    test_advanced_sentiment_analyzer()

# Debugging Instructions:
# - Run this script to test the advanced sentiment analysis functionality.
# - Check the assertions to ensure the sentiment score is within the expected range.
# - Modify the test articles to see how the sentiment score changes.