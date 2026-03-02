import pandas as pd
import numpy as np
import os
import pickle
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from autoencoder import LSTMAutoencoder

def evaluate_hybrid_system(signals_path: str = "data/rule_signals.csv", 
                           model_path: str = "models/lstm_autoencoder.pt",
                           scaler_path: str = "models/scaler.pkl",
                           output_path: str = "data/hybrid_results.csv") -> None:
    """
    Merges the rule-based Engine (Mahesh Kaushik Strategy) with the Unsupervised LSTM-Autoencoder.
    Rule logic + ML filtering = Hybrid Neuro-Symbolic Trading.
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
        
    features = ['DMA_50', 'DMA_100', 'DMA_200', 'RSI_14', 'MACD', 'MACD_signal', 'Volume_Change_Pct']
    
    # Initialize PyTorch Model
    model = LSTMAutoencoder(seq_len=1, n_features=len(features), embedding_dim=4)
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    
    print("Evaluating all Rule_Signal == 1 (Potential Buys) through the Autoencoder...")
    
    # We only care about vetoing "Buy" signals (Bull Traps). We leave sells and waits alone.
    buy_signals = df[df['Rule_Signal'] == 1].copy()
    
    if len(buy_signals) == 0:
        print("No buy signals found to evaluate.")
        return
        
    X_eval = buy_signals[features].values
    X_eval_scaled = scaler.transform(X_eval)
    
    X_tensor = torch.tensor(X_eval_scaled, dtype=torch.float32).unsqueeze(1)
    
    # Calculate Reconstruction Error for each sample
    criterion = nn.MSELoss(reduction='none')
    
    with torch.no_grad():
        reconstructions = model(X_tensor)
        # Calculate MSE per sample across all features
        errors = criterion(reconstructions, X_tensor).mean(dim=(1, 2)).numpy()
        
    buy_signals['Reconstruction_Error'] = errors
    
    # Define Anomaly Threshold
    # E.g., Top 30% of highest errors are considered "Bull Traps"
    threshold = np.percentile(errors, 70) 
    print(f"Calculated Anomaly Threshold (70th percentile): {threshold:.4f}")
    
    # Hybrid Logic: If error is higher than threshold, it's a Trap (Override to 0)
    buy_signals['Hybrid_Signal'] = np.where(buy_signals['Reconstruction_Error'] > threshold, 0, 1)
    
    # Merge back into main dataframe
    df['Reconstruction_Error'] = np.nan
    df['Hybrid_Signal'] = df['Rule_Signal'] # Default to rule signal
    
    # Update only the evaluated rows
    df.loc[buy_signals.index, 'Reconstruction_Error'] = buy_signals['Reconstruction_Error']
    df.loc[buy_signals.index, 'Hybrid_Signal'] = buy_signals['Hybrid_Signal']
    
    # Calculate Metrics
    total_rule_buys = len(buy_signals)
    total_hybrid_buys = len(df[df['Hybrid_Signal'] == 1])
    traps_avoided = total_rule_buys - total_hybrid_buys
    
    print("\n" + "="*50)
    print("HYBRID SYSTEM EVALUATION RESULTS")
    print("="*50)
    print(f"Total pure Rule-Based Buys generated : {total_rule_buys}")
    print(f"Total Hybrid Buys (After ML Filter)  : {total_hybrid_buys}")
    print(f"Total Bull Traps Avoided (Vetoed)    : {traps_avoided}")
    print(f"Noise Reduction Rate                 : {(traps_avoided/total_rule_buys)*100:.2f}%")
    print("="*50 + "\n")
    
    # Save the output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path)
    print(f"Saved hybrid evaluation results to {output_path}")

if __name__ == "__main__":
    evaluate_hybrid_system()
