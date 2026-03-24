# ROADMAP.md

> **Current Phase**: Not started
> **Milestone**: v2.0

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
**Status**: ✅ Complete
**Objective**: Combine the rule-engine and the Autoencoder. Evaluate the final hybrid system against baseline performance, generate backtesting metrics (precision, false positive reduction), and save the final deployable model.
**Requirements**: REQ-04

### Phase 5: Demo Script & Documentation
**Status**: ✅ Complete
**Objective**: Create `predict.py` for inference on new data, and finalize all project documentation (the final report) for the supervisor.

---

### Phase 6: Deployment (Flask API & Streamlit UI)
**Status**: ✅ Complete
**Objective**: Deploy the trained Neuro-Symbolic Trading System using a Flask backend API for inference and a Streamlit frontend for user interaction.
**Depends on**: Phase 5

**Tasks**:
- [x] Plan 6.1: Flask Backend API
- [x] Plan 6.2: Streamlit UI Frontend

**Verification**:
- API tested locally via `/predict` endpoint.
- Streamlit UI created and integrated successfully.

---

# Milestone: v2.0 (Professional Web UI)

## Must-Haves
- [ ] Login system
- [ ] Company Search Bar
- [ ] Streamlined Company Dashboard (Charts, Indicators, Caps, High/Low, Ratios, Pros/Cons)
- [ ] Uncluttered, premium visual design

## Phases

### Phase 7: Frontend Architecture & Auth System
**Status**: ✅ Complete
**Objective**: Set up a modern frontend project (React/Vite or Next.js) with routing, state management, and basic authentication pages (Login/Signup).
**Requirements**: REQ-UI-01

### Phase 8: Home & Search Interfaces
**Status**: ✅ Complete
**Objective**: Build a clean, professional homepage with a central search component capable of querying the stock list and directing users to specific company dashboards.
**Requirements**: REQ-UI-02

### Phase 9: Simplified Professional Company Dashboard
**Status**: ✅ Complete
**Objective**: Build the core data view for a single stock, containing charts, key indicators, market cap, high/low ratios, pros/cons, styled cleanly without clutter.
**Requirements**: REQ-UI-03

### Phase 10: Backend API Integration
**Status**: ⬜ Not Started
**Objective**: Update the existing Flask API to serve all necessary fundamental metrics, pros/cons data, and ML signals to the new frontend dashboard.
**Requirements**: REQ-UI-04
