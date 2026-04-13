import pandas as pd
import numpy as np
import ta
import os


def _engineer_single_ticker(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates all technical indicators for a single ticker's DataFrame.
    v2.0: Added ATR, EMA, and Regime detection for the Hybrid Scoring Engine.
    """
    df = df.sort_index().copy()

    # 1. Daily Moving Averages (DMA / SMA)
    df['DMA_20'] = df['Close'].rolling(window=20).mean()
    df['DMA_50'] = df['Close'].rolling(window=50).mean()
    df['DMA_100'] = df['Close'].rolling(window=100).mean()
    df['DMA_200'] = df['Close'].rolling(window=200).mean()

    # 2. Exponential Moving Averages (EMA) — Algorithm 2 requirement
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()

    # 3. RSI - 14 Days
    df['RSI_14'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()

    # 4. MACD
    macd_indicator = ta.trend.MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
    df['MACD'] = macd_indicator.macd()
    df['MACD_signal'] = macd_indicator.macd_signal()
    df['MACD_hist'] = macd_indicator.macd_diff()  # MACD Histogram for momentum strength

    # 5. Volume Change Percentage
    df['Volume_Change_Pct'] = df['Volume'].pct_change() * 100

    # 6. Bollinger Bands (20, 2)
    bollinger = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
    df['Bollinger_Upper'] = bollinger.bollinger_hband()
    df['Bollinger_Middle'] = bollinger.bollinger_mavg()
    df['Bollinger_Lower'] = bollinger.bollinger_lband()
    # Bollinger %B — position within bands (0=lower, 1=upper)
    df['Bollinger_PctB'] = bollinger.bollinger_pband()

    # 7. 52-Week High and Low (252 trading days)
    df['52W_High'] = df['Close'].rolling(window=252).max()
    df['52W_Low'] = df['Close'].rolling(window=252).min()
    df['Distance_to_52W_High'] = (df['Close'] - df['52W_High']) / df['52W_High']
    df['Distance_to_52W_Low'] = (df['Close'] - df['52W_Low']) / df['52W_Low']

    # 8. ATR (Average True Range) — 14 period (Position Sizing + Trailing Stop)
    df['ATR_14'] = ta.volatility.AverageTrueRange(
        high=df['High'], low=df['Low'], close=df['Close'], window=14
    ).average_true_range()

    # 9. Market Regime (EMA Cross)
    df['Regime'] = np.where(df['EMA_50'] > df['EMA_200'], 'Bullish', 'Bearish')

    # 10. Momentum features for XGBoost
    df['Returns_5d'] = df['Close'].pct_change(5) * 100
    df['Returns_10d'] = df['Close'].pct_change(10) * 100
    df['Returns_20d'] = df['Close'].pct_change(20) * 100
    df['Volume_SMA_20'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA_20']

    return df


def engineer_features(input_path: str = "data/raw_stock_data.csv", output_path: str = "data/processed_stock_data.csv") -> None:
    """
    Calculates technical indicators PER TICKER using groupby.
    v2.0: Added ATR, EMA, Regime, Momentum features.
    """
    if not os.path.exists(input_path):
        print(f"Error: Raw data not found at {input_path}")
        return

    print("Loading raw stock data...")
    df = pd.read_csv(input_path, index_col=0, parse_dates=True)

    if 'Ticker' not in df.columns:
        print("Error: 'Ticker' column not found.")
        return

    print(f"Processing {df['Ticker'].nunique()} tickers (v2.0 with ATR, EMA, Regime)...")
    print(f"Total rows before feature engineering: {len(df)}")

    processed_frames = []
    for ticker, group in df.groupby('Ticker'):
        try:
            engineered = _engineer_single_ticker(group)
            processed_frames.append(engineered)
        except Exception as e:
            print(f"  Skipping {ticker}: {e}")
            continue

    result = pd.concat(processed_frames)
    result.replace([np.inf, -np.inf], np.nan, inplace=True)

    critical_cols = ['DMA_20', 'DMA_50', 'DMA_100', 'DMA_200', 'RSI_14',
                     'MACD', 'MACD_signal', 'Volume_Change_Pct',
                     'Bollinger_Upper', 'Bollinger_Middle', 'Bollinger_Lower',
                     'Distance_to_52W_High', 'Distance_to_52W_Low',
                     'ATR_14', 'EMA_50', 'EMA_200']
    result.dropna(subset=critical_cols, inplace=True)

    print(f"Total rows after dropping NaNs: {len(result)}")
    print(f"Tickers remaining: {result['Ticker'].nunique()}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.to_csv(output_path)
    print(f"Successfully saved processed data to {output_path}")


if __name__ == "__main__":
    engineer_features()
