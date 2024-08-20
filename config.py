# Configuration file for API keys and global settings

API_KEYS = {
    'reddit_client_id': 'Up2_w6L851Kg_PsN_KJpWA',  # Replace with your Reddit client ID
    'reddit_client_secret': 'bmM2To0THTLo_zL8FuHXUUfDjAcdqg',  # Replace with your Reddit client secret
    'reddit_user_agent': 'My_Reddit_Bot -armand0e',  # Replace with your Reddit user agent
}

SETTINGS = {
    'historical_data_length': '1y',  # Default length for historical data (1 year)
    'reddit_posts_limit': 300,        # Max number of Reddit posts to fetch
    'global_market_keywords': ['inflation', 'CPI', 'Federal Reserve', 'interest rates', 'unemployment', 'GDP',
                                'economic growth', 'geopolitical risk', 'war', 'Israel', 'Middle East', 'global markets',
                                'oil prices', 'natural disasters', 'trade wars', 'tariffs'],  
                                     # Keywords to monitor in global market sentiment
    'sentiment_threshold': 0.2,      # Threshold for positive sentiment classification
    'reliability_threshold': 70,     # Reliability threshold for making decisions
    'buy_threshold': 0.2,            # Sentiment threshold to consider buying
    'sell_threshold': -0.2,          # Sentiment threshold to consider selling
    'logging_level': 'INFO',         # Logging level (e.g., DEBUG, INFO, WARNING, ERROR)
    'sentiment_model_name': 'distilbert-base-uncased-finetuned-sst-2-english', # Name of the model used for sentiment analysis
    'sentiment_max_length': 512,     # Max length for sentiment analysis inputs
    'use_gpu': False,                # Whether to use GPU for sentiment analysis (set to True if GPU is available)
}

