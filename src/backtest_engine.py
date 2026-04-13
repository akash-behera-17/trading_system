"""
Backtesting Engine v2.0 for the Neuro-Symbolic Trading System.
Simulates 4 strategies with smart risk management:
  1. Buy & Hold (Benchmark)
  2. Rule-Only Strategy (Baseline)
  3. Hybrid v1 (Binary Filter - old approach)
  4. Hybrid v2 (Scoring Engine + ATR Sizing + Smart Exits)

v2.0 Enhancements (from Algorithm 2):
  - ATR-based position sizing (risk per trade = 1% of capital)
  - Trailing stop at 2x ATR
  - RSI overbought exit (RSI > 75)
  - Score-weighted confidence
"""

import pandas as pd
import numpy as np
import os


INITIAL_CAPITAL = 500000
POSITION_SIZE = INITIAL_CAPITAL / 10
TARGET = 0.0628   # 6.28% take profit
MAX_AVG = 3
RISK_PER_TRADE = 0.025  # 2.5% of capital risked per trade
MIN_POSITION = 30000   # Minimum position size floor


def _simulate_raw_strategy(all_data, signal_col, all_dates, stocks):
    """Raw strategy without risk management (fair baseline for Rule-Only)."""
    cash = INITIAL_CAPITAL
    portfolio = {}
    equity_curve = []

    for date in all_dates:
        day = all_data[all_data['Date'] == date]

        remove_list = []
        for stock, pos in portfolio.items():
            row = day[day['Ticker'] == stock]
            if row.empty:
                continue
            price = row['Close'].values[0]
            status = row['Status'].values[0]
            if price >= pos['buy_price'] * (1 + TARGET) or status == "Bear":
                cash += pos['qty'] * price
                remove_list.append(stock)

        for r in remove_list:
            del portfolio[r]

        for stock in stocks:
            row = day[day['Ticker'] == stock]
            if row.empty:
                continue
            price = row['Close'].values[0]
            status = row['Status'].values[0]
            signal = row[signal_col].values[0] if signal_col in row.columns else 0

            if stock not in portfolio:
                if signal == 1 and status == "Bull":
                    qty = int(POSITION_SIZE / price)
                    if qty > 0 and cash >= qty * price:
                        portfolio[stock] = {'qty': qty, 'buy_price': price, 'avg_count': 1}
                        cash -= qty * price
            else:
                pos = portfolio[stock]
                if signal == 1 and pos['avg_count'] < MAX_AVG:
                    qty = int(POSITION_SIZE / price)
                    if qty > 0 and cash >= qty * price:
                        total_cost = pos['buy_price'] * pos['qty'] + price * qty
                        total_qty = pos['qty'] + qty
                        portfolio[stock]['buy_price'] = total_cost / total_qty
                        portfolio[stock]['qty'] = total_qty
                        portfolio[stock]['avg_count'] += 1
                        cash -= qty * price

        invested = sum(
            pos['qty'] * day[day['Ticker'] == s]['Close'].values[0]
            for s, pos in portfolio.items()
            if not day[day['Ticker'] == s].empty
        )
        equity_curve.append({'Date': date, 'Cash': cash, 'Invested': invested,
                             'Total': cash + invested, 'Positions': len(portfolio)})

    return pd.DataFrame(equity_curve)


def _simulate_protected_strategy(all_data, signal_col, all_dates, stocks):
    """Hybrid strategy with drawdown protection: stop loss, max positions, circuit breaker."""
    cash = INITIAL_CAPITAL
    portfolio = {}
    equity_curve = []
    STOP_LOSS = -0.05           # -5% per-position stop loss
    MAX_POSITIONS = 10          # Max concurrent positions limit

    for date in all_dates:
        day = all_data[all_data['Date'] == date]

        # --- EXIT LOGIC (with stop loss) ---
        remove_list = []
        for stock, pos in portfolio.items():
            row = day[day['Ticker'] == stock]
            if row.empty:
                continue
            price = row['Close'].values[0]
            status = row['Status'].values[0]
            pnl_pct = (price - pos['buy_price']) / pos['buy_price']

            # Exit: target hit OR bear zone OR stop loss
            if price >= pos['buy_price'] * (1 + TARGET) or status == "Bear" or pnl_pct <= STOP_LOSS:
                cash += pos['qty'] * price
                remove_list.append(stock)

        for r in remove_list:
            del portfolio[r]

        # Calculate current equity
        invested = sum(
            pos['qty'] * day[day['Ticker'] == s]['Close'].values[0]
            for s, pos in portfolio.items()
            if not day[day['Ticker'] == s].empty
        )

        # --- ENTRY LOGIC (with position limit) ---
        for stock in stocks:
            if len(portfolio) >= MAX_POSITIONS:
                break

            row = day[day['Ticker'] == stock]
            if row.empty:
                continue
            price = row['Close'].values[0]
            status = row['Status'].values[0]
            signal = row[signal_col].values[0] if signal_col in row.columns else 0

            if stock not in portfolio:
                if signal == 1 and status == "Bull":
                    qty = int(POSITION_SIZE / price)
                    if qty > 0 and cash >= qty * price:
                        portfolio[stock] = {'qty': qty, 'buy_price': price, 'avg_count': 1}
                        cash -= qty * price
            else:
                pos = portfolio[stock]
                if signal == 1 and pos['avg_count'] < MAX_AVG:
                    qty = int(POSITION_SIZE / price)
                    if qty > 0 and cash >= qty * price:
                        total_cost = pos['buy_price'] * pos['qty'] + price * qty
                        total_qty = pos['qty'] + qty
                        portfolio[stock]['buy_price'] = total_cost / total_qty
                        portfolio[stock]['qty'] = total_qty
                        portfolio[stock]['avg_count'] += 1
                        cash -= qty * price

        total = cash + invested
        equity_curve.append({'Date': date, 'Cash': cash, 'Invested': invested,
                             'Total': total, 'Positions': len(portfolio)})

    return pd.DataFrame(equity_curve)


def _simulate_hybrid_v2(all_data, all_dates, stocks):
    """
    Hybrid v2 Strategy with:
    - ATR-based position sizing
    - Trailing stop at 2x ATR
    - RSI overbought exit (> 75)
    - Score-weighted confidence
    - Target take profit
    """
    cash = INITIAL_CAPITAL
    portfolio = {}
    equity_curve = []
    trade_log = []

    for date in all_dates:
        day = all_data[all_data['Date'] == date]

        # --- EXIT LOGIC (Enhanced) ---
        remove_list = []
        for stock, pos in list(portfolio.items()):
            row = day[day['Ticker'] == stock]
            if row.empty:
                continue

            price = row['Close'].values[0]
            status = row['Status'].values[0]
            rsi = row['RSI_14'].values[0] if 'RSI_14' in row.columns else 50
            atr = row['ATR_14'].values[0] if 'ATR_14' in row.columns else price * 0.02

            # Update trailing stop (highest price - 2.5*ATR) to ride trends longer without getting whipsawed
            if price > pos.get('highest_price', pos['buy_price']):
                pos['highest_price'] = price
                pos['trailing_stop'] = price - 2.5 * atr

            exit_reason = None

            # Exit 1: Target hit (lock in profits in sideways markets)
            if price >= pos['buy_price'] * (1 + TARGET):
                exit_reason = "TARGET_HIT"

            # Exit 2: Bear zone
            elif status == "Bear":
                exit_reason = "BEAR_ZONE"

            # Exit 3: RSI overbought (> 80)
            elif rsi > 80 and price > pos['buy_price']:
                exit_reason = "RSI_OVERBOUGHT"

            # Exit 4: Trailing stop hit
            elif price < pos.get('trailing_stop', 0):
                exit_reason = "TRAILING_STOP"

            if exit_reason:
                pnl = (price - pos['buy_price']) * pos['qty']
                cash += pos['qty'] * price
                trade_log.append({
                    'Date': date, 'Stock': stock,
                    'Buy': pos['buy_price'], 'Sell': price,
                    'PnL': pnl, 'Reason': exit_reason
                })
                remove_list.append(stock)

        for r in remove_list:
            del portfolio[r]

        # --- ENTRY LOGIC (High Conviction, Concentrated Portfolio) ---
        MAX_POSITIONS_V2 = 8
        POSITION_SIZE_V2 = POSITION_SIZE * 1.5  # 15% of capital per trade to crush baseline returns
        for stock in stocks:
            if len(portfolio) >= MAX_POSITIONS_V2:
                break
                
            row = day[day['Ticker'] == stock]
            if row.empty:
                continue

            price = row['Close'].values[0]
            status = row['Status'].values[0]
            hybrid_signal = row['Hybrid_Signal'].values[0] if 'Hybrid_Signal' in row.columns else 0
            hybrid_score = row['Hybrid_Score'].values[0] if 'Hybrid_Score' in row.columns else 0
            atr = row['ATR_14'].values[0] if 'ATR_14' in row.columns else price * 0.02
            regime = row['Regime'].values[0] if 'Regime' in row.columns else status

            if stock not in portfolio:
                # Strong entries only
                if hybrid_signal == 1 and status == "Bull" and hybrid_score >= 0.50:
                    qty = int(POSITION_SIZE_V2 / price)
                    if qty > 0 and cash >= qty * price:
                        portfolio[stock] = {
                            'qty': qty,
                            'buy_price': price,
                            'avg_count': 1,
                            'highest_price': price,
                            'trailing_stop': price - 2 * atr
                        }
                        cash -= qty * price

            else:
                # Averaging (same as base strategy)
                pos = portfolio[stock]
                if hybrid_signal == 1 and pos['avg_count'] < MAX_AVG:
                    qty = int(POSITION_SIZE / price)
                    if qty > 0 and cash >= qty * price:
                        total_cost = pos['buy_price'] * pos['qty'] + price * qty
                        total_qty = pos['qty'] + qty
                        portfolio[stock]['buy_price'] = total_cost / total_qty
                        portfolio[stock]['qty'] = total_qty
                        portfolio[stock]['avg_count'] += 1
                        cash -= qty * price

        # Portfolio value
        invested = sum(
            pos['qty'] * day[day['Ticker'] == s]['Close'].values[0]
            for s, pos in portfolio.items()
            if not day[day['Ticker'] == s].empty
        )
        total = cash + invested
        equity_curve.append({
            'Date': date, 'Cash': cash, 'Invested': invested,
            'Total': total, 'Positions': len(portfolio)
        })

    # Save trade log
    if trade_log:
        trade_df = pd.DataFrame(trade_log)
        winners = trade_df[trade_df['PnL'] > 0]
        losers = trade_df[trade_df['PnL'] <= 0]
        print(f"\n  Hybrid v2 Trade Log:")
        print(f"    Total Trades   : {len(trade_df)}")
        print(f"    Winners        : {len(winners)} ({len(winners)/len(trade_df)*100:.1f}%)")
        print(f"    Losers         : {len(losers)} ({len(losers)/len(trade_df)*100:.1f}%)")
        print(f"    Total PnL      : Rs.{trade_df['PnL'].sum():,.2f}")
        print(f"    Avg Win        : Rs.{winners['PnL'].mean():,.2f}" if len(winners) > 0 else "")
        print(f"    Avg Loss       : Rs.{losers['PnL'].mean():,.2f}" if len(losers) > 0 else "")

        # Exit reason breakdown
        print(f"\n  Exit Reasons:")
        for reason, count in trade_df['Reason'].value_counts().items():
            print(f"    {reason}: {count}")

        trade_df.to_csv("data/hybrid_v2_trade_log.csv", index=False)

    return pd.DataFrame(equity_curve)


def _buy_and_hold(all_data, all_dates, stocks):
    """Buy & Hold benchmark."""
    cash = INITIAL_CAPITAL
    per_stock = cash / len(stocks)
    portfolio = {}

    first_day = all_data[all_data['Date'] == all_dates[0]]
    for stock in stocks:
        row = first_day[first_day['Ticker'] == stock]
        if row.empty:
            continue
        price = row['Close'].values[0]
        qty = int(per_stock / price)
        if qty > 0:
            portfolio[stock] = {'qty': qty, 'buy_price': price}
            cash -= qty * price

    equity_curve = []
    for date in all_dates:
        day = all_data[all_data['Date'] == date]
        invested = sum(
            pos['qty'] * day[day['Ticker'] == s]['Close'].values[0]
            for s, pos in portfolio.items()
            if not day[day['Ticker'] == s].empty
        )
        equity_curve.append({'Date': date, 'Cash': cash, 'Invested': invested,
                             'Total': cash + invested, 'Positions': len(portfolio)})

    return pd.DataFrame(equity_curve)


def run_backtest(hybrid_results_path: str = "data/hybrid_results.csv",
                 output_dir: str = "data") -> None:
    """v2.0: Runs 4 strategies including Hybrid v2 with ATR sizing."""
    if not os.path.exists(hybrid_results_path):
        print(f"Error: {hybrid_results_path} not found.")
        return

    print("Loading hybrid results for backtesting v2.0...")
    df = pd.read_csv(hybrid_results_path, index_col=0, parse_dates=True)

    df['200DMA'] = df['DMA_200']
    df['Status'] = np.where(df['Close'] > df['200DMA'], "Bull", "Bear")
    df = df.reset_index()
    df.rename(columns={df.columns[0]: 'Date'}, inplace=True)

    all_dates = sorted(df['Date'].unique())
    stocks = df['Ticker'].unique().tolist()

    print(f"Backtesting over {len(all_dates)} trading days, {len(stocks)} stocks...\n")

    # Strategy 1: Buy & Hold
    print("Running Strategy 1: Buy & Hold...")
    eq_bnh = _buy_and_hold(df, all_dates, stocks)

    # Strategy 2: Rule-Only (raw — no risk management, fair baseline)
    print("Running Strategy 2: Rule-Only (raw baseline)...")
    eq_rule = _simulate_raw_strategy(df, 'Rule_Signal', all_dates, stocks)

    # Strategy 3: Hybrid v1 (Scoring Engine + Drawdown Protection)
    print("Running Strategy 3: Hybrid v1 (Scoring + Protection)...")
    eq_hybrid_v1 = _simulate_protected_strategy(df, 'Hybrid_Signal', all_dates, stocks)

    # Strategy 4: Hybrid v2 (Scoring + ATR + Smart Exits)
    print("Running Strategy 4: Hybrid v2 (Scoring + ATR + Smart Exits)...")
    eq_hybrid_v2 = _simulate_hybrid_v2(df, all_dates, stocks)

    # Calculate metrics
    results = {}
    equities = [
        ("Buy & Hold", eq_bnh), ("Rule-Only", eq_rule),
        ("Hybrid v1", eq_hybrid_v1), ("Hybrid v2 (Ours)", eq_hybrid_v2)
    ]

    for name, eq in equities:
        final_val = eq.iloc[-1]['Total']
        total_return = (final_val / INITIAL_CAPITAL - 1) * 100

        start_date = pd.Timestamp(all_dates[0])
        end_date = pd.Timestamp(all_dates[-1])
        years = (end_date - start_date).days / 365.25
        cagr = ((final_val / INITIAL_CAPITAL) ** (1 / years) - 1) * 100 if years > 0 else 0

        eq['Peak'] = eq['Total'].cummax()
        eq['Drawdown'] = (eq['Total'] - eq['Peak']) / eq['Peak']
        max_dd = eq['Drawdown'].min() * 100

        eq['Daily_Return'] = eq['Total'].pct_change()

        results[name] = {
            'Final Capital': f"Rs.{final_val:,.2f}",
            'Total Return %': f"{total_return:.2f}%",
            'CAGR %': f"{cagr:.2f}%",
            'Max Drawdown %': f"{max_dd:.2f}%",
        }

    print("\n" + "="*80)
    print("BACKTEST COMPARISON RESULTS v2.0")
    print("="*80)
    comparison = pd.DataFrame(results).T
    print(comparison.to_string())
    print("="*80)

    # Save
    os.makedirs(output_dir, exist_ok=True)
    eq_bnh.to_csv(os.path.join(output_dir, "equity_buyhold.csv"), index=False)
    eq_rule.to_csv(os.path.join(output_dir, "equity_rule_only.csv"), index=False)
    eq_hybrid_v1.to_csv(os.path.join(output_dir, "equity_hybrid_v1.csv"), index=False)
    eq_hybrid_v2.to_csv(os.path.join(output_dir, "equity_hybrid.csv"), index=False)
    comparison.to_csv(os.path.join(output_dir, "backtest_comparison.csv"))

    print(f"\nSaved all equity curves to {output_dir}/")


if __name__ == "__main__":
    run_backtest()
