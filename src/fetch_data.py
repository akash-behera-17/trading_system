import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

# ==============================
# FULL MULTI-SECTOR STOCK UNIVERSE (170 NSE Stocks)
# ==============================
STOCK_LIST = [
    "DIXON", "GODFRYPHLP", "SJVN", "PAGEIND", "BAJAJHFL", "TRENT", "UBL",
    "JUBLFOOD", "MAZDOCK", "NIACL", "KPRMILL", "PIIND", "SOLARINDS", "CRISIL",
    "SUPREMEIND", "DMART", "TIINDIA", "ITC", "COLPAL", "MANKIND", "IREDA",
    "MAXHEALTH", "PFC", "DLF", "INDIGO", "DEEPAKNTR", "ABBOTINDIA", "COCHINSHIP",
    "TATATECH", "POWERGRID", "ACC", "IRCTC", "CGPOWER", "HAVELLS", "KPITTECH",
    "IGL", "CONCOR", "BALKRISIND", "GODREJPROP", "EXIDEIND", "GAIL", "NHPC",
    "HAL", "ABB", "HINDUNILVR", "ADANIENT", "ICICIBANK", "ZYDUSLIFE", "NAUKRI",
    "INDHOTEL", "GUJGASLTD", "BERGEPAINT", "TORNTPOWER", "COFORGE", "LICI",
    "SBICARD", "APOLLOHOSP", "JSWENERGY", "TATAPOWER", "IRFC", "ONGC",
    "BAJFINANCE", "PIDILITIND", "PETRONET", "CIPLA", "SIEMENS", "TCS", "NTPC",
    "COROMANDEL", "DABUR", "HDFCLIFE", "ULTRACEMCO", "AMBUJACEM", "DIVISLAB",
    "ASTRAL", "DRREDDY", "LTTS", "JIOFIN", "BAJAJFINSV", "VBL", "SUNPHARMA",
    "RVNL", "HUDCO", "OIL", "ICICIGI", "HDFCBANK", "SRF", "VOLTAS",
    "POLICYBZR", "BOSCHLTD", "COALINDIA", "HDFCAMC", "GRASIM", "ADANIGREEN",
    "GODREJCP", "PRESTIGE", "AUROPHARMA", "ALKEM", "APOLLOTYRE", "BEL",
    "MPHASIS", "APARINDS", "HCLTECH", "KOTAKBANK", "LUPIN", "WIPRO", "MRF",
    "FORTIS", "MARICO", "TATACONSUM", "TECHM", "INFY", "BRITANNIA", "TATACOMM",
    "ADANIPORTS", "NESTLEIND", "CHOLAFIN", "JINDALSTEL", "JSWSTEEL", "BSE",
    "AXISBANK", "BHARTIARTL", "SUNDARMFIN", "ESCORTS", "UNIONBANK", "TORNTPHARM",
    "BAJAJ-AUTO", "RELIANCE", "PERSISTENT", "ASIANPAINT", "IOC", "INDUSINDBK",
    "TATASTEEL", "SBILIFE", "POLYCAB", "INDUSTOWER", "TITAN", "M&M", "NMDC",
    "UPL", "LTIM", "BPCL", "APLAPOLLO", "SAIL", "SBIN", "BHARATFORG",
    "ADANIPOWER", "HINDPETRO", "BHEL", "BANKBARODA", "KEI", "IDFCFIRSTB",
    "MOTHERSON", "EICHERMOT", "MARUTI", "HEROMOTOCO", "AIAENG", "TVSMOTOR",
    "CUMMINSIND", "HINDALCO", "FEDERALBNK", "VEDL", "AUBANK", "HINDZINC",
    "CANBK", "MUTHOOTFIN", "ASHOKLEY", "LTF", "SHRIRAMFIN", "NATIONALUM"
]


def fetch_stock_data(tickers: list = None, years: int = 5, output_dir: str = "data") -> None:
    """
    Fetches raw daily stock data for ALL tickers in the universe.
    Combines into a single DataFrame with a 'Ticker' column.
    """
    if tickers is None:
        tickers = [t + ".NS" for t in STOCK_LIST]

    print(f"Fetching {years} years of data for {len(tickers)} stocks...")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)

    try:
        # Download all tickers at once (threaded for speed)
        data = yf.download(
            tickers,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            group_by="ticker",
            threads=True
        )

        if data.empty:
            print("Error: No data returned from yfinance.")
            return

        # Parse the multi-index columns into per-ticker DataFrames
        all_frames = []
        for ticker in tickers:
            try:
                if len(tickers) == 1:
                    df_ticker = data.copy()
                else:
                    df_ticker = data[ticker].copy()

                # Handle potential sub-MultiIndex
                if isinstance(df_ticker.columns, pd.MultiIndex):
                    df_ticker.columns = df_ticker.columns.droplevel(1)

                df_ticker = df_ticker[['Open', 'High', 'Low', 'Close', 'Volume']]
                df_ticker = df_ticker.dropna(subset=['Close'])

                if len(df_ticker) < 200:
                    continue

                df_ticker['Ticker'] = ticker
                all_frames.append(df_ticker)
            except Exception:
                continue

        if not all_frames:
            print("Error: No valid stock data after filtering.")
            return

        combined = pd.concat(all_frames)
        combined.index.name = 'Date'

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "raw_stock_data.csv")
        combined.to_csv(output_path)

        unique_tickers = combined['Ticker'].nunique()
        print(f"Successfully saved {len(combined)} rows for {unique_tickers} stocks to {output_path}")

    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    fetch_stock_data()
