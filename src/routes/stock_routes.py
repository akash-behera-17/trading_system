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
