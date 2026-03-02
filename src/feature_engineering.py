import pandas as pd
import numpy as np
import ta
import os

def engineer_features(input_path: str = "data/raw_stock_data.csv", output_path: str = "data/processed_stock_data.csv") -> None:
    """
    Calculates technical indicators for the rule-based engine and the LSTM-Autoencoder.
    - 50, 100, 200 DMA
    - RSI (14)
    - MACD, MACD Signal
    - Volume Change %
    """
    
    # Check if raw data exists
    if not os.path.exists(input_path):
        print(f"Error: Raw data not found at {input_path}")
        return

    print("Loading raw stock data...")
    df = pd.read_csv(input_path, index_col=0, parse_dates=True)
    
    print("Calculating technical indicators...")
    
    # 1. Daily Moving Averages (DMA)
    df['DMA_50'] = df['Close'].rolling(window=50).mean()
    df['DMA_100'] = df['Close'].rolling(window=100).mean()
    df['DMA_200'] = df['Close'].rolling(window=200).mean()
    
    # 2. Relative Strength Index (RSI) - 14 Days
    df['RSI_14'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    
    # 3. MACD
    macd_indicator = ta.trend.MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
    df['MACD'] = macd_indicator.macd()
    df['MACD_signal'] = macd_indicator.macd_signal()
    
    # 4. Volume Change Percentage
    df['Volume_Change_Pct'] = df['Volume'].pct_change() * 100
    
    # Drop NaNs created by rolling windows (e.g., first 200 days will be NaN due to DMA_200)
    print(f"Rows before dropping NaNs: {len(df)}")
    df.dropna(inplace=True)
    print(f"Rows after dropping NaNs: {len(df)}")
    
    # Save the processed output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path)
    
    print(f"Successfully saved processed data to {output_path}")

if __name__ == "__main__":
    engineer_features()
