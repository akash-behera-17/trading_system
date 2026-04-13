"""
XGBoost Supervised Classifier for the Neuro-Symbolic Trading System.
Trained on labeled success/failure data to predict the probability
of a profitable outcome for each buy signal.

This provides a SUPERVISED complement to the unsupervised LSTM-Autoencoder,
dramatically improving signal quality.
"""

import pandas as pd
import numpy as np
import os
import pickle
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, accuracy_score


# Features used by XGBoost (broader than autoencoder — includes momentum)
XGB_FEATURES = [
    'RSI_14', 'MACD', 'MACD_signal', 'Volume_Change_Pct',
    'Bollinger_PctB', 'Distance_to_52W_High', 'Distance_to_52W_Low',
    'Returns_5d', 'Returns_10d', 'Returns_20d', 'Volume_Ratio',
    'MACD_hist', 'ATR_14'
]


def train_xgboost(input_path: str = "data/rule_signals.csv",
                   model_dir: str = "models/") -> None:
    """
    Trains an XGBoost binary classifier on labeled Rule_Signal == 1 instances.
    Label: 1 = successful trade (5% gain, <3% drawdown in 10 days), 0 = failure.
    """
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    print("Loading data for XGBoost training...")
    df = pd.read_csv(input_path, index_col=0, parse_dates=True)

    if 'Ticker' not in df.columns:
        print("Error: 'Ticker' column not found.")
        return

    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Check for required features
    missing = [f for f in XGB_FEATURES if f not in df.columns]
    if missing:
        print(f"Error: Missing features: {missing}")
        print("Run the updated feature_engineering.py first.")
        return

    # --- Create Labels Per Ticker ---
    print("Creating success labels per ticker...")
    labeled_frames = []
    for ticker, group in df.groupby('Ticker'):
        group = group.sort_index().copy()
        group['Max_Next_10_Days'] = group['Close'].rolling(window=10).max().shift(-10)
        group['Min_Next_10_Days'] = group['Close'].rolling(window=10).min().shift(-10)

        group['Success'] = (
            (group['Max_Next_10_Days'] >= group['Close'] * 1.05) &
            (group['Min_Next_10_Days'] > group['Close'] * 0.97)
        ).astype(int)

        labeled_frames.append(group)

    df = pd.concat(labeled_frames)

    # Filter only buy signals for training
    buy_df = df[df['Rule_Signal'] == 1].copy()
    buy_df = buy_df.dropna(subset=XGB_FEATURES + ['Success'])

    X = buy_df[XGB_FEATURES].values
    y = buy_df['Success'].values

    print(f"\nTraining set: {len(X)} samples")
    print(f"  Positive (Success=1): {y.sum()} ({y.mean()*100:.1f}%)")
    print(f"  Negative (Success=0): {(1-y).sum()} ({(1-y).mean()*100:.1f}%)")

    # --- Train with TimeSeriesSplit for proper evaluation ---
    tscv = TimeSeriesSplit(n_splits=5)

    # Calculate scale_pos_weight for imbalanced data
    pos_count = y.sum()
    neg_count = len(y) - pos_count
    scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1

    print(f"  Scale Pos Weight: {scale_pos_weight:.2f}")

    # Optimized XGBoost hyperparameters
    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        reg_alpha=0.1,         # L1 regularization
        reg_lambda=1.0,        # L2 regularization
        min_child_weight=5,
        gamma=0.1,
        eval_metric='logloss',
        random_state=42
    )

    # Cross-validation scores
    cv_scores = []
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        val_pred = model.predict(X_val)
        acc = accuracy_score(y_val, val_pred)
        cv_scores.append(acc)

    print(f"\nCross-Validation Accuracy: {np.mean(cv_scores)*100:.2f}% (+/- {np.std(cv_scores)*100:.2f}%)")

    # Final training on full dataset
    print("\nTraining final model on full dataset...")
    model.fit(X, y, verbose=False)

    # Feature importance
    importances = model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    print("\nFeature Importance (Top 5):")
    for i in range(min(5, len(XGB_FEATURES))):
        idx = sorted_idx[i]
        print(f"  {XGB_FEATURES[idx]}: {importances[idx]:.4f}")

    # Save model
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "xgboost_classifier.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    # Save feature list for inference
    with open(os.path.join(model_dir, "xgb_features.pkl"), "wb") as f:
        pickle.dump(XGB_FEATURES, f)

    print(f"\nSaved XGBoost model to {model_path}")

    # Final report
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]
    print(f"\nFinal Training Report:")
    print(classification_report(y, y_pred, target_names=['Failure', 'Success']))
    print(f"Mean predicted probability for successes: {y_prob[y==1].mean():.3f}")
    print(f"Mean predicted probability for failures:  {y_prob[y==0].mean():.3f}")


if __name__ == "__main__":
    train_xgboost()
