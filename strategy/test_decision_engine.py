# strategy/test_decision_engine.py

from decision_engine import DecisionEngine

def test_decision_engine():
    # Test with sample historical data and sentiment score
    historical_data = [100, 102, 101, 105, 110]
    sentiment_score = 0.3

    # Create an instance of DecisionEngine
    engine = DecisionEngine(historical_data, sentiment_score)

    # Evaluate the stock
    decision = engine.evaluate_stock()

    # Perform basic assertions to verify the decision
    assert decision in ["Buy", "Sell", "Hold"], "Decision should be one of 'Buy', 'Sell', or 'Hold'"

    # Output test result
    print(f"DecisionEngine test passed with decision: {decision}")

if __name__ == "__main__":
    test_decision_engine()

# Debugging Instructions:
# - Run this script to test the decision-making functionality.
# - Check the assertions to ensure the decision logic is working correctly.
# - Modify the historical data and sentiment score to see how the decision changes.