# ethics/test_ethics_checker.py

from ethics_checker import EthicsChecker

def test_ethics_checker():
    # Test with a high positive sentiment score
    checker = EthicsChecker(0.6)
    checker.check_for_ethical_issues()

    # Test with a high negative sentiment score
    checker = EthicsChecker(-0.6)
    checker.check_for_ethical_issues()

    # Test with a neutral sentiment score
    checker = EthicsChecker(0.0)
    checker.check_for_ethical_issues()

    # Output test result
    print("EthicsChecker test passed.")

if __name__ == "__main__":
    test_ethics_checker()

# Debugging Instructions:
# - Run this script to test the ethics checking functionality.
# - Ensure that the warnings are triggered for high positive or negative sentiment scores.
# - Modify the sentiment score to see how the ethics warnings change.