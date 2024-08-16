import logging
import numpy as np
from transformers import pipeline
import config

class AdvancedSentimentAnalyzer:
    def __init__(self):
        logging.info("Initializing advanced sentiment analysis model")
        device = 0 if config.SETTINGS['use_gpu'] else -1
        self.sentiment_model = pipeline(
            "sentiment-analysis", 
            model=config.SETTINGS['sentiment_model_name'], 
            device=device, 
            clean_up_tokenization_spaces=True
        )

    def analyze_sentiment(self, texts):
        logging.info("Analyzing sentiment using advanced NLP model")
        max_length = config.SETTINGS['sentiment_max_length']
        truncated_texts = [text[:max_length] for text in texts]

        results = self.sentiment_model(truncated_texts)
        scores = []
        for result in results:
            score = result['score'] if result['label'] == 'POSITIVE' else -result['score']
            scores.append(score)

        weighted_average_score = sum(scores) / len(scores) if scores else 0
        weighted_avg_stds = np.sum(np.std(scores)) / np.size(scores) if scores else 0
        logging.info(f"Average sentiment score: {weighted_average_score}")
        logging.info(f"Average sentiment std: {weighted_avg_stds}")

        reliability = max(0, 100 - (weighted_avg_stds * 100))
        return weighted_average_score, reliability
