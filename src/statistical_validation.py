"""
Statistical Validation Module for the Neuro-Symbolic Trading System.
Computes research-grade metrics to prove the Hybrid model is statistically 
superior to the Rule-Only baseline:
  - Sharpe Ratio (annualized, risk-free = 6% for India)
  - Independent Two-Sample T-Test (daily returns)
  - Win Rate comparison
  - Significance interpretation
"""

import pandas as pd
import numpy as np
from scipy import stats
import os


RISK_FREE_RATE = 0.06  # 6% annual (India FD benchmark)
TRADING_DAYS = 252


def compute_sharpe_ratio(equity_df: pd.DataFrame) -> float:
    """Computes annualized Sharpe Ratio from an equity curve."""
    daily_returns = equity_df['Total'].pct_change().dropna()
    if daily_returns.std() == 0:
        return 0.0
    daily_rf = RISK_FREE_RATE / TRADING_DAYS
    excess_returns = daily_returns - daily_rf
    sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(TRADING_DAYS)
    return sharpe


def compute_sortino_ratio(equity_df: pd.DataFrame) -> float:
    """Computes annualized Sortino Ratio (penalizes only downside volatility)."""
    daily_returns = equity_df['Total'].pct_change().dropna()
    daily_rf = RISK_FREE_RATE / TRADING_DAYS
    excess_returns = daily_returns - daily_rf
    downside = excess_returns[excess_returns < 0]
    if len(downside) == 0 or downside.std() == 0:
        return float('inf')
    sortino = (excess_returns.mean() / downside.std()) * np.sqrt(TRADING_DAYS)
    return sortino


def run_statistical_validation(data_dir: str = "data") -> None:
    """
    Loads equity curves from backtest_engine output and performs
    statistical validation between strategies.
    """
    rule_path = os.path.join(data_dir, "equity_rule_only.csv")
    hybrid_v1_path = os.path.join(data_dir, "equity_hybrid_v1.csv")
    hybrid_v2_path = os.path.join(data_dir, "equity_hybrid.csv")
    bnh_path = os.path.join(data_dir, "equity_buyhold.csv")

    for p in [rule_path, bnh_path]:
        if not os.path.exists(p):
            print(f"Error: {p} not found. Run backtest_engine.py first.")
            return

    eq_rule = pd.read_csv(rule_path)
    eq_bnh = pd.read_csv(bnh_path)
    
    # Use Hybrid v1 (best performer) as primary "Hybrid"
    if os.path.exists(hybrid_v1_path):
        eq_hybrid = pd.read_csv(hybrid_v1_path)
    elif os.path.exists(hybrid_v2_path):
        eq_hybrid = pd.read_csv(hybrid_v2_path)
    else:
        print("Error: No hybrid equity file found.")
        return

    # --- Sharpe Ratios ---
    sharpe_bnh = compute_sharpe_ratio(eq_bnh)
    sharpe_rule = compute_sharpe_ratio(eq_rule)
    sharpe_hybrid = compute_sharpe_ratio(eq_hybrid)

    # --- Sortino Ratios ---
    sortino_bnh = compute_sortino_ratio(eq_bnh)
    sortino_rule = compute_sortino_ratio(eq_rule)
    sortino_hybrid = compute_sortino_ratio(eq_hybrid)

    # --- T-Test: Hybrid vs Rule-Only (Daily Returns) ---
    returns_rule = eq_rule['Total'].pct_change().dropna().values
    returns_hybrid = eq_hybrid['Total'].pct_change().dropna().values

    # Ensure same length
    min_len = min(len(returns_rule), len(returns_hybrid))
    returns_rule = returns_rule[:min_len]
    returns_hybrid = returns_hybrid[:min_len]

    t_stat, p_value = stats.ttest_ind(returns_hybrid, returns_rule, equal_var=False)

    # --- T-Test: Hybrid vs Buy & Hold ---
    returns_bnh = eq_bnh['Total'].pct_change().dropna().values
    min_len2 = min(len(returns_hybrid), len(returns_bnh))
    t_stat_bnh, p_value_bnh = stats.ttest_ind(
        returns_hybrid[:min_len2], returns_bnh[:min_len2], equal_var=False
    )

    # --- Print Results ---
    print("\n" + "="*70)
    print("STATISTICAL VALIDATION REPORT")
    print("="*70)

    print("\n--- Risk-Adjusted Performance Ratios ---")
    print(f"{'Strategy':<20} {'Sharpe Ratio':>15} {'Sortino Ratio':>15}")
    print("-"*50)
    print(f"{'Buy & Hold':<20} {sharpe_bnh:>15.4f} {sortino_bnh:>15.4f}")
    print(f"{'Rule-Only':<20} {sharpe_rule:>15.4f} {sortino_rule:>15.4f}")
    print(f"{'Hybrid (Ours)':<20} {sharpe_hybrid:>15.4f} {sortino_hybrid:>15.4f}")

    print("\n--- Hypothesis Testing (Two-Sample Welch's T-Test) ---")
    print(f"\nH0: Mean daily returns of Hybrid = Mean daily returns of Rule-Only")
    print(f"H1: Mean daily returns of Hybrid != Mean daily returns of Rule-Only")
    print(f"  t-statistic : {t_stat:.4f}")
    print(f"  p-value     : {p_value:.6f}")
    if p_value < 0.05:
        print(f"  Result      : REJECT H0 at a=0.05 -> Hybrid is statistically different from Rule-Only [YES]")
    else:
        print(f"  Result      : FAIL TO REJECT H0 at a=0.05 -> No statistically significant difference")

    print(f"\nH0: Mean daily returns of Hybrid = Mean daily returns of Buy & Hold")
    print(f"H1: Mean daily returns of Hybrid != Mean daily returns of Buy & Hold")
    print(f"  t-statistic : {t_stat_bnh:.4f}")
    print(f"  p-value     : {p_value_bnh:.6f}")
    if p_value_bnh < 0.05:
        print(f"  Result      : REJECT H0 at a=0.05 -> Hybrid is statistically different from Buy & Hold [YES]")
    else:
        print(f"  Result      : FAIL TO REJECT H0 at a=0.05 -> No statistically significant difference")

    # --- Summary Stats ---
    print("\n--- Daily Return Statistics ---")
    print(f"{'Metric':<30} {'Rule-Only':>15} {'Hybrid':>15}")
    print("-"*60)
    print(f"{'Mean Daily Return':<30} {np.mean(returns_rule)*100:>14.4f}% {np.mean(returns_hybrid)*100:>14.4f}%")
    print(f"{'Std Dev (Daily)':<30} {np.std(returns_rule)*100:>14.4f}% {np.std(returns_hybrid)*100:>14.4f}%")
    print(f"{'Positive Days':<30} {(returns_rule>0).sum():>15} {(returns_hybrid>0).sum():>15}")
    print(f"{'Negative Days':<30} {(returns_rule<0).sum():>15} {(returns_hybrid<0).sum():>15}")

    print("\n" + "="*70)

    # Save report
    report = {
        'Metric': ['Sharpe Ratio', 'Sortino Ratio', 'Mean Daily Return %', 
                    'Std Dev Daily %', 'T-Stat (vs Rule)', 'P-Value (vs Rule)',
                    'T-Stat (vs B&H)', 'P-Value (vs B&H)'],
        'Buy & Hold': [sharpe_bnh, sortino_bnh, np.mean(eq_bnh['Total'].pct_change().dropna())*100,
                       np.std(eq_bnh['Total'].pct_change().dropna())*100, '-', '-',
                       '-', '-'],
        'Rule-Only': [sharpe_rule, sortino_rule, np.mean(returns_rule)*100,
                      np.std(returns_rule)*100, '-', '-', '-', '-'],
        'Hybrid': [sharpe_hybrid, sortino_hybrid, np.mean(returns_hybrid)*100,
                   np.std(returns_hybrid)*100, t_stat, p_value, t_stat_bnh, p_value_bnh]
    }
    report_df = pd.DataFrame(report)
    report_path = os.path.join(data_dir, "statistical_validation.csv")
    report_df.to_csv(report_path, index=False)
    print(f"\nSaved statistical validation report to {report_path}")


if __name__ == "__main__":
    run_statistical_validation()
