# news/test_gdelt_fetcher.py

from gdelt_fetcher import GDELTFetcher

def test_gdelt_fetcher():
    # Create an instance of GDELTFetcher for a sample stock symbol
    fetcher = GDELTFetcher("AAPL")

    # Fetch the tone chart data
    tone_chart_data = fetcher.fetch_gdelt_tone_chart()

    # Perform basic assertions to verify the fetched tone chart data
    assert isinstance(tone_chart_data, dict), "Tone chart data should be returned as a dictionary"
    assert len(tone_chart_data) > 0, "Tone chart data should not be empty"

    # Output test result
    print(f"GDELTFetcher test passed. Fetched tone chart data with {len(tone_chart_data)} entries.")

if __name__ == "__main__":
    test_gdelt_fetcher()

# Debugging Instructions:
# - Run this script to test the GDELT tone chart fetching functionality.
# - Check the assertions to ensure the tone chart data is correctly formatted.
# - Replace the stock symbol and re-run to test with different inputs.