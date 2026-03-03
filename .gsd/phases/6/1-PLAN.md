---
phase: 6
plan: 1
wave: 1
---

# Plan 6.1: Flask Backend API

## Objective
Develop a Flask REST API that loads the pre-trained Neuro-Symbolic Trading System model and exposes an endpoint for real-time or batched stock direction inference.

## Context
- .gsd/SPEC.md
- src/predict.py
- src/trap_detection.py

## Tasks

<task type="auto">
  <name>Develop Flask API Engine</name>
  <files>
    - src/app.py
    - requirements.txt
  </files>
  <action>
    - Add `flask` and `flask-cors` to `requirements.txt`.
    - Create `src/app.py` serving as the Flask backend.
    - Implement a `/predict` POST endpoint which accepts JSON data (e.g., `ticker`, `start_date`, `end_date`).
    - Use the existing logic from `predict.py` to fetch data, compute indicators, and return the combined rule-engine and Autoencoder signal.
    - Ensure CORS is handled so the Streamlit frontend can communicate with it.
  </action>
  <verify>flask --app src.app run --port 5000 & curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d '{"ticker":"AAPL", "period":"1y"}'</verify>
  <done>Flask server starts successfully and returns a valid JSON response with the prediction signals.</done>
</task>

## Success Criteria
- [ ] Requirements updated with Flask dependencies.
- [ ] `/predict` endpoint successfully returns the inference results matching the output structure of `predict.py`.
