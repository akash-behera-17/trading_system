# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision
To develop a Hybrid Neuro-Symbolic Trading System that combines a deterministic rule-based expert system (Mahesh Kaushik Strategy) for signal generation with an Unsupervised LSTM-Autoencoder to filter out false breakouts and market noise.

## Goals
1. Implement the Mahesh Kaushik Strategy as a rule-based engine (50/100/200 DMAs and 10% deviation rules).
2. Develop an Unsupervised LSTM-Autoencoder to act as an anomaly detector (Bull Trap detector) trained only on successful historical trades.
3. Build a hybrid decision system that outputs reliable and explainable Buy, Sell, or Wait signals.

## Non-Goals (Out of Scope)
- Real-time news sentiment analysis
- LSTM for sequence learning and direct price prediction
- Multi-stock portfolio system (starting with a single stock focus)
- High-frequency trading execution

## Users
Traders, analysts, and researchers looking for an explainable, noise-reduced decision-support system to guide stock market entries and exits.

## Constraints
- **Technical**: Python (3.9/3.10), yfinance, pandas, scikit-learn, PyTorch/Keras, ta
- **Methodological**: Supervised ML is avoided for prediction; unsupervised ML is strictly used for validation.
- **Data**: Single stock historical daily data (5 years) for training and evaluation.

## Success Criteria
- [ ] Rule-based engine accurately identifies Bull, Bear, and Unconfirmed zones.
- [ ] Autoencoder correctly flags "Bull Traps" (anomalous momentum) with a high reconstruction error.
- [ ] The system demonstrably improves precision compared to the pure rule-based approach.
