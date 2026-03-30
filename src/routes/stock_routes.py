import pandas as pd
import yfinance as yf
import ta
import numpy as np
from flask import Blueprint, request, jsonify

stock_bp = Blueprint('stocks', __name__, url_prefix='/api/stocks')

# A static dictionary of popular NSE/BSE stocks to support the frontend search autocomplete
POPULAR_STOCKS = [
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
    {"ticker": "LARSEN.NS", "name": "Larsen & Toubro Ltd"},
    {"ticker": "ASIANPAINT.NS", "name": "Asian Paints Ltd"},
    {"ticker": "HCLTECH.NS", "name": "HCL Technologies Ltd"},
    {"ticker": "MARUTI.NS", "name": "Maruti Suzuki India Ltd"},
    {"ticker": "AXISBANK.NS", "name": "Axis Bank Ltd"},
    {"ticker": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries Ltd"},
    {"ticker": "TITAN.NS", "name": "Titan Company Ltd"},
    {"ticker": "WIPRO.NS", "name": "Wipro Ltd"},
    {"ticker": "ULTRACEMCO.NS", "name": "UltraTech Cement Ltd"},
    {"ticker": "MM.NS", "name": "Mahindra & Mahindra Ltd"},
    {"ticker": "NESTLEIND.NS", "name": "Nestle India Ltd"},
    {"ticker": "POWERGRID.NS", "name": "Power Grid Corporation of India Ltd"},
    {"ticker": "BAJAJFINSV.NS", "name": "Bajaj Finserv Ltd"},
    {"ticker": "INDUSINDBK.NS", "name": "IndusInd Bank Ltd"}
]

@stock_bp.route('/search', methods=['GET'])
def search_stocks():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify(POPULAR_STOCKS[:10])  # return top 10 if no query

    # Filter stocks where the ticker or name matches the search string
    results = [
        s for s in POPULAR_STOCKS 
        if query in s['ticker'].lower() or query in s['name'].lower()
    ]
    
    return jsonify(results)

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
            "shortName": info.get('shortName', ticker)
        }

        # 2. Historical Data (1 year for DMA200)
        hist = stock.history(period="1y", interval="1d")
        if hist.empty:
            return jsonify({"error": f"No historical data found for {ticker}"}), 404
            
        # Clean multi-index if yf returns one
        if isinstance(hist.columns, pd.MultiIndex):
            try:
                hist.columns = hist.columns.droplevel('Ticker')
            except KeyError:
                hist.columns = hist.columns.droplevel(1)

        # 3. Chart Data Formatting for Recharts
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
