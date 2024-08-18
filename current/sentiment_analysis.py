from transformers import pipeline
from scipy.stats import zscore
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SentimentAnalysis:
    def __init__(self):
        logger.info("Loading sentiment analysis model")
        self.sentiment_model = pipeline("sentiment-analysis")

    def analyze_sentiment(self, texts):
        logger.info(f"Analyzing sentiment for texts: {texts}")
        results = self.sentiment_model(texts)
        logger.info(f"Sentiment analysis results: {results}")
        return results

    def normalize_scores(self, results):
        logger.info("Normalizing sentiment scores")
        scores = [result['score'] * 100 if result['label'] == 'POSITIVE' else -result['score'] * 100 for result in results]
        normalized_scores = zscore(scores) * 100
        logger.info(f"Normalized scores: {normalized_scores}")
        return normalized_scores

if __name__=='__main__':
    texts = ["This stock is amazing!", "Terrible results, wouldn't buy."]
    analyzer = SentimentAnalysis()
    sentiments = analyzer.analyze_sentiment(texts)
    normalized_scores = analyzer.normalize_scores(sentiments)
    print(normalized_scores)