# Configuration file for API keys and global settings
from dev.funcs import generate_keywords

API_KEYS = {
    'reddit_client_id': 'Up2_w6L851Kg_PsN_KJpWA',  # Replace with your Reddit client ID
    'reddit_client_secret': 'bmM2To0THTLo_zL8FuHXUUfDjAcdqg',  # Replace with your Reddit client secret
    'reddit_user_agent': 'python:moneybutt:armand0e',  # Replace with your Reddit user agent
}

SETTINGS = {
    'global_market_keywords': [
        'inflation', 'CPI', 'Federal Reserve', 'interest rates', 'unemployment', 'GDP',
        'economic growth', 'geopolitical risk', 'war', 'Israel', 'Middle East', 'global markets',
        'oil prices', 'natural disasters', 'trade wars', 'tariffs'
    ],  
    'tickers_and_keywords': {
        # keywords can be hardcoded or replaced:
            #"GOOGL": ["Google", "Alphabet", "YouTube", "Android"],
            #"AMZN": ["Amazon", "AWS", "Prime", "Bezos"],
            #"TSLA": ["Tesla", "Musk", "Model 3", "EV"],
            #"NVDA": ["Nvidia", "AI", "GPU", "Blackwell"],
            #"AVGO": ["Broadcomm", "Semiconductor", "GPU", "AI"]
        "AAPL": generate_keywords('AAPL'),
        "MSFT": generate_keywords('MSFT'),
        "GOOGL": generate_keywords('GOOGL'),
        "AMZN": generate_keywords('AMZN'),
        "TSLA": generate_keywords('TSLA'),
        "NVDA": generate_keywords('NVDA'),
        "AVGO": generate_keywords('AVGO')
    }
}

