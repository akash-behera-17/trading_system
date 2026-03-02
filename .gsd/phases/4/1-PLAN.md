---
phase: 4
plan: 1
wave: 1
depends_on: []
files_modified:
  - src/hybrid_evaluation.py
autonomous: true
user_setup: []
must_haves:
  truths:
    - "Autoencoder anomalies are used to veto weak Rule_Signal == 1 setups"
    - "A final merged signal (Hybrid_Signal) is generated and backtested against historical baseline"
  artifacts:
    - "src/hybrid_evaluation.py"
    - "data/hybrid_results.csv"
---

# Plan 4.1: Hybrid System & Evaluation

<objective>
Combine the rule-based engine and the LSTM-Autoencoder anomaly detector into a single decision pipeline. Evaluate the performance by demonstrating how the Autoencoder successfully filters out "Bull Traps" compared to the baseline rule-engine.
Purpose: To prove to the supervisor that the Neuro-Symbolic Hybrid architecture quantitatively improves precision and stability.
Output: `src/hybrid_evaluation.py` and `data/hybrid_results.csv`.
</objective>

<context>
Load for context:
- .gsd/SPEC.md
- src/autoencoder.py
- src/rule_engine.py
</context>

<tasks>

<task type="auto">
  <name>Build the Hybrid Pipeline and Evaluation Metrics</name>
  <files>src/hybrid_evaluation.py</files>
  <action>
    Create a script `src/hybrid_evaluation.py`.
    Load `data/rule_signals.csv`.
    Load `models/lstm_autoencoder.pt` and `models/scaler.pkl`.
    
    Processing Steps:
    1. Filter the dataset for all instances where `Rule_Signal == 1` (ALL potential buys).
    2. Extract the features: `['DMA_50', 'DMA_100', 'DMA_200', 'RSI_14', 'MACD', 'MACD_signal', 'Volume_Change_Pct']`.
    3. Scale these features using the loaded scaler.
    4. Run them through the PyTorch LSTM-Autoencoder.
    5. Calculate the Mean Squared Error (Reconstruction Error) for each sample.
    6. Define an anomaly threshold (e.g., the 75th percentile of errors from the training set, or strictly `error > 0.5`). Let's calculate the threshold dynamically as the `mean + 1*std_dev` of the errors of all signals, or simply pick the top 30% of errors as "Traps".
    
    Decision Logic:
    - If `Rule_Signal == 1` AND `Reconstruction Error < Threshold` -> `Hybrid_Signal = 1` (Strong Buy)
    - If `Rule_Signal == 1` AND `Reconstruction Error >= Threshold` -> `Hybrid_Signal = 0` (Vetoed / Bull Trap)
    - For all other rows, `Hybrid_Signal = Rule_Signal`
    
    Metrics to Print to Console:
    - Total Rule-Based Buys
    - Total Hybrid Buys (After Filter)
    - Total Bull Traps Avoided
    
    Save the final dataframe with `Hybrid_Signal` and `Reconstruction_Error` to `data/hybrid_results.csv`.
  </action>
  <verify>python src/hybrid_evaluation.py</verify>
  <done>Script successfully merges both systems, calculates backtesting filter metrics, and saves hybrid_results.csv.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] `data/hybrid_results.csv` exists and contains the `Hybrid_Signal` column.
- [ ] Print statements confirm the number of traps avoided.
</verification>

<success_criteria>
- [ ] All tasks verified
- [ ] Must-haves confirmed
</success_criteria>
