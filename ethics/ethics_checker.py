# ethics/ethics_checker.py

import logging

class EthicsChecker:
    def __init__(self, sentiment_score):
        self.sentiment_score = sentiment_score

    def check_for_ethical_issues(self):
        logging.info("Performing ethics check")

        if self.sentiment_score > 0.5:
            logging.warning("High positive sentiment. Ensure this is not due to manipulative reporting.")
        elif self.sentiment_score < -0.5:
            logging.warning("High negative sentiment. Avoid trading on potentially false or manipulative news.")

# Debugging Instructions:
# - Test with extreme sentiment scores to see if the ethics warnings are triggered.
# - Use the test script to validate the ethics checking process.
# - Ensure that the logic aligns with ethical trading practices.