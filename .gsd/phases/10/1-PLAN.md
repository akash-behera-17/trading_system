---
phase: 10
plan: 1
wave: 1
---

# Plan 10.1: ML Model Integration into React UI

## Objective
Update the React Dashboard to asynchronously fetch the Machine Learning AI verdict from the already existing Flask `/predict` endpoint. Integrate this AI signal visually into the professional layout interface.

## Context
- .gsd/ROADMAP.md
- .gsd/phases/10/RESEARCH.md
- src/app.py (Contains the `/predict` logic).
- frontend/src/pages/Dashboard.jsx

## Tasks

<task type="auto">
  <name>Dashboard AI State Integration</name>
  <files>frontend/src/pages/Dashboard.jsx</files>
  <action>
    Introduce new React states `aiData`, `aiLoading`, and `aiError` within `Dashboard.jsx`.
    Inside `useEffect`, immediately following the successful fetch of fundamental stats (`/api/stocks/dashboard`), trigger an Axios POST request to `http://localhost:5000/predict` supplying `{"ticker": ticker}`.
    Catch and map the `res.data` containing `rule_description`, `ml_anomaly`, `final_recommendation`, etc.
  </action>
  <verify>cat frontend/src/pages/Dashboard.jsx | findstr /predict</verify>
  <done>The Dashboard component has asynchronous data handlers capable of managing the heavy ML inference task cleanly.</done>
</task>

<task type="auto">
  <name>Render Neuro-Symbolic Insight UI</name>
  <files>frontend/src/pages/Dashboard.jsx</files>
  <action>
    Locate the Phase 9 "Neuro-Symbolic Callout Stub". 
    Implement conditional JSX rendering:
    - If `aiLoading`, show a pulsing generic message "Running Neuro-Symbolic AI...".
    - If `aiError`, show "AI Unavailable".
    - If `aiData` arrives, highlight `final_recommendation`. Conditionally colour it standard Gray/Green if it's a "STRONG BUY", or Red gradient if `aiData.ml_anomaly` is true. Include `reconstruction_error` and `rule_description` context tags for deep transparency (as requested structurally in the original spec).
  </action>
  <verify>cat frontend/src/pages/Dashboard.jsx | findstr final_recommendation</verify>
  <done>The Dashboard visually reflects the PyTorch inference directly to the end user.</done>
</task>

## Success Criteria
- [ ] PyTorch predictions successfully display within the React frontend.
- [ ] Asynchronous rendering prevents the ML model's compute time from blocking the fundamental data layout and charts.
- [ ] No major refactoring of the ML backend pipeline is required; effectively bridging the V1.0 logic directly into the V2.0 aesthetic milestone.
