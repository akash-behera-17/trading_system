import pandas as pd
import numpy as np
import os
import pickle
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from autoencoder import LSTMAutoencoder

def create_sequences_for_indices(data, indices, seq_len):
    xs = []
    valid_idxs = []
    for idx in indices:
        if idx >= seq_len - 1:
            xs.append(data[idx - seq_len + 1 : idx + 1])
            valid_idxs.append(idx)
    return np.array(xs), valid_idxs

def evaluate_hybrid_system(signals_path: str = "data/rule_signals.csv", 
                           model_path: str = "models/lstm_autoencoder.pt",
                           scaler_path: str = "models/scaler.pkl",
                           output_path: str = "data/hybrid_results.csv") -> None:
    """
    Merges the rule-based Engine (Opus 4.6 Confluence Edition) with the Unsupervised LSTM-Autoencoder.
    """
    if not os.path.exists(signals_path):
        print(f"Error: Signals data not found at {signals_path}")
        return
        
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        print("Error: Autoencoder model or scaler not found. Run Phase 3 first.")
        return

    print("Loading data and model artifacts...")
    df = pd.read_csv(signals_path, index_col=0, parse_dates=True)
    
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
        
    features = [
        'DMA_20', 'DMA_50', 'DMA_100', 'DMA_200', 
        'RSI_14', 'MACD', 'MACD_signal', 'Volume_Change_Pct',
        'Bollinger_Upper', 'Bollinger_Middle', 'Bollinger_Lower',
        'Distance_to_52W_High', 'Distance_to_52W_Low'
    ]
    
    # Initialize PyTorch Model
    model = LSTMAutoencoder(seq_len=10, n_features=len(features), embedding_dim=16)
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    
    print("Evaluating all Rule_Signal == 1 (Potential Buys) through the LSTM-Autoencoder...")
    
    buy_indices = np.where(df['Rule_Signal'] == 1)[0]
    
    if len(buy_indices) == 0:
        print("No buy signals found to evaluate.")
        return
        
    # Safeguard against missing features or NaNs
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df[features] = df[features].ffill().bfill()
    X_raw = df[features].values
    
    X_scaled = scaler.transform(X_raw)
    
    X_eval, valid_idxs = create_sequences_for_indices(X_scaled, buy_indices, seq_len=10)
    
    if len(X_eval) == 0:
        print("No valid sequences found (too early in history).")
        return
        
    X_tensor = torch.tensor(X_eval, dtype=torch.float32)
    
    criterion = nn.MSELoss(reduction='none')
    
    with torch.no_grad():
        reconstructions = model(X_tensor)
        errors = criterion(reconstructions, X_tensor).mean(dim=(1, 2)).numpy()
        
    df['Reconstruction_Error'] = np.nan
    df['Hybrid_Signal'] = df['Rule_Signal'] 
    
    for i, idx in enumerate(valid_idxs):
        df.iloc[idx, df.columns.get_loc('Reconstruction_Error')] = errors[i]
        
    threshold = np.percentile(errors, 70) 
    print(f"Calculated Anomaly Threshold (70th percentile): {threshold:.4f}")
    
    for i, idx in enumerate(valid_idxs):
        if errors[i] > threshold:
            df.iloc[idx, df.columns.get_loc('Hybrid_Signal')] = 0
            
    total_rule_buys = len(valid_idxs)
    total_hybrid_buys = len([i for i in range(len(valid_idxs)) if errors[i] <= threshold])
    traps_avoided = total_rule_buys - total_hybrid_buys
    
    print("\n" + "="*50)
    print("HYBRID SYSTEM EVALUATION RESULTS")
    print("="*50)
    print(f"Total pure Rule-Based Buys generated : {total_rule_buys}")
    print(f"Total Hybrid Buys (After ML Filter)  : {total_hybrid_buys}")
    print(f"Total Bull Traps Avoided (Vetoed)    : {traps_avoided}")
    print(f"Noise Reduction Rate                 : {(traps_avoided/total_rule_buys)*100:.2f}%")
    print("="*50 + "\n")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path)
    print(f"Saved hybrid evaluation results to {output_path}")

if __name__ == "__main__":
    evaluate_hybrid_system()
