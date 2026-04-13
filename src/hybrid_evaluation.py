"""
Hybrid Scoring Engine v2.0 for the Neuro-Symbolic Trading System.

Instead of a crude binary filter (old approach: 88% rejection rate),
this engine computes a WEIGHTED HYBRID SCORE combining:
  - XGBoost supervised probability (50%)
  - Autoencoder anomaly confidence (30%)
  - Technical indicator confirmation (20%)

Inspired by Algorithm 2: Hybrid Strategy Execution Engine
"""

import pandas as pd
import numpy as np
import os
import pickle
import torch
import torch.nn as nn
from autoencoder import LSTMAutoencoder, AE_FEATURES


def create_sequences_for_indices(data, indices, seq_len):
    xs = []
    valid_idxs = []
    for idx in indices:
        if idx >= seq_len - 1:
            xs.append(data[idx - seq_len + 1 : idx + 1])
            valid_idxs.append(idx)
    return np.array(xs) if xs else np.array([]).reshape(0, seq_len, data.shape[1]), valid_idxs


def _compute_technical_score(row: pd.Series) -> float:
    """
    Computes a technical confirmation score [0.0 - 1.0] based on
    how many indicator conditions are favorable.
    """
    score = 0.0
    max_score = 5.0

    # 1. RSI in sweet spot (40-65 is ideal buy zone)
    rsi = row.get('RSI_14', 50)
    if 40 <= rsi <= 65:
        score += 1.0
    elif 35 <= rsi < 40 or 65 < rsi <= 70:
        score += 0.5

    # 2. MACD bullish (MACD > Signal and histogram positive/rising)
    macd = row.get('MACD', 0)
    signal = row.get('MACD_signal', 0)
    macd_hist = row.get('MACD_hist', 0)
    if macd > signal:
        score += 0.5
        if macd_hist > 0:
            score += 0.5  # Extra for positive histogram

    # 3. Price position within Bollinger Bands (middle zone is safer)
    pctb = row.get('Bollinger_PctB', 0.5)
    if 0.3 <= pctb <= 0.7:
        score += 1.0
    elif 0.2 <= pctb < 0.3 or 0.7 < pctb <= 0.8:
        score += 0.5

    # 4. Volume surge (above average = conviction)
    vol_ratio = row.get('Volume_Ratio', 1.0)
    if vol_ratio >= 1.5:
        score += 1.0
    elif vol_ratio >= 1.2:
        score += 0.5

    # 5. EMA regime confirmation (Price > EMA50 > EMA200)
    close = row.get('Close', 0)
    ema50 = row.get('EMA_50', 0)
    ema200 = row.get('EMA_200', 0)
    if close > ema50 > ema200:
        score += 1.0

    return min(score / max_score, 1.0)


def evaluate_hybrid_system(signals_path: str = "data/rule_signals.csv",
                           ae_model_path: str = "models/lstm_autoencoder.pt",
                           scaler_path: str = "models/scaler.pkl",
                           xgb_model_path: str = "models/xgboost_classifier.pkl",
                           xgb_features_path: str = "models/xgb_features.pkl",
                           ae_hp_path: str = "models/ae_hyperparams.pkl",
                           output_path: str = "data/hybrid_results.csv",
                           hybrid_threshold: float = 0.45) -> None:
    """
    v2.0 Hybrid Scoring Engine.
    Combines XGBoost (50%) + Autoencoder (30%) + Technical (20%).
    """
    for p, name in [(signals_path, "signals"), (ae_model_path, "autoencoder"),
                    (scaler_path, "scaler"), (xgb_model_path, "xgboost"),
                    (xgb_features_path, "xgb features")]:
        if not os.path.exists(p):
            print(f"Error: {name} not found at {p}")
            return

    print("Loading all model artifacts...")
    df = pd.read_csv(signals_path, index_col=0, parse_dates=True)

    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    with open(xgb_model_path, "rb") as f:
        xgb_model = pickle.load(f)
    with open(xgb_features_path, "rb") as f:
        xgb_features = pickle.load(f)

    # Load autoencoder with saved hyperparams
    if os.path.exists(ae_hp_path):
        with open(ae_hp_path, "rb") as f:
            hp = pickle.load(f)
        ae_model = LSTMAutoencoder(
            seq_len=hp['seq_len'], n_features=hp['n_features'],
            embedding_dim=hp['embedding_dim'], dropout=hp.get('dropout', 0.2)
        )
    else:
        ae_model = LSTMAutoencoder(seq_len=10, n_features=len(AE_FEATURES), embedding_dim=32, dropout=0.2)

    ae_model.load_state_dict(torch.load(ae_model_path, map_location='cpu', weights_only=True))
    ae_model.eval()

    # Initialize output columns
    df['XGB_Score'] = np.nan
    df['AE_Score'] = np.nan
    df['Tech_Score'] = np.nan
    df['Hybrid_Score'] = np.nan
    df['Hybrid_Signal'] = df['Rule_Signal'].copy()
    df['Reconstruction_Error'] = np.nan

    total_rule_buys = 0
    total_hybrid_buys = 0

    print(f"Running Hybrid Scoring Engine v2.0 on {df['Ticker'].nunique()} tickers...")
    print(f"  Weights: XGBoost=0.50, Autoencoder=0.30, Technical=0.20")
    print(f"  Threshold: {hybrid_threshold}")

    for ticker, group in df.groupby('Ticker'):
        group = group.sort_index()
        group_clean = group.copy()
        group_clean.replace([np.inf, -np.inf], np.nan, inplace=True)
        group_clean[AE_FEATURES] = group_clean[AE_FEATURES].ffill().bfill()

        buy_mask = group_clean['Rule_Signal'] == 1
        buy_indices = np.where(buy_mask.values)[0]

        if len(buy_indices) == 0:
            continue

        total_rule_buys += len(buy_indices)
        original_indices = group_clean.index

        # --- 1. XGBoost Score ---
        xgb_input_cols = [c for c in xgb_features if c in group_clean.columns]
        buy_rows = group_clean.iloc[buy_indices]
        xgb_data = buy_rows[xgb_input_cols].fillna(0).values

        try:
            xgb_probs = xgb_model.predict_proba(xgb_data)[:, 1]
        except Exception:
            xgb_probs = np.full(len(buy_indices), 0.5)

        # --- 2. Autoencoder Score ---
        X_raw = group_clean[AE_FEATURES].values
        X_scaled = scaler.transform(X_raw)
        X_eval, valid_ae_idxs = create_sequences_for_indices(X_scaled, buy_indices, seq_len=10)

        ae_scores_map = {}
        re_map = {}
        if len(X_eval) > 0:
            X_tensor = torch.tensor(X_eval, dtype=torch.float32)
            criterion = nn.MSELoss(reduction='none')

            with torch.no_grad():
                recons = ae_model(X_tensor)
                errors = criterion(recons, X_tensor).mean(dim=(1, 2)).numpy()

            # Normalize errors to [0, 1] score (lower error = higher score)
            if errors.max() > errors.min():
                normalized = 1.0 - (errors - errors.min()) / (errors.max() - errors.min())
            else:
                normalized = np.ones_like(errors) * 0.5

            for i, local_idx in enumerate(valid_ae_idxs):
                ae_scores_map[local_idx] = normalized[i]
                re_map[local_idx] = errors[i]

        # --- 3. Technical Score + Final Hybrid Score ---
        for i, local_idx in enumerate(buy_indices):
            global_idx = original_indices[local_idx]
            row = group_clean.iloc[local_idx]

            xgb_s = xgb_probs[i]
            ae_s = ae_scores_map.get(local_idx, 0.5)  # default 0.5 if no sequence
            tech_s = _compute_technical_score(row)

            # Weighted combination
            hybrid_score = 0.50 * xgb_s + 0.30 * ae_s + 0.20 * tech_s

            df.loc[global_idx, 'XGB_Score'] = xgb_s
            df.loc[global_idx, 'AE_Score'] = ae_s
            df.loc[global_idx, 'Tech_Score'] = tech_s
            df.loc[global_idx, 'Hybrid_Score'] = hybrid_score
            df.loc[global_idx, 'Reconstruction_Error'] = re_map.get(local_idx, np.nan)

            if hybrid_score >= hybrid_threshold:
                df.loc[global_idx, 'Hybrid_Signal'] = 1
                total_hybrid_buys += 1
            else:
                df.loc[global_idx, 'Hybrid_Signal'] = 0

    noise_reduction = ((total_rule_buys - total_hybrid_buys) / total_rule_buys * 100) if total_rule_buys > 0 else 0

    print("\n" + "="*60)
    print("HYBRID SCORING ENGINE v2.0 RESULTS")
    print("="*60)
    print(f"Tickers Evaluated                    : {df['Ticker'].nunique()}")
    print(f"Total Rule-Based Buys                : {total_rule_buys}")
    print(f"Total Hybrid v2 Buys (Score >= {hybrid_threshold}) : {total_hybrid_buys}")
    print(f"Signals Filtered Out                 : {total_rule_buys - total_hybrid_buys}")
    print(f"Noise Reduction Rate                 : {noise_reduction:.2f}%")

    # Score distribution
    scored = df[df['Hybrid_Score'].notna()]
    if len(scored) > 0:
        print(f"\nHybrid Score Distribution:")
        print(f"  Mean  : {scored['Hybrid_Score'].mean():.3f}")
        print(f"  Median: {scored['Hybrid_Score'].median():.3f}")
        print(f"  Min   : {scored['Hybrid_Score'].min():.3f}")
        print(f"  Max   : {scored['Hybrid_Score'].max():.3f}")
    print("="*60 + "\n")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path)
    print(f"Saved hybrid v2 results to {output_path}")


if __name__ == "__main__":
    evaluate_hybrid_system()
