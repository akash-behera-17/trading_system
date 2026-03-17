---
phase: 5
plan: 1
wave: 1
depends_on: []
files_modified:
  - predict.py
  - REPORT.md
autonomous: true
user_setup: []
must_haves:
  truths:
    - "A predict.py script exists that can take a live ticker and output the hybrid signal"
    - "A final REPORT.md is generated for the supervisor, explaining the Neuro-Symbolic approach"
  artifacts:
    - "predict.py"
    - "REPORT.md"
---

# Plan 5.1: Demo Script & Documentation

<objective>
Develop a live inference script (`predict.py`) that fetches recent data and outputs the current Hybrid Signal. Furthermore, generate the final `REPORT.md` document containing the abstract, architecture, and results to present to the supervisor.
Purpose: To make the system deployable/usable and fulfill the academic reporting requirements.
Output: `predict.py` and `REPORT.md`.
</objective>

<context>
Load for context:
- .gsd/SPEC.md
- src/fetch_data.py
- src/feature_engineering.py
- src/rule_engine.py
- src/hybrid_evaluation.py
</context>

<tasks>

<task type="auto">
  <name>Build Live Inference Script</name>
  <files>predict.py</files>
  <action>
    Create `predict.py` in the root directory.
    This script should:
    1. Accept a stock ticker (e.g., RELIANCE.NS) and fetch the last 300 days of data using `yfinance`.
    2. Calculate DMA 50/100/200, RSI, MACD, and Volume Change % on this data.
    3. Apply the Mahesh Kaushik Strategy on the *latest* day's data to get the Rule_Signal.
    4. If Rule_Signal == 1, load the PyTorch autoencoder and scaler from `models/`, evaluate the current features, and determine if it's a valid Hybrid Buy or a Bull Trap (using a hardcoded threshold from Phase 4, e.g., 4.6290).
    5. Print the final recommendation: STRONG BUY, AVOID (BULL TRAP), SELL, or WAIT.
  </action>
  <verify>python predict.py</verify>
  <done>Script successfully prints a live trading recommendation based on the hybrid model.</done>
</task>

<task type="auto">
  <name>Draft Final Report Documentation</name>
  <files>REPORT.md</files>
  <action>
    Create `REPORT.md` in the root directory.
    Write the 18-point documentation structure requested by the user initially.
    Crucially, in the "Introduction" and "Model Selection" sections, emphasize the novel "Neuro-Symbolic AI" approach: utilizing the Mahesh Kaushik deterministic rules for signal generation and an Unsupervised LSTM-Autoencoder strictly for Bull-Trap detection.
    Include the metrics achieved in Phase 4 (e.g., ~30% false positive reduction).
  </action>
  <verify>test -f REPORT.md</verify>
  <done>REPORT.md contains the final academic project documentation tailored for the supervisor.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] `predict.py` logic runs without errors and produces a recommendation.
- [ ] `REPORT.md` is fully drafted.
</verification>

<success_criteria>
- [ ] All tasks verified
- [ ] Must-haves confirmed
</success_criteria>
