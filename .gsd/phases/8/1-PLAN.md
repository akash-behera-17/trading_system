---
phase: 8
plan: 1
wave: 1
---

# Plan 8.1: Backend Search API

## Objective
Establish a backend endpoint to provide a pre-defined or dynamic list of supported stocks for the frontend search autocomplete component, preventing relying on massive raw data payloads or external APIs directly from the client.

## Context
- .gsd/SPEC.md
- .gsd/ROADMAP.md
- .gsd/phases/8/RESEARCH.md
- src/app.py

## Tasks

<task type="auto">
  <name>Create Stock Routes Blueprint</name>
  <files>src/routes/stock_routes.py, src/app.py</files>
  <action>
    Create a new Flask Blueprint `stock_bp` in `src/routes/stock_routes.py`.
    Register this blueprint in `src/app.py` under `/api/stocks`.
  </action>
  <verify>python -c "from src.app import app; print([rule.rule for rule in app.url_map.iter_rules()])" | findstr /api/stocks</verify>
  <done>Flask successfully registers the new blueprint route namespace.</done>
</task>

<task type="auto">
  <name>Implement Static Search Endpoint</name>
  <files>src/routes/stock_routes.py</files>
  <action>
    Inside `stock_bp`, create a simple internal dictionary of top 10-20 popular NSE/BSE stocks (e.g., RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS) mapped to their company names.
    Create a GET `/search` route that accepts a `q` query parameter.
    Filter the internal dictionary for keys or values containing `q` (case-insensitive) and return as JSON list of objects: `[{"ticker": "RELIANCE.NS", "name": "Reliance Industries"}]`.
  </action>
  <verify>python -c "import requests, time; try: print(requests.get('http://localhost:5000/api/stocks/search?q=rel').json()) except: print('Requires server run')"</verify>
  <done>The `/search` endpoint returns a correctly filtered JSON list when queried.</done>
</task>

## Success Criteria
- [ ] Valid GET endpoint `/api/stocks/search` exists.
- [ ] Returns a filtered list of objects matching the query string.
- [ ] Operates purely from safe internal dictionaries (no heavy DB/yfinance calls needed just for autocomplete).
