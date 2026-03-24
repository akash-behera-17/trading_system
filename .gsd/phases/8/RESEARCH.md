# Phase 8 Research: Home & Search Interfaces

## 1. Discovery Level
Level 2 — Standard Research
We are deciding how to implement a clean, fast autocomplete stock search bar without relying on a massive database or external paid APIs, keeping it localized but functional.

## 2. Requirements & Constraints
- Must function identically to a professional screener.in search.
- When the user types "rel", it should show "Reliance Industries (RELIANCE.NS)", etc.
- We rely on `yfinance` in the backend. 
- Constraint: We don't have a live SQL database of all 5000+ Indian stocks. Therefore, providing a static JSON or CSV of top Nifty 500 stocks served straight to the React frontend or via a simple Flask endpoint is the most efficient, low-overhead solution.

## 3. Technology & Architecture Choice

### 3.1 Backend: Static Ticker Registry
**Decision**: A simple static dictionary/JSON inside the Flask backend OR a hardcoded list in React.
*Why*: For this MVP, a hardcoded list of major Indian stocks (Nifty 50 or top 100) is sufficient and highly performant. A Flask endpoint `/api/stocks/search?q=XYZ` can return matches from this list. *However*, we can just hardcode an array of the most popular 50 stocks directly into the React component for zero-latency autocomplete. Since the ultimate prediction relies on standard yfinance tickers, anything that is passed correctly (e.g. `RELIANCE.NS`) will work.

Let's build a dedicated `/api/stocks/search` endpoint in Flask. It's cleaner architecture and separates the data layer from the view layer.

### 3.2 Frontend: Autocomplete Component
**Decision**: We will build a custom React component using standard Tailwind styling.
*Why*: We don't need a heavy library like `react-select`. A simple relative-positioned dropdown `<ul>` below an `<input>` is easy to style into the "uncluttered premium" look required.

## 4. Phase 8 Deliverables Architecture

### Backend Updates (Flask)
- Create `src/routes/stock_routes.py`.
- Add a tiny static dictionary of popular NSE/BSE tickers.
- Add `/api/stocks/search?q={query}` endpoint returning matched tickers and company names.

### Frontend Architecture (React/Vite)
- Create `src/pages/Home.jsx`.
- Create `src/components/SearchBar.jsx`.
- The search bar sends Axios requests to `/api/stocks/search` with debounce.
- On selecting a stock, it pushes to `/dashboard?ticker=RELIANCE.NS` (which will be built in Phase 9).
