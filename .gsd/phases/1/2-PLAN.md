---
phase: 1
plan: 2
wave: 2
depends_on: [1]
files_modified:
  - src/feature_engineering.py
autonomous: true
user_setup: []
must_haves:
  truths:
    - "Technical indicators are calculated accurately for the rule engine"
  artifacts:
    - "src/feature_engineering.py"
---

# Plan 1.2: Feature Engineering

<objective>
Calculate essential technical indicators (50/100/200 DMA, RSI, MACD, Volume Change %) needed for the rule-based engine and the LSTM-Autoencoder.
Purpose: To transform raw price data into meaningful structural market indicators.
Output: `src/feature_engineering.py`
</objective>

<context>
Load for context:
- .gsd/SPEC.md
- src/fetch_data.py
</context>

<tasks>

<task type="auto">
  <name>Implement technical indicators</name>
  <files>src/feature_engineering.py</files>
  <action>
    Load `data/raw_stock_data.csv`.
    Calculate `DMA_50`, `DMA_100`, `DMA_200` using rolling mean on Close.
    Calculate `RSI_14` using the `ta` library.
    Calculate `MACD` and `MACD_signal` using `ta.trend.MACD`.
    Calculate `Volume_Change_Pct` (percentage change of Volume).
    Drop rows with NaNs (created by the 200-day rolling window).
    Save output to `data/processed_stock_data.csv`.
    AVOID creating classification targets (1/0) because we are doing anomaly detection.
  </action>
  <verify>python src/feature_engineering.py</verify>
  <done>Script runs without errors and produces data/processed_stock_data.csv with all indicator columns.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] `data/processed_stock_data.csv` contains columns for 50, 100, 200 DMAs, RSI, and MACD.
- [ ] NaNs are successfully removed.
</verification>

<success_criteria>
- [ ] All tasks verified
- [ ] Must-haves confirmed
</success_criteria>
