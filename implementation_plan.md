# Modernizing the Neuro-Symbolic Trading Model

This document outlines proposed changes to the `rule_engine.py` and `autoencoder.py` based on the comprehensive qualitative and quantitative technical analysis reports (such as the SUNPHARMA and POWERGRID ones).

Currently, your model's logic is a bit simplistic compared to a professional citadel-style qualitative breakdown:
1. **Rule Engine:** Only uses price relative to 50, 100, and 200 DMAs.
2. **Autoencoder:** Only uses a sequence length of 1 (effectively ignoring temporal dependencies) and a limited feature set (MAs, RSI, MACD, Volume).

## User Review Required

> [!IMPORTANT]
> Some of these changes will require additional data processing in `feature_engineering.py` (e.g., calculating Bollinger Bands, 20-day SMA, 52-week highs/lows, Fib retracements) before they can be used in the rule engine or autoencoder. 
> Please review these recommendations and let me know if you want me to proceed with implementing them across the pipeline (which includes updating `feature_engineering.py` first).

## Proposed Changes

### [MODIFY] `src/rule_engine.py`

The Opus 4.6 analysis relies heavily on confluence (multiple factors aligning). We should upgrade the rule engine to incorporate these factors:

- **Add 20-Day SMA / Short-Term Momentum:** The current rules only look at 50, 100, 200 DMA. The Opus reports emphasize the 20-day SMA for short-term trend entry/exit.
- **RSI and MACD Filters:** Add oscillator constraints to the rules. A stock shouldn't get a 'Bull' signal if RSI is > 70 (overbought) or if the MACD histogram is heavily negative.
- **Bollinger Band Squeeze / Reversion:** Add a rule where price must be bouncing off the Lower/Middle Bollinger Band to validate an entry (avoiding buying at the Upper Band).
- **Proximity to 52-Week Range (Fibonacci Proxy):** Add a rule checking where the price is relative to its 52-week high and low. As seen in the analyst reports, a pullback to the 38.2% or 50% retracement of the 52-week range is prime territory for a buy.

*New Bull Condition Example:*
```python
bull_condition = (
    # Trend
    (df['Close'] > df['DMA_50']) & (df['DMA_50'] > df['DMA_200']) & 
    (df['Close'] > df['DMA_20']) & # Short term momentum
    # Oscillators
    (df['RSI_14'] > 40) & (df['RSI_14'] < 70) & # Not overbought
    (df['MACD'] > df['MACD_signal']) & # Bullish momentum
    # Value
    (df['Close'] <= df['Bollinger_Upper']) # Not overextended
)
```

---

### [MODIFY] `src/autoencoder.py`

The current LSTM Autoencoder is an LSTM in name only, as it's trained on `seq_len=1`, which means it doesn't analyze time sequences, just single data points. 

- **True Sequence Modeling:** Increase the `seq_len` parameter from 1 to 10 or 20 (e.g., a 2-week or 4-week lookback). The LSTM will now ingest arrays of `(batch, 10,  n_features)` instead of `(batch, 1, n_features)`. This allows the autoencoder to "see" chart patterns, momentum deceleration, and volume divergence over time (which the Opus report heavily emphasizes).
- **Expanded Feature Set:** Update the feature list to include the indicators that professional analysts use:
  - Add `DMA_20` (Short term trend).
  - Add `Bollinger_Upper`, `Bollinger_Lower`, `Bollinger_Mid` (Volatility/Consolidation signals).
  - Add `Distance_to_52W_High` and `Distance_to_52W_Low` to give the model a sense of Fibonacci retracement depth.
- **Better Target Definition for "Success":** Currently, success is defined as making a 5% gain in 10 days. We should also enforce that the stock doesn't crash >3% (stop loss) during those 10 days to enforce "Risk/Reward" setup quality.

## Open Questions

1. **Feature Engineering:** To implement these rule engine and autoencoder changes, I will need to update `src/feature_engineering.py` to calculate Bollinger Bands, 20 DMA, and 52-week highs/lows. Shall I proceed with those feature engine updates first?
2. **Autoencoder Sequence Length:** To use an LSTM properly, we need to restructure the data prep step to create rolling windows (e.g., lookback of 10 days) of features. Are you okay with the autoencoder processing a 10-day window instead of a single day? 

## Verification Plan

### Automated Tests
- Run `python src/feature_engineering.py` to verify new features calculate correctly.
- Run `python src/rule_engine.py` to ensure the new multi-factor rules generate plausible signal counts.
- Run `python src/autoencoder.py` to ensure the model trains successfully under the new sequence shapes without shape mismatch errors.
