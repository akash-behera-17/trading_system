# STATE.md

> **Current Phase**: Not started
> **Goal**: Build a professional web application with an aesthetic comparable to screener.in, featuring user authentication, advanced search, and comprehensive uncluttered stock views.

## Current Position
- **Milestone**: v2.0
- **Phase**: 7
- **Task**: Planning complete
- **Status**: Ready for execution
## Last Session Summary
Phase 6 executed successfully. Created `src/app.py` for the Flask REST API exposing model inference, and `ui/dashboard.py` for the Streamlit web dashboard. Integrated the two systems successfully for real-time inference.

## Memory & Context
- **Project Structure**: Hybrid Neuro-Symbolic Trading System
- **Key Deviation from Standard**: Avoid standard supervised ML (SVM/XGBoost directly on price). Use expert rules + Unsupervised Anomaly Detection.

## Critical Constraints
- Only train the Autoencoder on successful historical setups.
- Do not predict price; validate the structural integrity of signals.

## Next Steps
1. Project execution is complete. You can view the UI by running `streamlit run ui/dashboard.py` (ensure `flask run` is active first) or run `/verify 6` to finalize.
