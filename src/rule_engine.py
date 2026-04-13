import pandas as pd
import numpy as np
import os

def apply_strategy(input_path: str = "data/processed_stock_data.csv", output_path: str = "data/rule_signals.csv") -> None:
    """
    Applies the Mahesh Kaushik Rule-Based Confluence Strategy on multi-ticker data.
    Signals are computed row-wise (vectorized) — the Ticker column is preserved
    but does not affect the boolean logic since each row's indicators already 
    belong to a single company (ensured by the feature engineering step).
    """
    if not os.path.exists(input_path):
        print(f"Error: Processed data not found at {input_path}")
        return

    print("Loading processed data for rule evaluation...")
    df = pd.read_csv(input_path, index_col=0, parse_dates=True)

    if 'Ticker' not in df.columns:
        print("Error: 'Ticker' column not found.")
        return

    print(f"Evaluating rules on {df['Ticker'].nunique()} tickers, {len(df)} rows...")

    # Bull condition (Confluence):
    # Trend alignment + oscillator confirmation + volatility guard
    bull_condition = (
        (df['Close'] > df['DMA_50']) &
        (df['DMA_50'] > df['DMA_200']) &
        (df['Close'] > df['DMA_20']) &
        (df['RSI_14'] > 40) & (df['RSI_14'] < 70) &
        (df['MACD'] > df['MACD_signal']) &
        (df['Close'] <= df['Bollinger_Upper']) &
        (df['Close'] <= df['DMA_200'] * 1.10)
    )

    # Bear condition (Confluence):
    bear_condition = (
        (df['Close'] < df['DMA_50']) &
        (df['DMA_50'] < df['DMA_200']) &
        (df['Close'] < df['DMA_20']) &
        (df['RSI_14'] < 60) & (df['RSI_14'] > 30) &
        (df['MACD'] < df['MACD_signal']) &
        (df['Close'] >= df['Bollinger_Lower']) &
        (df['Close'] >= df['DMA_200'] * 0.90)
    )

    conditions = [bull_condition, bear_condition]
    choices = [1, -1]
    df['Rule_Signal'] = np.select(conditions, choices, default=0)

    # Print per-signal counts
    signal_counts = df['Rule_Signal'].value_counts()
    print(f"\nSignal Distribution:")
    print(f"  Buy  (1) : {signal_counts.get(1, 0)}")
    print(f"  Wait (0) : {signal_counts.get(0, 0)}")
    print(f"  Sell (-1): {signal_counts.get(-1, 0)}")

    # Print per-ticker buy signal stats
    buy_per_ticker = df[df['Rule_Signal'] == 1].groupby('Ticker').size()
    print(f"\nTickers generating Buy signals: {len(buy_per_ticker)}")
    print(f"Total Buy signals across all tickers: {buy_per_ticker.sum()}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path)

    print(f"\nSuccessfully saved rule signals to {output_path}")


if __name__ == "__main__":
    apply_strategy()
