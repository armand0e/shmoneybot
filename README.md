# MoneyBot: A Python-Based Trading Bot

MoneyBot is a Python-based trading bot designed to analyze financial data, sentiment, and market news to make informed trading decisions. The bot leverages multiple data sources, including Reddit, GDELT, and financial APIs, to gather comprehensive insights for stock trading.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Components](#components)
   - [Financial Data Fetcher](#financial-data-fetcher)
   - [Sentiment Analysis](#sentiment-analysis)
   - [News Fetching](#news-fetching)
   - [Stock Evaluation](#stock-evaluation)
6. [Contributing](#contributing)
7. [License](#license)

## Project Overview

MoneyBot is designed to assist traders in making data-driven decisions. By combining technical analysis, sentiment analysis, and world news, the bot evaluates stock performance and provides a recommendation to buy, sell, or hold a particular stock.

## Project Structure

The project is organized into a single script with logical class separation:

\```
moneybot/
├── config.py          # Configuration file for API keys and settings
├── moneybot.py        # Main script containing all the functionality (combined main and stock logic)
├── news.py            # Contains classes for fetching news from Reddit and GDELT
├── sentiment.py       # Handles sentiment analysis and ethical considerations
├── requirements.txt   # List of required Python packages
└── README.md          # Project documentation
\```

## Installation

1. **Clone the repository**:
   \```bash
   git clone https://github.com/yourusername/moneybot.git
   cd moneybot
   \```

2. **Install the required dependencies**:
   Ensure you have Python 3.7+ installed, then install the dependencies:
   \```bash
   pip install -r requirements.txt
   \```

3. **Set up your API keys**:
   Add your API keys in `config.py`. Example:
   \```python
   API_KEYS = {
       'reddit_client_id': 'your_client_id',
       'reddit_client_secret': 'your_client_secret',
       'reddit_user_agent': 'your_user_agent',
       # Add other API keys here if needed
   }
   \```

## Usage

To run the bot for a specific stock, use the following command:

\```bash
./moneybot.py AAPL
\```

Replace `AAPL` with the ticker symbol of the stock you want to analyze.

## Components

### Financial Data Fetcher

The `FinancialDataFetcher` class is responsible for fetching real-time and historical financial data for a given stock ticker using Yahoo Finance.

### Sentiment Analysis

The bot uses the `AdvancedSentimentAnalyzer` class to analyze sentiment from news articles and Reddit posts. It calculates a sentiment score that influences the trading decision.

### News Fetching

The script includes functionality to fetch news from various sources:
- **RedditNewsFetcher**: Searches Reddit for the largest relevant subreddit and fetches the latest posts.
- **GDELTFetcher**: Fetches global and market-related news using the GDELT API.

### Stock Evaluation

The `Stock` class consolidates all functionality:
- **fetch_historical_data**: Fetches historical closing prices for the stock.
- **fetch_news**: Retrieves relevant news from Reddit.
- **fetch_world_news**: Fetches broader market and world news using GDELT.
- **calculate_sentiment_score**: Analyzes the sentiment of the collected news.
- **calculate_technical_score**: Analyzes the historical data to determine the stock's technical score.
- **calculate_overall_reliability**: Computes an overall reliability score based on sentiment and technical analysis.
- **evaluate**: Combines all the collected data and scores to make a final trading decision (Buy, Sell, Hold).

The `evaluate` method in the `Stock` class automatically performs all the necessary data fetching and analysis steps, providing a final recommendation based on pre-configured thresholds.

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch: \```git checkout -b feature-branch-name\```
3. Make your changes and commit them: \```git commit -m 'Add some feature'\```
4. Push to the branch: \```git push origin feature-branch-name\```
5. Submit a pull request.

Please ensure your code adheres to the project's coding standards and includes relevant documentation.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.