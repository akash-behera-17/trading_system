import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

def fetch_stock_data(ticker: str, years: int = 5, output_dir: str = "data") -> None:
    """
    Fetches raw daily stock data for a given ticker and saves it to a CSV file.
    Only includes Open, High, Low, Close, Volume.
    """
    print(f"Fetching {years} years of data for {ticker}...")
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)
    
    # Fetch data
    try:
        data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        
        if data.empty:
            print(f"Error: No data found for {ticker}.")
            return

        # Keep only required columns and clean up multi-index columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
            
        data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, "raw_stock_data.csv")
        data.to_csv(output_path)
        
        print(f"Successfully saved {len(data)} rows of data to {output_path}")
        
    except Exception as e:
        print(f"An error occurred while fetching data: {e}")

if __name__ == "__main__":
    # You can change the ticker here. Using RELIANCE.NS as the default.
    target_ticker = "RELIANCE.NS"
    fetch_stock_data(target_ticker)
