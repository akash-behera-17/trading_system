import pandas as pd
import numpy as np
import os

def apply_strategy(input_path: str = "data/processed_stock_data.csv", output_path: str = "data/rule_signals.csv") -> None:
    """
    Applies the Mahesh Kaushik Rule-Based Strategy.
    - Bull Zone (Potential Buy, 1): Close > 50 DMA > 100 DMA > 200 DMA AND Close <= 200 DMA * 1.10
    - Bear Zone (Potential Sell, -1): Close < 50 DMA < 100 DMA < 200 DMA AND Close >= 200 DMA * 0.90
    - Unconfirmed (Wait, 0): All other conditions
    """
    if not os.path.exists(input_path):
        print(f"Error: Processed data not found at {input_path}")
        return

    print("Loading processed data for rule evaluation...")
    df = pd.read_csv(input_path, index_col=0, parse_dates=True)
    
    # Define conditions
    # Bull condition
    bull_condition = (
        (df['Close'] > df['DMA_50']) &
        (df['DMA_50'] > df['DMA_100']) &
        (df['DMA_100'] > df['DMA_200']) &
        (df['Close'] <= df['DMA_200'] * 1.10)
    )
    
    # Bear condition
    bear_condition = (
        (df['Close'] < df['DMA_50']) &
        (df['DMA_50'] < df['DMA_100']) &
        (df['DMA_100'] < df['DMA_200']) &
        (df['Close'] >= df['DMA_200'] * 0.90)
    )
    
    # Assign signals based on conditions using np.select
    conditions = [bull_condition, bear_condition]
    choices = [1, -1] # 1 for Buy, -1 for Sell
    
    # Default is 0 (Wait)
    df['Rule_Signal'] = np.select(conditions, choices, default=0)
    
    print(f"Signal Counts:\n{df['Rule_Signal'].value_counts()}")
    
    # Save the output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path)
    
    print(f"Successfully evaluated rules and saved signals to {output_path}")

if __name__ == "__main__":
    apply_strategy()
