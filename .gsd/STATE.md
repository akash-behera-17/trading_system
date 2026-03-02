# STATE.md

> **Current Phase**: Not Started
> **Goal**: Complete project initialization and move to Phase 1.

## Memory & Context
- **Project Structure**: Hybrid Neuro-Symbolic Trading System
- **Key Deviation from Standard**: Avoid standard supervised ML (SVM/XGBoost directly on price). Use expert rules + Unsupervised Anomaly Detection.

## Critical Constraints
- Only train the Autoencoder on successful historical setups.
- Do not predict price; validate the structural integrity of signals.

## Next Steps
- Run `/plan 1` to create the execution plan for Phase 1.
