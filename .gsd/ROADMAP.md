# ROADMAP.md

> **Current Phase**: Not started
> **Milestone**: v1.0

## Must-Haves (from SPEC)
- [ ] Rule-based engine (Mahesh Kaushik strategy)
- [ ] LSTM-Autoencoder anomaly detector
- [ ] Hybrid decision pipeline

## Phases

### Phase 1: Environment & Data Pipeline
**Status**: ✅ Complete
**Objective**: Set up the project structure, dependencies, and data pipeline to fetch historical stock data via `yfinance` and engineer all required technical indicators (DMAs, RSI, MACD, Volume).
**Requirements**: REQ-01

### Phase 2: Rule-Based Engine (Expert System)
**Status**: ✅ Complete
**Objective**: Implement the Mahesh Kaushik strategy (50/100/200 DMA logic + 10% constraints) to classify market zones and generate base "Potential Buy" or "Potential Sell" signals.
**Requirements**: REQ-02

### Phase 3: Trap Detection Model (LSTM-Autoencoder)
**Status**: ✅ Complete
**Objective**: Filter historical data for successful rule-based signals, design and train the Unsupervised LSTM-Autoencoder on these valid setups to learn the baseline structural integrity.
**Requirements**: REQ-03

### Phase 4: Hybrid System & Evaluation
**Status**: ⬜ Not Started
**Objective**: Combine the rule-engine and the Autoencoder. Evaluate the final hybrid system against baseline performance, generate backtesting metrics (precision, false positive reduction), and save the final deployable model.
**Requirements**: REQ-04

### Phase 5: Demo Script & Documentation
**Status**: ⬜ Not Started
**Objective**: Create `predict.py` for inference on new data, and finalize all project documentation (the final report) for the supervisor.
