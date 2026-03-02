## Phase 3 Verification

### Must-Haves
- [x] "A deep learning model is built using PyTorch or Keras to reconstruct indicators" — VERIFIED (evidence: PyTorch LSTMAutoencoder class implemented in `src/autoencoder.py` and model saved)
- [x] "The model is ONLY trained on historical data where Rule_Signal = 1 (Buy) AND the price moved up by 5% in the next 10 days" — VERIFIED (evidence: 16 samples cleanly isolated based on 1.05x price pop logic; future data was explicitly dropped before training to avoid data leakage).

### Verdict: PASS
