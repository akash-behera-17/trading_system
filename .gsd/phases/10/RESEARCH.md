# Phase 10 Research: Backend API Integration (Neuro-Symbolic ML)

## 1. Discovery Level
Level 2 — Standard Research
We are deciding how to integrate the existing machine learning inference process (the Neuro-Symbolic AI from Phase 4/5) into the professional React dashboard we built in Phase 9.

## 2. Requirements & Constraints
- The dashboard needs to display the final AI verdict ("Buy", "Sell", "Avoid (Anomaly)").
- Currently, `src/app.py` has a `/predict` POST endpoint containing all the loaded PyTorch Autoencoder models and `yfinance` fetches. 
- In Phase 9, we built `/api/stocks/dashboard` as a GET endpoint in `src/routes/stock_routes.py` which provides fundamentals and charts.

## 3. Technology & Architecture Choice

### 3.1 Backend: Merge Endpoints vs Separate Calls
**Decision**: Separate Calls.
*Why*: The `dashboard` GET endpoint is very fast because it only fetches a 6-month history and simple math. The ML inference (`/predict`) can sometimes take a moment longer if the PyTorch model needs to evaluate anomalies, and it requires POST data. 
To keep the UI snappy, the Dashboard should load the charts immediately. Then, the React component fires a separate POST request to `/predict` to get the AI verdict and overlays it onto the UI asynchronously.

*Refactoring*: We will keep `/predict` in `src/app.py` as it already exists and holds the global ML models (`autoencoder_model`, `scaler`). The React Dashboard will simply be updated to call `/predict` independently and populate the "Neuro-Symbolic Callout Stub" we created in Phase 9.

### 3.2 Frontend: React State Update
**Decision**: We will add a new `useEffect` hook in `Dashboard.jsx`.
*Why*: After the initial dashboard data loads, we'll kick off the prediction fetch. We'll add local states: `aiAnalysis` and `aiLoading`. Once `/predict` returns its JSON `{"rule_signal": x, "ml_anomaly": bool, "final_recommendation": string}`, we render it directly in the black AI gradient card.

## 4. Phase 10 Deliverables Architecture

### Backend Refinement (Flask)
- Ensure `/predict` allows CORS properly (already handled globally in `app.py`).
- Ensure it accepts standard JSON payloads format: `{"ticker": "RELIANCE.NS"}`.

### Frontend Integration (React)
- Update `frontend/src/pages/Dashboard.jsx`.
- Post to `http://localhost:5000/predict` on mount when `ticker` is present.
- Replace the "Phase 10 stub" text with dynamic, conditional tailwind rendering based on `aiAnalysis.final_recommendation`.
