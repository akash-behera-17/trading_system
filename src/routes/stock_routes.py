import pandas as pd
import yfinance as yf
import ta
import numpy as np
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

stock_bp = Blueprint('stocks', __name__, url_prefix='/api/stocks')


def _compute_confidence_and_trade_plan(
    price, w52_high, w52_low, fib_levels, fib_position,
    ma_values, ma_signals_dict, macd_cross, rsi_val, sellers_fading,
    bb_position, dma50_val, dma200_val, support_1, support_2,
    resistance_1, avg_vol_20, score_fn, signals_dict
):
    """Compute confidence score, trade plan scenarios, and overall rating."""

    # === CONFIDENCE SCORE (0-100) ===
    # Each factor contributes points based on alignment
    points = 0
    max_points = 80

    # Trend alignment (max 15 pts)
    if dma50_val and price > dma50_val: points += 8
    if dma200_val and price > dma200_val: points += 7

    # MA stack golden cross (max 10 pts)
    if dma50_val and dma200_val and dma50_val > dma200_val: points += 10

    # RSI in healthy zone (max 10 pts)
    if rsi_val:
        if 40 < rsi_val < 65: points += 10
        elif 30 < rsi_val <= 40: points += 5
        elif rsi_val > 65: points += 3

    # MACD bullish (max 10 pts)
    if macd_cross == "bullish": points += 10

    # Volume conviction (max 10 pts)
    if sellers_fading: points += 7
    if avg_vol_20 and avg_vol_20 > 0: points += 3

    # Bollinger positioning (max 10 pts)
    if bb_position == "mid-band": points += 6
    elif bb_position == "near_lower": points += 10
    elif bb_position == "near_upper": points += 2

    # Fibonacci position (max 15 pts)
    if fib_position > 61.8: points += 15
    elif fib_position > 50: points += 10
    elif fib_position > 38.2: points += 6
    elif fib_position < 23.6: points += 2

    confidence = min(round((points / max_points) * 100), 100)

    # === OVERALL RATING ===
    if confidence >= 75:
        overall_rating = "STRONG BUY"
        rating_emoji = "🟢"
        rating_desc = "Strong technical alignment — breakout candidate"
    elif confidence >= 60:
        overall_rating = "BUY ON DIP"
        rating_emoji = "🟡"
        rating_desc = "Positive structure — wait for pullback entry"
    elif confidence >= 45:
        overall_rating = "NEUTRAL"
        rating_emoji = "🟡"
        rating_desc = "Mixed signals — don't chase, wait for clarity"
    elif confidence >= 30:
        overall_rating = "CAUTIOUS"
        rating_emoji = "🟠"
        rating_desc = "Weak momentum — avoid fresh positions"
    else:
        overall_rating = "AVOID"
        rating_emoji = "🔴"
        rating_desc = "Bearish structure — stay out"

    # Rating bars (each out of 10)
    strong_buy_bar = min(10, max(0, (confidence - 70) // 3)) if confidence > 70 else 0
    buy_bar = min(10, max(0, (confidence - 50) // 3)) if confidence > 50 else 0
    neutral_bar = min(10, max(0, (confidence - 30) // 3)) if confidence > 30 else 0
    sell_bar = min(10, max(0, (50 - confidence) // 5)) if confidence < 50 else 0
    strong_sell_bar = min(10, max(0, (30 - confidence) // 3)) if confidence < 30 else 0

    # === TRADE PLAN ===
    # Determine key levels
    fib_382 = fib_levels.get("38.2", 0)
    fib_618 = fib_levels.get("61.8", 0)
    fib_500 = fib_levels.get("50.0", 0)

    # Pullback entry zone: confluence of 38.2% Fib + 100 DMA or 50 DMA
    pullback_low = fib_382
    pullback_high = fib_500
    if dma50_val and abs(dma50_val - fib_382) < (w52_high - w52_low) * 0.1:
        pullback_high = round(dma50_val, 2)

    # Stop loss: below 200 DMA or below 23.6% Fib
    stop_loss = round(fib_levels.get("23.6", w52_low * 1.02), 2)
    if dma200_val and dma200_val < pullback_low:
        stop_loss = round(dma200_val * 0.995, 2)

    # Targets
    target_1 = round(resistance_1 if resistance_1 else w52_high * 0.97, 2)
    target_2 = round(w52_high, 2)
    target_3 = round(w52_high * 1.08, 2)  # ~8% above 52W high

    # R:R calculations from pullback midpoint
    entry_mid = round((pullback_low + pullback_high) / 2, 2)
    risk = round(entry_mid - stop_loss, 2)
    reward_1 = round(target_1 - entry_mid, 2) if target_1 > entry_mid else 0
    reward_2 = round(target_2 - entry_mid, 2) if target_2 > entry_mid else 0
    reward_3 = round(target_3 - entry_mid, 2) if target_3 > entry_mid else 0

    rr_1 = round(reward_1 / risk, 1) if risk > 0 else 0
    rr_2 = round(reward_2 / risk, 1) if risk > 0 else 0
    rr_3 = round(reward_3 / risk, 1) if risk > 0 else 0

    # Breakout entry
    breakout_entry = round(w52_high * 0.99, 2)
    breakout_stop = round(w52_high * 0.96, 2)
    breakout_target = target_3
    breakout_risk = round(breakout_entry - breakout_stop, 2)
    breakout_reward = round(breakout_target - breakout_entry, 2)
    breakout_rr = round(breakout_reward / breakout_risk, 1) if breakout_risk > 0 else 0

    # No-trade zone
    no_trade_low = round(pullback_high, 2)
    no_trade_high = round(w52_high * 0.97, 2)

    return {
        "confidence": {
            "score": confidence,
            "rating": overall_rating,
            "emoji": rating_emoji,
            "description": rating_desc,
            "bars": {
                "strong_buy": {"value": strong_buy_bar, "label": f"{'Needs ' + str(round(w52_high, 0)) + ' break' if strong_buy_bar < 5 else 'Technical alignment strong'}"},
                "buy": {"value": buy_bar, "label": f"At ₹{round(pullback_low)}-{round(pullback_high)} zone" if buy_bar > 3 else "Not yet"},
                "neutral": {"value": neutral_bar, "label": "Current level — don't chase" if 40 < confidence < 65 else ""},
                "sell": {"value": sell_bar, "label": f"Only below ₹{round(stop_loss)}" if sell_bar > 2 else "Not applicable"},
                "strong_sell": {"value": strong_sell_bar, "label": "Not applicable" if strong_sell_bar < 3 else "Structure broken"}
            }
        },
        "trade_plan": {
            "scenario_a": {
                "name": "Pullback Buy (Primary)",
                "description": "Wait for correction to exhaust at confluence support zone",
                "entry_low": pullback_low,
                "entry_high": pullback_high,
                "entry_rationale": f"38.2% Fibonacci + SMA confluence. High-probability demand zone.",
                "stop_loss": stop_loss,
                "stop_rationale": f"Below 200-DMA / 23.6% Fibonacci. Limits damage, avoids noise.",
                "targets": [
                    {"label": "Target 1", "price": target_1, "pct": round(((target_1 - entry_mid) / entry_mid) * 100, 1), "rationale": "Immediate resistance / prior support"},
                    {"label": "Target 2", "price": target_2, "pct": round(((target_2 - entry_mid) / entry_mid) * 100, 1), "rationale": "52-week high retest"},
                    {"label": "Target 3", "price": target_3, "pct": round(((target_3 - entry_mid) / entry_mid) * 100, 1), "rationale": "Fibonacci extension / analyst consensus"}
                ],
                "risk_per_share": risk,
                "reward_targets": [
                    {"label": "R:R to T1", "value": f"1:{rr_1}", "good": rr_1 >= 2},
                    {"label": "R:R to T2", "value": f"1:{rr_2}", "good": rr_2 >= 2},
                    {"label": "R:R to T3", "value": f"1:{rr_3}", "good": rr_3 >= 2}
                ]
            },
            "scenario_b": {
                "name": "Breakout Buy (Aggressive)",
                "description": f"Only if stock reclaims ₹{round(w52_high, 0)} with strong volume",
                "entry_low": breakout_entry,
                "entry_high": round(breakout_entry + 5, 2),
                "entry_rationale": f"Confirmed close above ₹{round(w52_high * 0.98, 0)} with volume spike",
                "stop_loss": breakout_stop,
                "stop_rationale": "Below breakout pivot",
                "target": breakout_target,
                "target_pct": round(((breakout_target - breakout_entry) / breakout_entry) * 100, 1),
                "risk": breakout_risk,
                "reward": breakout_reward,
                "rr": f"1:{breakout_rr}",
                "rr_good": breakout_rr >= 2
            },
            "no_trade_zone": {
                "low": no_trade_low,
                "high": no_trade_high,
                "reason": "Dead zone — too far from support for good R:R, too weak for breakout. Overhead resistance immediately above."
            }
        }
    }

# Nifty 50 constituents for search autocomplete and market movers
NIFTY_50 = [
    {"ticker": "RELIANCE.NS", "name": "Reliance Industries Ltd"},
    {"ticker": "TCS.NS", "name": "Tata Consultancy Services Ltd"},
    {"ticker": "HDFCBANK.NS", "name": "HDFC Bank Ltd"},
    {"ticker": "INFY.NS", "name": "Infosys Ltd"},
    {"ticker": "ICICIBANK.NS", "name": "ICICI Bank Ltd"},
    {"ticker": "HINDUNILVR.NS", "name": "Hindustan Unilever Ltd"},
    {"ticker": "ITC.NS", "name": "ITC Ltd"},
    {"ticker": "SBIN.NS", "name": "State Bank of India"},
    {"ticker": "BHARTIARTL.NS", "name": "Bharti Airtel Ltd"},
    {"ticker": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank Ltd"},
    {"ticker": "BAJFINANCE.NS", "name": "Bajaj Finance Ltd"},
    {"ticker": "LT.NS", "name": "Larsen & Toubro Ltd"},
    {"ticker": "ASIANPAINT.NS", "name": "Asian Paints Ltd"},
    {"ticker": "HCLTECH.NS", "name": "HCL Technologies Ltd"},
    {"ticker": "MARUTI.NS", "name": "Maruti Suzuki India Ltd"},
    {"ticker": "AXISBANK.NS", "name": "Axis Bank Ltd"},
    {"ticker": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries Ltd"},
    {"ticker": "TITAN.NS", "name": "Titan Company Ltd"},
    {"ticker": "WIPRO.NS", "name": "Wipro Ltd"},
    {"ticker": "ULTRACEMCO.NS", "name": "UltraTech Cement Ltd"},
    {"ticker": "M&M.NS", "name": "Mahindra & Mahindra Ltd"},
    {"ticker": "NESTLEIND.NS", "name": "Nestle India Ltd"},
    {"ticker": "POWERGRID.NS", "name": "Power Grid Corporation of India Ltd"},
    {"ticker": "BAJAJFINSV.NS", "name": "Bajaj Finserv Ltd"},
    {"ticker": "INDUSINDBK.NS", "name": "IndusInd Bank Ltd"},
    {"ticker": "TATAMOTORS.NS", "name": "Tata Motors Ltd"},
    {"ticker": "NTPC.NS", "name": "NTPC Ltd"},
    {"ticker": "ADANIENT.NS", "name": "Adani Enterprises Ltd"},
    {"ticker": "ADANIPORTS.NS", "name": "Adani Ports and SEZ Ltd"},
    {"ticker": "TATASTEEL.NS", "name": "Tata Steel Ltd"},
    {"ticker": "ONGC.NS", "name": "Oil and Natural Gas Corporation Ltd"},
    {"ticker": "JSWSTEEL.NS", "name": "JSW Steel Ltd"},
    {"ticker": "COALINDIA.NS", "name": "Coal India Ltd"},
    {"ticker": "TECHM.NS", "name": "Tech Mahindra Ltd"},
    {"ticker": "DRREDDY.NS", "name": "Dr. Reddy's Laboratories Ltd"},
    {"ticker": "CIPLA.NS", "name": "Cipla Ltd"},
    {"ticker": "APOLLOHOSP.NS", "name": "Apollo Hospitals Enterprise Ltd"},
    {"ticker": "EICHERMOT.NS", "name": "Eicher Motors Ltd"},
    {"ticker": "DIVISLAB.NS", "name": "Divi's Laboratories Ltd"},
    {"ticker": "BPCL.NS", "name": "Bharat Petroleum Corporation Ltd"},
    {"ticker": "BRITANNIA.NS", "name": "Britannia Industries Ltd"},
    {"ticker": "HEROMOTOCO.NS", "name": "Hero MotoCorp Ltd"},
    {"ticker": "GRASIM.NS", "name": "Grasim Industries Ltd"},
    {"ticker": "HINDALCO.NS", "name": "Hindalco Industries Ltd"},
    {"ticker": "TATACONSUM.NS", "name": "Tata Consumer Products Ltd"},
    {"ticker": "SBILIFE.NS", "name": "SBI Life Insurance Company Ltd"},
    {"ticker": "HDFCLIFE.NS", "name": "HDFC Life Insurance Company Ltd"},
    {"ticker": "BAJAJ-AUTO.NS", "name": "Bajaj Auto Ltd"},
    {"ticker": "SHRIRAMFIN.NS", "name": "Shriram Finance Ltd"},
    {"ticker": "BANKBARODA.NS", "name": "Bank of Baroda"}
]


@stock_bp.route('/search', methods=['GET'])
def search_stocks():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify(NIFTY_50[:10])

    results = [
        s for s in NIFTY_50
        if query in s['ticker'].lower() or query in s['name'].lower()
    ]

    return jsonify(results)


@stock_bp.route('/chart-data', methods=['GET'])
def chart_data():
    """Returns OHLCV + DMA data for charting. Supports period param: 1mo, 6mo, 1y, 3y, 5y, max."""
    ticker = request.args.get('ticker', '')
    period = request.args.get('period', '1y')

    if not ticker:
        return jsonify({"error": "Ticker is required"}), 400

    # Map friendly period names
    period_map = {
        '1mo': '1mo', '1m': '1mo',
        '6mo': '6mo', '6m': '6mo',
        '1y': '1y', '1yr': '1y',
        '3y': '3y', '3yr': '3y',
        '5y': '5y', '5yr': '5y',
        'max': 'max', 'all': 'max'
    }
    yf_period = period_map.get(period.lower(), '1y')

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=yf_period)

        if df.empty:
            return jsonify({"error": f"No data for {ticker}"}), 404

        # Compute DMAs
        close = df['Close']
        df['DMA_50'] = close.rolling(50).mean()
        df['DMA_100'] = close.rolling(100).mean()
        df['DMA_200'] = close.rolling(200).mean()

        # Build OHLCV array
        ohlcv = []
        for idx, row in df.iterrows():
            ts = int(idx.timestamp())
            ohlcv.append({
                "time": ts,
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2),
                "volume": int(row['Volume']) if pd.notna(row['Volume']) else 0
            })

        # Build DMA arrays (skip NaN)
        dma50 = [{"time": int(idx.timestamp()), "value": round(float(v), 2)}
                 for idx, v in df['DMA_50'].items() if pd.notna(v)]
        dma100 = [{"time": int(idx.timestamp()), "value": round(float(v), 2)}
                  for idx, v in df['DMA_100'].items() if pd.notna(v)]
        dma200 = [{"time": int(idx.timestamp()), "value": round(float(v), 2)}
                  for idx, v in df['DMA_200'].items() if pd.notna(v)]

        # Volume array
        volume = [{"time": int(idx.timestamp()),
                   "value": int(row['Volume']) if pd.notna(row['Volume']) else 0,
                   "color": 'rgba(34,197,94,0.3)' if row['Close'] >= row['Open'] else 'rgba(239,68,68,0.3)'}
                  for idx, row in df.iterrows()]

        info = stock.info
        return jsonify({
            "ticker": ticker,
            "name": info.get('shortName', ticker),
            "period": yf_period,
            "ohlcv": ohlcv,
            "volume": volume,
            "dma50": dma50,
            "dma100": dma100,
            "dma200": dma200
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stock_bp.route('/market-movers', methods=['GET'])
def market_movers():
    """Returns top 5 gainers and top 5 losers from Nifty 50 by today's % change."""
    try:
        tickers_str = " ".join([s['ticker'] for s in NIFTY_50])
        data = yf.download(tickers_str, period="2d", progress=False, group_by='ticker')

        movers = []
        for stock in NIFTY_50:
            t = stock['ticker']
            try:
                if isinstance(data.columns, pd.MultiIndex):
                    ticker_data = data[t]
                else:
                    ticker_data = data

                if len(ticker_data) < 2:
                    continue

                prev_close = float(ticker_data['Close'].iloc[-2])
                curr_close = float(ticker_data['Close'].iloc[-1])

                if pd.isna(prev_close) or pd.isna(curr_close) or prev_close == 0:
                    continue

                pct_change = ((curr_close - prev_close) / prev_close) * 100

                movers.append({
                    "ticker": t,
                    "name": stock['name'],
                    "price": round(curr_close, 2),
                    "change_pct": round(pct_change, 2)
                })
            except Exception:
                continue

        movers.sort(key=lambda x: x['change_pct'], reverse=True)

        return jsonify({
            "gainers": movers[:5],
            "losers": movers[-5:][::-1]  # reverse so worst first
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stock_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({"error": "Ticker parameter is required"}), 400

    try:
        stock = yf.Ticker(ticker)

        # 1. Fundamentals
        info = stock.info
        fundamentals = {
            "marketCap": info.get('marketCap', 'N/A'),
            "fiftyTwoWeekHigh": info.get('fiftyTwoWeekHigh', 'N/A'),
            "fiftyTwoWeekLow": info.get('fiftyTwoWeekLow', 'N/A'),
            "trailingPE": info.get('trailingPE', 'N/A'),
            "priceToBook": info.get('priceToBook', 'N/A'),
            "currentPrice": info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
            "shortName": info.get('shortName', ticker),
            "sector": info.get('sector', 'N/A'),
            "industry": info.get('industry', 'N/A'),
            "previousClose": info.get('previousClose', 'N/A'),
            "dayHigh": info.get('dayHigh', 'N/A'),
            "dayLow": info.get('dayLow', 'N/A'),
        }

        # 2. Historical Data (1 year for DMA200)
        hist = stock.history(period="1y", interval="1d")
        if hist.empty:
            return jsonify({"error": f"No historical data found for {ticker}"}), 404

        if isinstance(hist.columns, pd.MultiIndex):
            try:
                hist.columns = hist.columns.droplevel('Ticker')
            except KeyError:
                hist.columns = hist.columns.droplevel(1)

        # 3. Chart Data Formatting
        chart_data = []
        for date, row in hist.iterrows():
            chart_data.append({
                "date": date.strftime('%Y-%m-%d'),
                "price": round(row['Close'], 2)
            })

        # 4. Technical Indicators & Heuristics (Pros/Cons)
        df = hist.copy()
        df['DMA50'] = df['Close'].rolling(window=50).mean()
        df['DMA200'] = df['Close'].rolling(window=200).mean()
        df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()

        latest = df.iloc[-1]
        close_price = latest['Close']
        dma50 = latest['DMA50']
        dma200 = latest['DMA200']
        rsi = latest['RSI']

        pros = []
        cons = []

        if pd.notna(dma200):
            if close_price > dma200:
                pros.append("Trading above 200-Day Moving Average (Long-term Uptrend)")
            else:
                cons.append("Trading below 200-Day Moving Average (Long-term Downtrend)")

        if pd.notna(dma50):
            if close_price > dma50:
                pros.append("Trading above 50-Day Moving Average (Short-term Strength)")
            else:
                cons.append("Trading below 50-Day Moving Average (Short-term Weakness)")

        if pd.notna(rsi):
            if rsi > 70:
                cons.append(f"RSI indicates stock is Overbought ({round(rsi, 1)})")
            elif rsi < 30:
                pros.append(f"RSI indicates stock is Oversold ({round(rsi, 1)})")
            else:
                pros.append(f"RSI is in neutral healthy territory ({round(rsi, 1)})")

        return jsonify({
            "fundamentals": fundamentals,
            "chart_data": chart_data,
            "pros": pros,
            "cons": cons
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stock_bp.route('/technical-analysis', methods=['GET'])
def get_technical_analysis():
    """Full Citadel-style technical analysis breakdown for a given ticker."""
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({"error": "Ticker parameter is required"}), 400

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        hist = stock.history(period="1y", interval="1d")
        if hist.empty:
            return jsonify({"error": f"No historical data found for {ticker}"}), 404

        if isinstance(hist.columns, pd.MultiIndex):
            try:
                hist.columns = hist.columns.droplevel('Ticker')
            except KeyError:
                hist.columns = hist.columns.droplevel(1)

        df = hist.copy()
        close = df['Close']
        latest_close = float(close.iloc[-1])

        # --- Moving Averages ---
        ma_periods = [5, 20, 50, 100, 200]
        ma_values = {}
        ma_signals = {}
        for p in ma_periods:
            ma = close.rolling(window=p).mean()
            val = float(ma.iloc[-1]) if pd.notna(ma.iloc[-1]) else None
            ma_values[f"MA_{p}"] = round(val, 2) if val else None
            if val:
                if latest_close > val:
                    ma_signals[f"MA_{p}"] = "bullish"
                elif latest_close < val * 0.98:
                    ma_signals[f"MA_{p}"] = "bearish"
                else:
                    ma_signals[f"MA_{p}"] = "neutral"
            else:
                ma_signals[f"MA_{p}"] = "insufficient_data"

        # --- RSI ---
        rsi_series = ta.momentum.RSIIndicator(close=close, window=14).rsi()
        rsi_val = float(rsi_series.iloc[-1]) if pd.notna(rsi_series.iloc[-1]) else None

        rsi_interpretation = "Neutral — balanced momentum"
        if rsi_val:
            if rsi_val > 70:
                rsi_interpretation = "Overbought — potential pullback risk"
            elif rsi_val > 60:
                rsi_interpretation = "Bullish momentum — room to run"
            elif rsi_val < 30:
                rsi_interpretation = "Oversold — potential bounce opportunity"
            elif rsi_val < 40:
                rsi_interpretation = "Weak momentum — buyers cautious"
            else:
                rsi_interpretation = "Neutral — balanced momentum"

        # --- MACD ---
        macd_indicator = ta.trend.MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
        macd_line = float(macd_indicator.macd().iloc[-1]) if pd.notna(macd_indicator.macd().iloc[-1]) else None
        macd_signal_line = float(macd_indicator.macd_signal().iloc[-1]) if pd.notna(macd_indicator.macd_signal().iloc[-1]) else None
        macd_hist = float(macd_indicator.macd_diff().iloc[-1]) if pd.notna(macd_indicator.macd_diff().iloc[-1]) else None

        macd_cross = "neutral"
        macd_interpretation = "Neutral"
        if macd_line is not None and macd_signal_line is not None:
            if macd_line > macd_signal_line:
                macd_cross = "bullish"
                macd_interpretation = "Buy (Bullish crossover active)"
            else:
                macd_cross = "bearish"
                macd_interpretation = "Sell (Bearish crossover active)"

        hist_direction = "narrowing"
        if macd_hist is not None:
            prev_hist = macd_indicator.macd_diff().iloc[-2] if len(macd_indicator.macd_diff()) > 1 else 0
            if abs(macd_hist) > abs(prev_hist):
                hist_direction = "widening"

        # --- Bollinger Bands ---
        bollinger = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
        bb_upper = float(bollinger.bollinger_hband().iloc[-1]) if pd.notna(bollinger.bollinger_hband().iloc[-1]) else None
        bb_middle = float(bollinger.bollinger_mavg().iloc[-1]) if pd.notna(bollinger.bollinger_mavg().iloc[-1]) else None
        bb_lower = float(bollinger.bollinger_lband().iloc[-1]) if pd.notna(bollinger.bollinger_lband().iloc[-1]) else None

        bb_position = "mid-band"
        bb_interpretation = "Consolidating near middle band"
        if bb_upper and bb_lower and bb_middle:
            bb_width = (bb_upper - bb_lower) / bb_middle * 100
            if latest_close > bb_upper * 0.98:
                bb_position = "near_upper"
                bb_interpretation = "Near upper band — potential overbought"
            elif latest_close < bb_lower * 1.02:
                bb_position = "near_lower"
                bb_interpretation = "Near lower band — potential oversold"
            else:
                bb_interpretation = f"Mid-band equilibrium — bandwidth {bb_width:.1f}%"

        # --- Volume Analysis ---
        vol = df['Volume']
        avg_vol_20 = float(vol.rolling(20).mean().iloc[-1]) if pd.notna(vol.rolling(20).mean().iloc[-1]) else None
        curr_vol = float(vol.iloc[-1])

        vol_trend = "average"
        vol_interpretation = "Average volume"
        if avg_vol_20 and avg_vol_20 > 0:
            vol_ratio = curr_vol / avg_vol_20
            if vol_ratio > 1.5:
                vol_trend = "high"
                vol_interpretation = "Unusually high volume — conviction move"
            elif vol_ratio < 0.5:
                vol_trend = "low"
                vol_interpretation = "Low volume — lack of conviction"
            else:
                vol_interpretation = f"Normal trading volume ({vol_ratio:.1f}x avg)"

        # Check if sellers are fading (volume declining on red days)
        recent = df.tail(5)
        red_days = recent[recent['Close'] < recent['Open']]
        sellers_fading = len(red_days) <= 2

        # --- 52W Range & Fibonacci ---
        w52_high = float(info.get('fiftyTwoWeekHigh', close.max()))
        w52_low = float(info.get('fiftyTwoWeekLow', close.min()))
        fib_range = w52_high - w52_low

        fib_levels = {
            "0.0": round(w52_low, 2),
            "23.6": round(w52_low + fib_range * 0.236, 2),
            "38.2": round(w52_low + fib_range * 0.382, 2),
            "50.0": round(w52_low + fib_range * 0.500, 2),
            "61.8": round(w52_low + fib_range * 0.618, 2),
            "100.0": round(w52_high, 2)
        }

        # Where does current price sit in the Fib retracement?
        fib_position = 0
        if fib_range > 0:
            fib_position = round(((latest_close - w52_low) / fib_range) * 100, 1)

        # --- Trend Direction ---
        dma50_val = ma_values.get("MA_50")
        dma200_val = ma_values.get("MA_200")
        dma20_val = ma_values.get("MA_20")

        # Daily trend
        daily_trend = "Sideways"
        if dma20_val:
            if latest_close > dma20_val * 1.01:
                daily_trend = "Bullish — trading above 20 DMA"
            elif latest_close < dma20_val * 0.99:
                daily_trend = "Bearish — trading below 20 DMA"
            else:
                daily_trend = "Sideways / Consolidating"

        # Weekly trend (use 50 DMA as proxy)
        weekly_trend = "Sideways"
        if dma50_val:
            if latest_close > dma50_val * 1.02:
                weekly_trend = "Bullish — sustained above 50 DMA"
            elif latest_close < dma50_val * 0.98:
                weekly_trend = "Bearish — below 50 DMA"
            else:
                weekly_trend = "Base-building near 50 DMA"

        # Monthly trend (use 200 DMA as proxy)
        monthly_trend = "Sideways"
        if dma200_val:
            if latest_close > dma200_val * 1.05:
                monthly_trend = "Bullish — structural uptrend intact"
            elif latest_close < dma200_val * 0.95:
                monthly_trend = "Bearish — long-term downtrend"
            else:
                monthly_trend = "Mildly Bullish — near 200 DMA"

        # --- Support / Resistance ---
        support_1 = dma50_val or fib_levels.get("38.2")
        support_2 = dma200_val or fib_levels.get("23.6")
        resistance_1 = round(w52_high * 0.98, 2) if w52_high else None

        # --- Signal Scorecard ---
        def score(signal):
            if signal in ("bullish", "near_lower", "high"):
                return "bullish"
            elif signal in ("bearish", "near_upper", "low"):
                return "bearish"
            return "neutral"

        # Calculate daily change
        prev_close = float(info.get('previousClose', close.iloc[-2] if len(close) > 1 else latest_close))
        daily_change = round(latest_close - prev_close, 2)
        daily_change_pct = round((daily_change / prev_close) * 100, 2) if prev_close else 0

        # Calculate 1Y return
        first_close = float(close.iloc[0])
        one_year_return = round(((latest_close - first_close) / first_close) * 100, 2) if first_close else 0

        return jsonify({
            "ticker": ticker,
            "name": info.get('shortName', ticker),
            "sector": info.get('sector', 'N/A'),
            "date": datetime.now().strftime('%d %b %Y'),
            "price": round(latest_close, 2),
            "daily_change": daily_change,
            "daily_change_pct": daily_change_pct,
            "w52_high": round(w52_high, 2),
            "w52_low": round(w52_low, 2),

            "trend": {
                "daily": daily_trend,
                "weekly": weekly_trend,
                "monthly": monthly_trend,
                "one_year_return": one_year_return
            },

            "support_resistance": {
                "strong_resistance": f"₹{round(w52_high, 2)} (52W High)",
                "resistance": f"₹{resistance_1}" if resistance_1 else "N/A",
                "support_1": f"₹{round(support_1, 2)}" if support_1 else "N/A",
                "support_2": f"₹{round(support_2, 2)}" if support_2 else "N/A",
                "strong_support": f"₹{round(w52_low, 2)} (52W Low)"
            },

            "moving_averages": {
                "values": ma_values,
                "signals": ma_signals
            },

            "rsi": {
                "value": round(rsi_val, 1) if rsi_val else None,
                "interpretation": rsi_interpretation
            },

            "macd": {
                "line": round(macd_line, 2) if macd_line else None,
                "signal": round(macd_signal_line, 2) if macd_signal_line else None,
                "histogram": round(macd_hist, 2) if macd_hist else None,
                "cross": macd_cross,
                "interpretation": macd_interpretation,
                "hist_direction": hist_direction
            },

            "bollinger": {
                "upper": round(bb_upper, 2) if bb_upper else None,
                "middle": round(bb_middle, 2) if bb_middle else None,
                "lower": round(bb_lower, 2) if bb_lower else None,
                "position": bb_position,
                "interpretation": bb_interpretation
            },

            "volume": {
                "current": int(curr_vol),
                "avg_20": int(avg_vol_20) if avg_vol_20 else None,
                "trend": vol_trend,
                "interpretation": vol_interpretation,
                "sellers_fading": sellers_fading
            },

            "fibonacci": {
                "levels": fib_levels,
                "current_position": fib_position
            },

            "scorecard": {
                "trend": score(ma_signals.get("MA_50", "neutral")),
                "rsi": "bullish" if (rsi_val and 40 < rsi_val < 65) else ("bearish" if (rsi_val and rsi_val > 70) else "neutral"),
                "macd": macd_cross,
                "ma_stack": "bullish" if (dma50_val and dma200_val and dma50_val > dma200_val) else ("bearish" if (dma50_val and dma200_val and dma50_val < dma200_val) else "neutral"),
                "bollinger": score(bb_position),
                "volume": "bullish" if sellers_fading else "neutral",
                "fibonacci": "bullish" if fib_position > 60 else ("bearish" if fib_position < 30 else "neutral"),
                "pattern": "neutral"
            },

            **_compute_confidence_and_trade_plan(
                latest_close, w52_high, w52_low, fib_levels, fib_position,
                ma_values, ma_signals, macd_cross, rsi_val, sellers_fading,
                bb_position, dma50_val, dma200_val, support_1, support_2,
                resistance_1, avg_vol_20,
                score, ma_signals
            )
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
