from transformers import pipeline
from scipy.stats import zscore
import logging

logger = logging.getLogger('SentimentModel')

class AdvancedSentimentAnalyzer:
    def __init__(self, model_name='distilbert-base-uncased-finetuned-sst-2-english', device=-1, max_length=512):
        self.model = pipeline('sentiment-analysis', model=model_name, device=device)
        self.max_length = max_length
        logger.info(f"AdvancedSentimentAnalyzer initialized with model {model_name} on device {device}")

    def analyze_sentiment(self, texts):
        sentiments = []
        for text in texts:
            truncated_text = text[:self.max_length]
            try:
                sentiment = self.model(truncated_text)[0]
                sentiment_score = 1 if sentiment['label'] == 'POSITIVE' else 0
                sentiments.append(sentiment_score)
                logger.debug(f"Text sentiment: {sentiment['label']} with score {sentiment_score}")
            except Exception as e:
                logger.error(f"Error analyzing sentiment for text: {str(e)}")
                continue

        if sentiments:
            average_sentiment = sum(sentiments) / len(sentiments)
            reliability = len(sentiments)
        else:
            average_sentiment = 0
            reliability = 0

        logger.info(f"Sentiment analysis completed with average score {average_sentiment} and reliability {reliability}")
        return average_sentiment, reliability