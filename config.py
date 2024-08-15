# config.py

# Configuration file for API keys and global settings

API_KEYS = {
    'reddit_client_id': 'Up2_w6L851Kg_PsN_KJpWA',  # Replace with your Reddit client ID
    'reddit_client_secret': 'bmM2To0THTLo_zL8FuHXUUfDjAcdqg',  # Replace with your Reddit client secret
    'reddit_user_agent': 'My_Reddit_Bot -armand0e'  # Replace with your Reddit user agent
}

SETTINGS = {
    'historical_data_length': '1y',  # Default length for historical data
    'reddit_posts_limit': 50,  # Max number of Reddit posts to fetch
    'global_market_keywords': ['inflation', 'CPI', 'Federal Reserve', 'interest rates'],  # Keywords to monitor in global market sentiment
    'sentiment_threshold': 0.5,  # Threshold for positive/negative sentiment classification
}

# Debugging Instructions:
# - Ensure all API keys are correctly filled out.
# - Adjust the SETTINGS values to suit your analysis needs.
# - Validate the API keys by testing connections to GNews and Reddit in their respective test scripts.