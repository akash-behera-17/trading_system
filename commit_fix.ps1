Set-Location "c:\MAD\ppd1\trading_system"
git add src/app.py .gitignore
git commit -m "fix: sync LSTMAutoencoder v2.0 architecture + protect env secrets

- Updated LSTMAutoencoder in app.py to match retrained model weights:
  embedding_dim 16->32, encoder num_layers 1->2, added dropout=0.2
  forward() uses hidden_n[-1] for correct multi-layer LSTM output
- Added .env.local to .gitignore to protect Supabase API keys
- Resolves model size mismatch error after owner git pull"
Write-Host "Done."
