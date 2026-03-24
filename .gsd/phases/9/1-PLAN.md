---
phase: 9
plan: 1
wave: 1
---

# Plan 9.1: Backend Dashboard Endpoint

## Objective
Establish a unified backend endpoint that provides all necessary data for the simplified professional company dashboard, including basic fundamentals, 6-month historical charting data, pre-calculated technical indicators, and a programmatic list of Pros & Cons.

## Context
- .gsd/ROADMAP.md
- .gsd/phases/9/RESEARCH.md
- src/routes/stock_routes.py

## Tasks

<task type="auto">
  <name>Create Dashboard Endpoint</name>
  <files>src/routes/stock_routes.py</files>
  <action>
    Add a GET `/dashboard` route to `stock_bp`.
    It should accept a `ticker` query parameter.
    Using `yfinance` (imported internally), fetch the ticker's `info` to retrieve fundamental data: Market Cap, 52Week High, 52Week Low, Trailing P/E, and PriceToBook. Safely default to `N/A` if attributes are missing.
    Fetch 6 months of historical interval `1d` data.
    Format the historical data into a list of dictionaries `[{"date": "YYYY-MM-DD", "price": 123.45}]` for Recharts.
  </action>
  <verify>python -c "from src.app import app; print([rule.rule for rule in app.url_map.iter_rules()])" | findstr dashboard</verify>
  <done>The `/dashboard` endpoint successfully registers and parses yfinance data.</done>
</task>

<task type="auto">
  <name>Generate Heuristic Pros and Cons</name>
  <files>src/routes/stock_routes.py</files>
  <action>
    Inside the `/dashboard` route, utilize the fetched 6-month data to calculate the 50 DMA, 200 DMA, and 14-day RSI for the most recent day.
    Compare the latest Close price against these indicators to append string statements to `pros` and `cons` array lists.
    (e.g., If Close > 200 DMA: append "Trading above 200-Day Moving Average" to `pros`).
    (e.g., If RSI > 70: append "RSI indicates stock is overbought (Risk)" to `cons`).
    Return the fully aggregated JSON comprising: fundamentals, chart_data, indicators, pros, and cons.
  </action>
  <verify>python -c "import requests, time; try: print(requests.get('http://localhost:5000/api/stocks/dashboard?ticker=RELIANCE.NS').json().keys()) except: print('Waiting for server')"</verify>
  <done>The endpoint returns the complete structure containing all necessary data arrays.</done>
</task>

## Success Criteria
- [ ] Valid GET endpoint `/api/stocks/dashboard` exists.
- [ ] Returns fundamental stats, chart payload, and heuristically evaluated Pros & Cons.
- [ ] Operates efficiently, returning formatted Recharts-ready data structures.
