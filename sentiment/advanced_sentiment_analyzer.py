from transformers import pipeline
import logging

class AdvancedSentimentAnalyzer:
    def __init__(self):
        # Initialize a sentiment-analysis pipeline using transformers
        logging.info("Initializing advanced sentiment analysis model")
        self.sentiment_model = pipeline("sentiment-analysis", device=0)

    def analyze_sentiment(self, texts):
        logging.info("Analyzing sentiment using advanced NLP model")
        max_length = 512  # Maximum sequence length for the model
        truncated_texts = [text[:max_length] for text in texts]  # Truncate texts if too long

        results = self.sentiment_model(truncated_texts)
        
        # Convert the results into a simple score (positive or negative)
        scores = []
        for result in results:
            score = result['score'] if result['label'] == 'POSITIVE' else -result['score']
            scores.append(score)

        # Return the weighted average sentiment score
        weighted_average_score = sum(scores) / len(scores) if scores else 0
        logging.info(f"Average sentiment score: {weighted_average_score}")
        return weighted_average_score
