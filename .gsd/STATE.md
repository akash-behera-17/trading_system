# STATE.md

> **Current Phase**: 6
> **Goal**: Deploy the trained Neuro-Symbolic Trading System via Flask API and Streamlit UI.

## Current Position
- **Phase**: 6 (Deployment)
- **Task**: Planning Phase 6
- **Status**: Not Started

## Last Session Summary
Phase 5 executed successfully. Live inference script `predict.py` built for dynamic market direction evaluation. Final extensive `REPORT.md` written. User initiated a new phase for deployment using Streamlit and a Flask API.

## Memory & Context
- **Project Structure**: Hybrid Neuro-Symbolic Trading System
- **Key Deviation from Standard**: Avoid standard supervised ML (SVM/XGBoost directly on price). Use expert rules + Unsupervised Anomaly Detection.

## Critical Constraints
- Only train the Autoencoder on successful historical setups.
- Do not predict price; validate the structural integrity of signals.

## Next Steps
1. Run `/plan 6` to create execution plans for the new deployment phase.
