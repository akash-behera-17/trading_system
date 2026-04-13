"""
Research Paper Metrics Calculator (Multi-Stock Edition).
Computes MAPE, RMSE, MAE, R2, and Prediction Accuracy (Win Rate)
on the full multi-ticker hybrid dataset.
"""

import pandas as pd
import numpy as np
import os
import pickle
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from autoencoder import LSTMAutoencoder
import torch
import torch.nn as nn
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error


def create_sequences_for_indices(data, indices, seq_len):
    xs = []
    valid_idxs = []
    for idx in indices:
        if idx >= seq_len - 1:
            xs.append(data[idx - seq_len + 1 : idx + 1])
            valid_idxs.append(idx)
    return np.array(xs) if xs else np.array([]).reshape(0, seq_len, data.shape[1]), valid_idxs


def calculate_metrics():
    signals_path = "data/hybrid_results.csv"
    model_path = "models/lstm_autoencoder.pt"
    scaler_path = "models/scaler.pkl"

    print("Loading hybrid results...")
    df = pd.read_csv(signals_path, index_col=0, parse_dates=True)

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(subset=['Close'], inplace=True)

    has_ticker = 'Ticker' in df.columns

    # === PREDICTION ACCURACY (WIN RATE) ===
    # Calculate Success per ticker to prevent cross-stock lookahead
    if has_ticker:
        success_frames = []
        for ticker, group in df.groupby('Ticker'):
            group = group.sort_index().copy()
            group['Max_Next_10_Days'] = group['Close'].rolling(window=10).max().shift(-10)
            group['Min_Next_10_Days'] = group['Close'].rolling(window=10).min().shift(-10)
            group['Is_Success'] = (
                (group['Max_Next_10_Days'] >= group['Close'] * 1.05) &
                (group['Min_Next_10_Days'] > group['Close'] * 0.97)
            )
            success_frames.append(group)
        df = pd.concat(success_frames)
    else:
        df['Max_Next_10_Days'] = df['Close'].rolling(window=10).max().shift(-10)
        df['Min_Next_10_Days'] = df['Close'].rolling(window=10).min().shift(-10)
        df['Is_Success'] = (
            (df['Max_Next_10_Days'] >= df['Close'] * 1.05) &
            (df['Min_Next_10_Days'] > df['Close'] * 0.97)
        )

    rule_buys = df[df['Rule_Signal'] == 1]
    rule_success = int(rule_buys['Is_Success'].sum())
    rule_accuracy = (rule_success / len(rule_buys)) * 100 if len(rule_buys) > 0 else 0

    # Hybrid buys: Only signals where Rule_Signal=1 AND Hybrid_Signal=1 (passed scoring)
    hybrid_buys = df[(df['Rule_Signal'] == 1) & (df['Hybrid_Signal'] == 1)]
    hybrid_success = int(hybrid_buys['Is_Success'].sum())
    hybrid_accuracy = (hybrid_success / len(hybrid_buys)) * 100 if len(hybrid_buys) > 0 else 0

    noise_reduction = ((len(rule_buys) - len(hybrid_buys)) / len(rule_buys) * 100) if len(rule_buys) > 0 else 0

    accuracy_output = f"""
==================================================
PREDICTION ACCURACY (WIN RATE) — MULTI-STOCK
==================================================
Stock Universe           : {df['Ticker'].nunique() if has_ticker else 1} tickers
Evaluation Period        : {df.index.min()} to {df.index.max()}
Pure Rule-Based Accuracy : {rule_accuracy:.2f}% ({rule_success}/{len(rule_buys)} successful trades)
Hybrid Model Accuracy    : {hybrid_accuracy:.2f}% ({hybrid_success}/{len(hybrid_buys)} successful trades)
Accuracy Improvement     : +{hybrid_accuracy - rule_accuracy:.2f}% (absolute)
Noise Reduction Rate     : {noise_reduction:.2f}% (Bull Traps Vetoed)
==================================================
"""
    print(accuracy_output)

    # === AUTOENCODER RECONSTRUCTION METRICS ===
    features = [
        'DMA_20', 'DMA_50', 'DMA_100', 'DMA_200',
        'RSI_14', 'MACD', 'MACD_signal', 'Volume_Change_Pct',
        'Bollinger_Upper', 'Bollinger_Middle', 'Bollinger_Lower',
        'Distance_to_52W_High', 'Distance_to_52W_Low'
    ]
    df[features] = df[features].ffill().bfill()

    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    # Load autoencoder with saved hyperparameters
    ae_hp_path = "models/ae_hyperparams.pkl"
    if os.path.exists(ae_hp_path):
        with open(ae_hp_path, "rb") as f:
            hp = pickle.load(f)
        model = LSTMAutoencoder(seq_len=hp['seq_len'], n_features=hp['n_features'],
                                embedding_dim=hp['embedding_dim'], dropout=hp.get('dropout', 0.2))
    else:
        model = LSTMAutoencoder(seq_len=10, n_features=len(features), embedding_dim=16)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'), weights_only=True))
    model.eval()

    # Collect reconstruction metrics per-ticker
    all_X_flat = []
    all_recon_flat = []
    total_sequences = 0

    if has_ticker:
        for ticker, group in df.groupby('Ticker'):
            group = group.sort_index()
            group_clean = group.copy()
            group_clean[features] = group_clean[features].ffill().bfill()

            eval_indices = np.where(group_clean['Rule_Signal'].values == 1)[0]
            if len(eval_indices) == 0:
                continue

            X_raw = group_clean[features].values
            X_scaled = scaler.transform(X_raw)
            X_eval, _ = create_sequences_for_indices(X_scaled, eval_indices, seq_len=10)

            if len(X_eval) == 0:
                continue

            X_tensor = torch.tensor(X_eval, dtype=torch.float32)
            with torch.no_grad():
                reconstructions = model(X_tensor)

            all_X_flat.append(X_tensor.numpy().flatten())
            all_recon_flat.append(reconstructions.numpy().flatten())
            total_sequences += len(X_eval)
    else:
        eval_indices = np.where(df['Rule_Signal'].values == 1)[0]
        X_raw = df[features].values
        X_scaled = scaler.transform(X_raw)
        X_eval, _ = create_sequences_for_indices(X_scaled, eval_indices, seq_len=10)
        X_tensor = torch.tensor(X_eval, dtype=torch.float32)
        with torch.no_grad():
            reconstructions = model(X_tensor)
        all_X_flat.append(X_tensor.numpy().flatten())
        all_recon_flat.append(reconstructions.numpy().flatten())
        total_sequences = len(X_eval)

    X_flat = np.concatenate(all_X_flat)
    recon_flat = np.concatenate(all_recon_flat)

    mse = mean_squared_error(X_flat, recon_flat)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(X_flat, recon_flat)
    mape = mean_absolute_percentage_error(X_flat, recon_flat)
    r2 = r2_score(X_flat, recon_flat)

    metrics_output = f"""
==================================================
AUTOENCODER RECONSTRUCTION METRICS — MULTI-STOCK
==================================================
Total Sequences Evaluated : {total_sequences}
MSE      : {mse:.4f}
RMSE     : {rmse:.4f}
MAE      : {mae:.4f}
MAPE     : {mape:.4f}
R-Squared: {r2:.4f}
==================================================
"""
    print(metrics_output)

    # Save to file
    os.makedirs("local_archive", exist_ok=True)
    with open("local_archive/research_paper_metrics.txt", "w") as f:
        f.write("RESEARCH PAPER EVALUATION REPORT (MULTI-STOCK)\n")
        f.write(accuracy_output)
        f.write("\n")
        f.write(metrics_output)
    print("Saved to local_archive/research_paper_metrics.txt")


if __name__ == "__main__":
    calculate_metrics()
