import pandas as pd
import numpy as np
import yfinance as yf
import ta
import pickle
import torch
import torch.nn as nn
from datetime import datetime, timedelta
import argparse

# Same Autoencoder Class Definition for Loading
class LSTMAutoencoder(nn.Module):
    def __init__(self, seq_len, n_features, embedding_dim=16):
        super(LSTMAutoencoder, self).__init__()
        self.seq_len = seq_len
        self.n_features = n_features
        self.embedding_dim = embedding_dim

        self.encoder = nn.LSTM(input_size=n_features, hidden_size=embedding_dim, num_layers=1, batch_first=True)
        self.decoder = nn.LSTM(input_size=embedding_dim, hidden_size=n_features, num_layers=1, batch_first=True)

    def forward(self, x):
        encoded_out, (hidden_n, cell_n) = self.encoder(x)
        hidden_n = hidden_n.squeeze(0).unsqueeze(1)
        hidden_n_repeated = hidden_n.repeat(1, self.seq_len, 1)
        decoded_out, _ = self.decoder(hidden_n_repeated)
        return decoded_out

def fetch_recent_data(ticker, days=300):
    """Fetches recent data necessary to calculate up to a 200-Day Moving Average."""
    print(f"Fetching recent data for {ticker}...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    
    if len(data) < 200:
        raise ValueError(f"Not enough data fetched for {ticker} to calculate 200 DMA.")
        
    return data[['Open', 'High', 'Low', 'Close', 'Volume']]

def engineer_features(df):
    """Calculates indicators on the live dataframe."""
    df = df.copy()
    df['DMA_50'] = df['Close'].rolling(window=50).mean()
    df['DMA_100'] = df['Close'].rolling(window=100).mean()
    df['DMA_200'] = df['Close'].rolling(window=200).mean()
    df['RSI_14'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    macd_indicator = ta.trend.MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
    df['MACD'] = macd_indicator.macd()
    df['MACD_signal'] = macd_indicator.macd_signal()
    df['Volume_Change_Pct'] = df['Volume'].pct_change() * 100
    
    return df.dropna().iloc[-1:] # Return only the latest day

def predict_signal(ticker):
    print("="*50)
    print(f"LIVE INFERENCE: {ticker}")
    print("="*50)
    
    # 1. Fetch Data
    try:
        df_raw = fetch_recent_data(ticker)
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return
        
    # 2. Engineer Features
    latest_day = engineer_features(df_raw)
    current_close = latest_day['Close'].values[0]
    date = latest_day.index[0].strftime('%Y-%m-%d')
    
    print(f"Latest Date : {date}")
    print(f"Close Price : Rs. {current_close:.2f}\n")
    
    # 3. Rule Engine (Mahesh Kaushik Strategy)
    bull_condition = (
        (latest_day['Close'] > latest_day['DMA_50']) &
        (latest_day['DMA_50'] > latest_day['DMA_100']) &
        (latest_day['DMA_100'] > latest_day['DMA_200']) &
        (latest_day['Close'] <= latest_day['DMA_200'] * 1.10)
    ).values[0]
    
    bear_condition = (
        (latest_day['Close'] < latest_day['DMA_50']) &
        (latest_day['DMA_50'] < latest_day['DMA_100']) &
        (latest_day['DMA_100'] < latest_day['DMA_200']) &
        (latest_day['Close'] >= latest_day['DMA_200'] * 0.90)
    ).values[0]
    
    rule_signal = 0
    if bull_condition: rule_signal = 1
    elif bear_condition: rule_signal = -1
    
    if rule_signal == -1:
        print("Recommendation: SELL (Bear Zone Detected)")
        return
    elif rule_signal == 0:
        print("Recommendation: WAIT (Unconfirmed Zone)")
        return
        
    print("Rule Engine  : POTENTIAL BUY (Bull Zone Detected)")
    print("Validating signal integrity via Deep Learning Autoencoder...")
    
    # 4. Autoencoder Check (Trap Detection)
    # Load Model artifacts
    try:
        with open("models/scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
            
        features = ['DMA_50', 'DMA_100', 'DMA_200', 'RSI_14', 'MACD', 'MACD_signal', 'Volume_Change_Pct']
        X_eval = latest_day[features].values
        X_eval_scaled = scaler.transform(X_eval)
        
        model = LSTMAutoencoder(seq_len=1, n_features=len(features), embedding_dim=4)
        model.load_state_dict(torch.load("models/lstm_autoencoder.pt", weights_only=True))
        model.eval()
        
        X_tensor = torch.tensor(X_eval_scaled, dtype=torch.float32).unsqueeze(1)
        criterion = nn.MSELoss(reduction='none')
        
        with torch.no_grad():
            reconstructions = model(X_tensor)
            error = criterion(reconstructions, X_tensor).mean().item()
            
        print(f"Reconstruction Error: {error:.4f}")
        
        # Threshold hardcoded from Phase 4 evaluation: 4.6290
        # For a robust script, this should ideally be loaded dynamically, but this fits the standalone demo purpose.
        THRESHOLD = 4.6290 
        
        if error >= THRESHOLD:
            print(f"ML Filter Result  : ANOMALY DETECTED (Threshold = {THRESHOLD})")
            print("Recommendation    : AVOID (BULL TRAP) ❌")
        else:
            print("ML Filter Result  : STRUCTURE VERIFIED")
            print("Recommendation    : STRONG BUY ✅")
            
    except Exception as e:
        print(f"Error during ML filtering: {e}")
        print("Returning pure rule-based recommendation.")
        print("Recommendation: POTENTIAL BUY (Warning: ML Validation Failed)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live Stock Direction Inference")
    parser.add_argument("--ticker", type=str, default="RELIANCE.NS", help="Ticker symbol (default: RELIANCE.NS)")
    args = parser.parse_args()
    
    predict_signal(args.ticker)
