# Phase 9 Research: Simplified Professional Company Dashboard

## 1. Discovery Level
Level 2 — Standard Research
We are deciding how to build a professional, uncluttered dashboard representing a stock. The prompt emphasizes: "Interactive price charts, INDICATORS, CURENT MARKET CAP HIGH LOE RATIOS, PROS AND CONS THATS ALL DONT MAKE IT CLADED . USE AS YOUR PREFERENCE".

## 2. Requirements & Constraints
- The UI must resemble the utility and aesthetic of screener.in but simplified to specific data points.
- Must include:
  - Interactive price charts (Requires a charting library like Recharts).
  - Indicators (DMA, RSI, MACD which are already in our backend).
  - Current Market Cap, 52-Week High/Low, Ratios (P/E, P/B expected).
  - Pros and Cons (Since we don't have fundamental NLP analysis, we can heuristically generate pros/cons based on technical indicators, or hardcode/mock slightly for the MVP, but heuristic is better: e.g., "Pro: Trading above 200 DMA", "Con: RSI indicates overbought").
- constraint: "DONT MAKE IT CLADED" (Don't make it cluttered).

## 3. Technology & Architecture Choice

### 3.1 Backend: Enriched Dashboard API
**Decision**: We must expand the existing Flask API to provide more fundamental data alongside the ML prediction. We can create a new route `/api/stocks/<ticker>/dashboard` or leverage `yfinance` to pull `info` alongside the history.
*Why*: `yfinance.Ticker(ticker).info` returns exactly what we need for the UI: Market Cap, 52 Week High/Low, Trailing P/E, Price to Book, etc. We will combine this with our existing technical analysis (DMA, RSI) to generate the "Pros and Cons" array programmatically.

### 3.2 Frontend: Dashboard Component Structure
**Decision**: Use `Recharts` for the interactive price chart (cleanest API for React). We will need to return the last 6 months of historical Close prices from the API to populate the chart.
*Why*: Recharts works seamlessly with React and Tailwind CSS. The dashboard will have:
1. Header: Company Name, Ticker, Current Price, Day Change.
2. Top Row Cards: Market Cap, High/Low, P/E Ratio, P/B Ratio.
3. Main Body Split: 
   - Left: Recharts interactive line chart.
   - Right: "Pros & Cons" bullet lists (green/red styled).
4. Bottom: The Neuro-Symbolic AI Verdict (from our existing `/predict` logic).

## 4. Phase 9 Deliverables Architecture

### Backend Updates (Flask)
- Update `src/app.py` or `src/routes/stock_routes.py` to add a `/api/stocks/<ticker>/dashboard` endpoint.
- Fetch `yfinance` history (for charting) and `info` (for fundamentals).
- Generate `pros` and `cons` string lists based on technicals (e.g., RSI > 70 = "Overbought", Close > DMA200 = "Long term uptrend").

### Frontend Updates (React)
- Create `src/pages/Dashboard.jsx`.
- Install `recharts` package.
- Fetch data from `/api/stocks/<ticker>/dashboard` on mount using the `ticker` query param.
- Layout the grid cleanly using Tailwind CSS to match the "professional and uncluttered" requirement.
