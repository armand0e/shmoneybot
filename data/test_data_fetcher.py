# data/test_data_fetcher.py

from data_fetcher import DataFetcher

def test_data_fetcher():
    # Create an instance of DataFetcher for a sample stock symbol
    fetcher = DataFetcher("AAPL")

    # Fetch the historical data
    data = fetcher.get_historical_data()

    # Perform basic assertions to verify the data
    assert isinstance(data, list), "Data should be returned as a list"
    assert len(data) > 0, "Data list should not be empty"
    assert all(isinstance(x, (int, float)) for x in data), "All elements in data list should be numeric"

    # Output test result
    print("DataFetcher test passed.")

if __name__ == "__main__":
    test_data_fetcher()

# Debugging Instructions:
# - Run this script to test the data fetching functionality.
# - Check the assertions to ensure the data is correctly formatted.
# - Replace the stock symbol and re-run to test with different inputs.