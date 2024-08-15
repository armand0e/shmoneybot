# $hmoneybot

This project implements an enhanced trading bot that integrates technical analysis, sentiment analysis (including Reddit and GNews), and market sentiment analysis based on economic indicators like Inflation, CPI, and key statements from influential figures.

## Project Structure
```
ShmoneyBot/
│
├── README.md
├── config.py
├── cli.py
│
├── data/
│   ├── data_fetcher.py
│   ├── financial_data_fetcher.py
│   ├── test_data_fetcher.py
│
├── news/
│   ├── gdelt_fetcher.py
│   ├── web_scraper.py
│   ├── reddit_news_fetcher.py
│   ├── test_gdelt_fetcher.py
│   ├── test_reddit_news_fetcher.py
│
├── sentiment/
│   ├── sentiment_analyzer.py
│   ├── advanced_sentiment_analyzer.py
│   ├── reddit_sentiment.py
│   ├── test_sentiment_analyzer.py
│   ├── test_reddit_sentiment.py
│
├── strategy/
│   ├── decision_engine.py
│   ├── test_decision_engine.py
│
└── ethics/
├── ethics_checker.py
├── test_ethics_checker.py
```
## File Descriptions and Debugging Instructions

### `config.py`
- **Description**: Contains API keys and global settings.
- **Debugging**: Ensure API keys are correct and that the settings are properly configured.

### `cli.py`
- **Description**: The command-line interface for interacting with the bot. It allows you to run the entire pipeline or specific parts.
- **Debugging**: Run with various stock symbols and check if the flow executes as expected.

### `data/`
- **data_fetcher.py**: Fetches historical data for stocks. Uses APIs like Interactive Brokers.
  - **Debugging**: Check if it correctly fetches data for different stock symbols.
- **financial_data_fetcher.py**: Fetches real-time stock data using Yahoo Finance API.
  - **Debugging**: Ensure it retrieves accurate real-time data for the stock symbols.
- **test_data_fetcher.py**: Test script to validate data fetching.
  - **Debugging**: Run the test and ensure the data output matches expectations.

### `news/`
- **gdelt_fetcher.py**: Fetches tone chart data from GDELT.
  - **Debugging**: Ensure the API returns the correct tone chart data for given stock symbols.
- **web_scraper.py**: Scrapes live news from financial websites.
  - **Debugging**: Ensure the scraper captures relevant headlines and descriptions.
- **reddit_news_fetcher.py**: Fetches news-related posts from relevant subreddits.
  - **Debugging**: Ensure the correct subreddit is linked to the stock and that news data is accurately fetched.
- **test_gdelt_fetcher.py**: Test script for GDELT tone chart fetching.
  - **Debugging**: Verify the tone chart data and sentiment analysis results.
- **test_reddit_news_fetcher.py**: Test script for Reddit news fetching.
  - **Debugging**: Test with sample posts and verify the news data output.

### `sentiment/`
- **advanced_sentiment_analyzer.py**: Analyzes sentiment of news articles using an advanced transformer-based model.
  - **Debugging**: Check the sentiment score outputs for accuracy using advanced NLP techniques.
- **sentiment_analyzer.py**: Basic sentiment analysis using VADER.
  - **Debugging**: Verify that the sentiment score is accurate for given inputs.
- **reddit_sentiment.py**: Fetches and analyzes sentiment of Reddit posts related to stocks.
  - **Debugging**: Ensure the correct subreddit is linked to the stock and that sentiment analysis reflects the content.
- **test_sentiment_analyzer.py**: Test script for advanced sentiment analysis.
  - **Debugging**: Run test cases with predefined articles.
- **test_reddit_sentiment.py**: Test script for Reddit sentiment analysis.
  - **Debugging**: Test with sample posts and verify the sentiment output.

### `strategy/`
- **decision_engine.py**: Combines technical data and sentiment to make trading decisions.
  - **Debugging**: Test with various data and sentiment inputs to ensure decisions are logical.
- **test_decision_engine.py**: Test script for decision making.
  - **Debugging**: Validate decision outputs based on sample inputs.

### `ethics/`
- **ethics_checker.py**: Checks for ethical concerns, like avoiding trades based on manipulative sentiment.
  - **Debugging**: Ensure the checker raises warnings for extreme sentiment scores.
- **test_ethics_checker.py**: Test script for ethics checks.
  - **Debugging**: Test with different sentiment scores to ensure proper functioning.

---

## Running the Bot

To run the bot, execute the following command:

```bash
python cli.py SYMBOL
```
Replace `SYMBOL` with the stock you want to analyze.

