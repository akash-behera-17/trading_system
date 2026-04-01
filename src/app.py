import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import yfinance as yf
import ta
import pickle
import torch
import torch.nn as nn
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# --- Database & Auth Configuration ---
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-prod'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock_ml.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from src.extensions import db, bcrypt
db.init_app(app)
bcrypt.init_app(app)

# Import models so SQLAlchemy knows about them
from src.models.user import User

with app.app_context():
    db.create_all()

# Register Blueprints
from src.routes.auth_routes import auth_bp
from src.routes.stock_routes import stock_bp
app.register_blueprint(auth_bp)
app.register_blueprint(stock_bp)

# --- 1. Model Definitions & Setup ---

class LSTMAutoencoder(nn.Module):
    def __init__(self, seq_len, n_features, embedding_dim=16):
        super(LSTMAutoencoder, self).__init__()
        self.seq_len = seq_len
        self.n_features = n_features
        self.embedding_dim = embedding_dim

        self.encoder = nn.LSTM(input_size=n_features, hidden_size=embedding_dim, num_layers=1, batch_first=True)
        self.decoder = nn.LSTM(input_size=embedding_dim, hidden_size=n_features, num_layers=1, batch_first=True)

    def forward(self, x):
        encoded_out, (hidden_n, cell_n) = self.encoder(x)
        hidden_n = hidden_n.squeeze(0).unsqueeze(1)
        hidden_n_repeated = hidden_n.repeat(1, self.seq_len, 1)
        decoded_out, _ = self.decoder(hidden_n_repeated)
        return decoded_out

# Hardcoded Threshold from Phase 4 evaluation: 0.2928 (70th percentile)
THRESHOLD = 0.2928
FEATURES = [
    'DMA_20', 'DMA_50', 'DMA_100', 'DMA_200', 
    'RSI_14', 'MACD', 'MACD_signal', 'Volume_Change_Pct',
    'Bollinger_Upper', 'Bollinger_Middle', 'Bollinger_Lower',
    'Distance_to_52W_High', 'Distance_to_52W_Low'
]
SEQ_LEN = 10

# Attempt to load models at startup to save time on each request.
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
try:
    with open(os.path.join(MODEL_DIR, "scaler.pkl"), "rb") as f:
        scaler = pickle.load(f)
        
    autoencoder_model = LSTMAutoencoder(seq_len=SEQ_LEN, n_features=len(FEATURES), embedding_dim=16)
    model_path = os.path.join(MODEL_DIR, "lstm_autoencoder.pt")
    autoencoder_model.load_state_dict(torch.load(model_path, weights_only=True))
    autoencoder_model.eval()
    MODEL_LOADED = True
    print("Models loaded successfully.")
except Exception as e:
    print(f"Warning: Could not load ML models on startup. Error: {e}")
    MODEL_LOADED = False

# --- 2. Helper Functions ---

def fetch_recent_data(ticker, days=500):
    """Fetches recent data necessary to calculate up to a 200-Day Moving Average."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)
    
    if data.empty:
        raise ValueError(f"No data fetched for {ticker}. Check symbol.")
        
    # Handle yfinance MultiIndex columns (Price, Ticker)
    if isinstance(data.columns, pd.MultiIndex):
        try:
            data.columns = data.columns.droplevel('Ticker')
        except KeyError:
            data.columns = data.columns.droplevel(1)
    
    if len(data) < 200:
        raise ValueError(f"Not enough data fetched for {ticker} to calculate 200 DMA.")
        
    return data[['Open', 'High', 'Low', 'Close', 'Volume']]

def engineer_features(df):
    """Calculates indicators on the live dataframe."""
    df = df.copy()
    df['DMA_20'] = df['Close'].rolling(window=20).mean()
    df['DMA_50'] = df['Close'].rolling(window=50).mean()
    df['DMA_100'] = df['Close'].rolling(window=100).mean()
    df['DMA_200'] = df['Close'].rolling(window=200).mean()
    
    df['RSI_14'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    
    macd_indicator = ta.trend.MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
    df['MACD'] = macd_indicator.macd()
    df['MACD_signal'] = macd_indicator.macd_signal()
    
    df['Volume_Change_Pct'] = df['Volume'].pct_change() * 100
    
    bollinger = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
    df['Bollinger_Upper'] = bollinger.bollinger_hband()
    df['Bollinger_Middle'] = bollinger.bollinger_mavg()
    df['Bollinger_Lower'] = bollinger.bollinger_lband()

    df['52W_High'] = df['Close'].rolling(window=252).max()
    df['52W_Low'] = df['Close'].rolling(window=252).min()
    
    df['Distance_to_52W_High'] = (df['Close'] - df['52W_High']) / df['52W_High']
    df['Distance_to_52W_Low'] = (df['Close'] - df['52W_Low']) / df['52W_Low']
    
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.dropna()
    
    if len(df) < SEQ_LEN:
        raise ValueError(f"Not enough valid data rows after dropping NaNs to form a {SEQ_LEN}-day sequence.")
        
    return df.iloc[-SEQ_LEN:]

# --- 3. API Endpoints ---

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "model_loaded": MODEL_LOADED})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data or 'ticker' not in data:
        return jsonify({"error": "Please provide a 'ticker' in the JSON body."}), 400
        
    ticker = data['ticker']
    
    try:
        # 1. Fetch & Engineer
        df_raw = fetch_recent_data(ticker)
        latest_10_days = engineer_features(df_raw)
        latest_day = latest_10_days.iloc[-1:]
        
        current_close = float(latest_day['Close'].values[0])
        date_str = latest_day.index[0].strftime('%Y-%m-%d')
        
        # 2. Rule Engine Verification (Opus 4.6 Confluence Logic)
        bull_condition = (
            (latest_day['Close'] > latest_day['DMA_50']).values[0] and
            (latest_day['DMA_50'] > latest_day['DMA_200']).values[0] and
            (latest_day['Close'] > latest_day['DMA_20']).values[0] and
            (latest_day['RSI_14'] > 40).values[0] and (latest_day['RSI_14'] < 70).values[0] and
            (latest_day['MACD'] > latest_day['MACD_signal']).values[0] and
            (latest_day['Close'] <= latest_day['Bollinger_Upper']).values[0] and
            (latest_day['Close'] <= latest_day['DMA_200'] * 1.10).values[0]
        )
        
        bear_condition = (
            (latest_day['Close'] < latest_day['DMA_50']).values[0] and
            (latest_day['DMA_50'] < latest_day['DMA_200']).values[0] and
            (latest_day['Close'] < latest_day['DMA_20']).values[0] and
            (latest_day['RSI_14'] < 60).values[0] and (latest_day['RSI_14'] > 30).values[0] and
            (latest_day['MACD'] < latest_day['MACD_signal']).values[0] and
            (latest_day['Close'] >= latest_day['Bollinger_Lower']).values[0] and
            (latest_day['Close'] >= latest_day['DMA_200'] * 0.90).values[0]
        )
        
        rule_signal = 0
        rule_desc = "WAIT (Unconfirmed Zone)"
        
        if bull_condition: 
            rule_signal = 1
            rule_desc = "POTENTIAL BUY (Bull Zone Detected)"
        elif bear_condition: 
            rule_signal = -1
            rule_desc = "SELL (Bear Zone Detected)"
            
        response_data = {
            "ticker": ticker,
            "date": date_str,
            "close_price": current_close,
            "rule_signal": rule_signal,
            "rule_description": rule_desc,
            "ml_filtered": False,
            "ml_anomaly": False,
            "reconstruction_error": None,
            "final_recommendation": rule_desc
        }
        
        # 3. ML Filter (Only if it's a Potential Buy and models are loaded)
        if rule_signal == 1 and MODEL_LOADED:
            # Extract features and scale (all 10 days)
            X_eval = latest_10_days[FEATURES].values
            X_eval_scaled = scaler.transform(X_eval)
            X_tensor = torch.tensor(X_eval_scaled, dtype=torch.float32).unsqueeze(0)
            
            criterion = nn.MSELoss(reduction='none')
            
            with torch.no_grad():
                reconstructions = autoencoder_model(X_tensor)
                error = criterion(reconstructions, X_tensor).mean().item()
                
            response_data["reconstruction_error"] = float(error)
            response_data["ml_filtered"] = True
            
            if error >= THRESHOLD:
                response_data["ml_anomaly"] = True
                response_data["final_recommendation"] = f"AVOID (BULL TRAP) - Anomaly Error: {error:.4f}"
            else:
                response_data["ml_anomaly"] = False
                response_data["final_recommendation"] = "STRONG BUY - Structure Verified"
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
