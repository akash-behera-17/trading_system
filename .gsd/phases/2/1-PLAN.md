---
phase: 2
plan: 1
wave: 1
depends_on: []
files_modified:
  - src/rule_engine.py
autonomous: true
user_setup: []
must_haves:
  truths:
    - "Mahesh Kaushik strategy is encoded securely as a Python function"
    - "Signals (Buy/Sell/Wait) are generated without future data leakage"
  artifacts:
    - "src/rule_engine.py"
---

# Plan 2.1: Mahesh Kaushik Strategy Implementation

<objective>
Implement the rule-based expert system based on the Mahesh Kaushik strategy. This engine processes the calculated technical indicators and classifies the market into Bullish, Bearish, or Unconfirmed zones, outputting a base signal (Potential Buy / Potential Sell / Wait).
Purpose: To establish the deterministic symbolic logic that acts as the initial trigger for the system.
Output: `src/rule_engine.py`
</objective>

<context>
Load for context:
- .gsd/SPEC.md
- src/feature_engineering.py
</context>

<tasks>

<task type="auto">
  <name>Build the Rule Engine</name>
  <files>src/rule_engine.py</files>
  <action>
    Create a script `src/rule_engine.py` with a function `apply_strategy(df)`.
    Load `data/processed_stock_data.csv`.
    Implement the Mahesh Kaushik Strategy Rules:
    - **Bull Zone (Potential Buy)**: Close > 50 DMA > 100 DMA > 200 DMA AND (Close <= 200 DMA * 1.10).
    - **Bear Zone (Potential Sell)**: Close < 50 DMA < 100 DMA < 200 DMA AND (Close >= 200 DMA * 0.90).
    - **Unconfirmed (Wait)**: All other conditions.
    
    Add a new column `Rule_Signal` where:
    1 = Potential Buy
    -1 = Potential Sell
    0 = Wait
    
    Save the updated dataframe to `data/rule_signals.csv`.
    AVOID predicting the future (do not shift to next day close here). Only use current day indicators.
  </action>
  <verify>python src/rule_engine.py</verify>
  <done>Script runs without errors and produces data/rule_signals.csv with the new Rule_Signal column.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] `data/rule_signals.csv` exists and contains the `Rule_Signal` column containing values 1, 0, or -1.
</verification>

<success_criteria>
- [ ] All tasks verified
- [ ] Must-haves confirmed
</success_criteria>
