from transformers import pipeline
from utils.logger import get_logger

logger = get_logger('SentimentModel')

class SentimentModel:
    def __init__(self, model_name='distilbert-base-uncased-finetuned-sst-2-english'):
        self.model = self._load_model(model_name)

    def _load_model(self, model_name):
        try:
            model = pipeline('sentiment-analysis', model=model_name)
            logger.info(f"Loaded Hugging Face model: {model_name}")
            return model
        except Exception as e:
            logger.error(f"Failed to load Hugging Face model: {str(e)}")
            raise

    def analyze_sentiment(self, social_media_data):
        sentiments = []
        for post in social_media_data:
            sentiment = self.model(post['text'])[0]  # Analyzes the sentiment of the text
            sentiment_score = 1 if sentiment['label'] == 'POSITIVE' else 0
            sentiments.append(sentiment_score)
        
        average_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        reliability = len(sentiments)
        logger.info(f"Sentiment analysis completed with average score {average_sentiment} and reliability {reliability}")
        return average_sentiment, reliability