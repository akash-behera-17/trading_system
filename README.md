# Hybrid Neuro-Symbolic Trading System

> A production-grade stock market direction prediction system combining rule-based expert logic with deep anomaly detection.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

This system uses a **Neuro-Symbolic** architecture — combining the explicit knowledge of trading experts (*Symbolic Logic*) with the pattern recognition capabilities of deep learning (*Neural Networks*) — to generate actionable stock trading signals while filtering out false breakouts ("Bull Traps").

Instead of asking a neural network to predict future prices (a notoriously noisy problem), the model is tasked with **validating the structural integrity** of the present technical indicators whenever the rule engine fires a "Buy" signal.

### Key Results

| Metric | Value |
|---|---|
| **False Positive Reduction** | ~30.36% |
| **Bull Traps Avoided** | 17 out of 56 signals |
| **Hybrid Approved Buys** | 39 verified entries |
| **Features Used** | 13 (v2.1) |
| **Sequence Length** | 10-day lookback |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   RAW STOCK DATA (yfinance)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FEATURE ENGINEERING (13 Indicators)            │
│  DMAs (20/50/100/200) · RSI · MACD · Bollinger Bands       │
│  Volume Change · 52-Week High/Low Distance                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            RULE-BASED ENGINE (Confluence Strategy)          │
│  Multi-factor entry: MA hierarchy + RSI + MACD + Bollinger │
├──────────┬───────────────────────────────────┬──────────────┤
│  SELL    │         POTENTIAL BUY              │    WAIT      │
│  ↓      │              ↓                     │    ↓         │
│ Action  │    LSTM-Autoencoder Filter          │  Action      │
│         │    (10-day sequence validation)     │              │
│         ├──────────────┬──────────────────────┤              │
│         │ Low Error    │ High Error           │              │
│         │ STRONG BUY ✅│ AVOID (Bull Trap) ⚠️ │              │
└─────────┴──────────────┴──────────────────────┴──────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | Flask, Flask-CORS, Flask-SQLAlchemy, Flask-Bcrypt, PyJWT |
| **Frontend** | React 18, Vite, Recharts, React Router |
| **ML / Deep Learning** | PyTorch (LSTM-Autoencoder), scikit-learn |
| **Data & Indicators** | yfinance, pandas, numpy, ta (Technical Analysis) |
| **Database** | SQLite (user auth) |

---

## Project Structure

```
.
├── src/
│   ├── app.py                  # Flask application & API endpoints
│   ├── autoencoder.py          # LSTM-Autoencoder model definition & training
│   ├── feature_engineering.py  # Technical indicator calculation (13 features)
│   ├── fetch_data.py           # Yahoo Finance data acquisition
│   ├── rule_engine.py          # Symbolic expert rules (Confluence Strategy)
│   ├── hybrid_evaluation.py    # Backtesting engine with sliding windows
│   ├── extensions.py           # Flask extensions (DB, Bcrypt)
│   ├── models/
│   │   └── user.py             # User model (SQLAlchemy)
│   └── routes/
│       ├── auth_routes.py      # JWT authentication endpoints
│       └── stock_routes.py     # Stock data & prediction endpoints
│
├── frontend/                   # React + Vite application
│   └── src/
│       ├── pages/
│       │   ├── Home.jsx        # Landing page with search
│       │   ├── Dashboard.jsx   # Stock analysis dashboard
│       │   └── Login.jsx       # Authentication page
│       ├── components/
│       │   ├── SearchBar.jsx   # Autocomplete stock search
│       │   ├── StockChart.jsx  # Price & indicator charts
│       │   ├── IndexChart.jsx  # Market index charts
│       │   └── ProtectedRoute.jsx
│       └── context/            # Auth state management
│
├── models/
│   ├── lstm_autoencoder.pt     # Trained PyTorch model weights
│   └── scaler.pkl              # Fitted StandardScaler
│
├── data/
│   ├── processed_stock_data.csv
│   ├── rule_signals.csv
│   └── hybrid_results.csv
│
├── predict.py                  # CLI inference script
├── requirements.txt            # Python dependencies
├── REPORT.md                   # Academic project report
│
├── er_diagram.html             # Entity-Relationship diagram
├── dfd_diagrams.html           # Data Flow diagrams
├── use_case_diagram.html       # Use Case diagram
├── sequence_diagram.html       # Sequence diagram
└── class_diagram.html          # Class diagram
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- pip

### 1. Clone & Install

```bash
git clone https://github.com/akash-behera-17/trading_system.git
cd trading_system

# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Run the Backend

```bash
python src/app.py
```

The Flask API starts on `http://localhost:5000`.

### 3. Run the Frontend

```bash
cd frontend
npm run dev
```

The React dev server starts on `http://localhost:5173`.

### 4. CLI Inference (Quick Test)

```bash
python predict.py --ticker RELIANCE.NS
```

Example output:

```
==================================================
LIVE INFERENCE: RELIANCE.NS
==================================================
Fetching recent data for RELIANCE.NS...
Latest Date : 2026-03-28
Close Price : Rs. 1275.50

Rule Engine  : POTENTIAL BUY (Bull Zone Detected)
Validating signal integrity via Deep Learning Autoencoder...
Reconstruction Error: 0.1542
ML Filter Result  : STRUCTURE VERIFIED
Recommendation    : STRONG BUY
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check & model status |
| `POST` | `/predict` | Run hybrid inference for a ticker |
| `POST` | `/api/auth/register` | User registration |
| `POST` | `/api/auth/login` | User login (returns JWT) |
| `GET` | `/api/stocks/search?q=` | Search stocks by name/ticker |
| `GET` | `/api/stocks/<ticker>/dashboard` | Full dashboard data for a stock |

### Example: Predict

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"ticker": "RELIANCE.NS"}'
```

---

## How It Works

### 1. Feature Engineering (13 Indicators)

The system computes 13 technical features from raw OHLCV data:

| Feature | Description |
|---|---|
| DMA 20 / 50 / 100 / 200 | Daily Moving Averages |
| RSI (14) | Relative Strength Index |
| MACD & MACD Signal | Moving Average Convergence Divergence |
| Volume Change % | Day-over-day volume change |
| Bollinger Upper / Middle / Lower | Bollinger Bands (20, 2σ) |
| Distance to 52W High / Low | Proximity to yearly extremes |

### 2. Rule Engine (Confluence Strategy)

A multi-factor deterministic filter inspired by the Mahesh Kaushik strategy, enhanced with additional confluence checks:

**Bull Zone** — All must hold:
- `Close > DMA_50 > DMA_200` (trend alignment)
- `Close > DMA_20` (short-term momentum)
- `40 < RSI < 70` (not overbought)
- `MACD > MACD_signal` (bullish crossover)
- `Close ≤ Bollinger Upper` (not overextended)
- `Close ≤ DMA_200 × 1.10` (within 10% of long-term mean)

### 3. LSTM-Autoencoder (Trap Detector)

An unsupervised anomaly detector trained exclusively on historically proven breakouts:

- **Input**: 10-day sequences × 13 features
- **Architecture**: `Encoder(LSTM) → Latent Space → Decoder(LSTM)`
- **Anomaly Threshold**: 70th percentile of reconstruction error (MSE = 0.2928)
- If a "Buy" signal's reconstruction error exceeds the threshold, it is classified as a **Bull Trap** and vetoed.

---

## Version History

| Version | Milestone | Key Changes |
|---|---|---|
| **v1.0** | Core ML System | Phases 1–5: Data pipeline, rule engine, LSTM-Autoencoder, backtesting, CLI inference |
| **v2.0** | Professional Web UI | Phases 6–10: Flask API, React dashboard, auth system, stock search, interactive charts |
| **v2.1** | Opus 4.6 Confluence | Phase 11: Expanded to 13 features, 10-day sequences, multi-factor confluence rules, system-wide pipeline sync |

---

## UML Documentation

The project includes comprehensive UML diagrams (viewable in browser):

- **ER Diagram** — `er_diagram.html`
- **Data Flow Diagrams** — `dfd_diagrams.html`
- **Use Case Diagram** — `use_case_diagram.html`
- **Sequence Diagram** — `sequence_diagram.html`
- **Class Diagram** — `class_diagram.html`

---

## Limitations

- Relies on price-based technical indicators; cannot predict exogenous shocks (e.g., geopolitical events, regulatory changes).
- The autoencoder uses a 10-day lookback window; future iterations could explore attention-based architectures for variable-length sequences.
- Currently supports NSE-listed stocks via Yahoo Finance.

## Future Enhancements

- NLP sentiment analysis on news headlines as a secondary veto layer.
- Expansion to full Nifty 50 with market-wide movers dashboard.
- Dynamic stop-loss and take-profit generation alongside "STRONG BUY" signals.
- TradingView-style interactive charting in the dashboard.

---

## References

- Mahesh Kaushik Trading Strategies (Moving Average concepts)
- PyTorch Documentation: Sequence Models and Autoencoders
- *Advances in Financial Machine Learning* — Marcos Lopez de Prado

---

## Contributors

See [CONTRIBUTORS.md](CONTRIBUTORS.md)

## License

This project is for academic and educational purposes.
