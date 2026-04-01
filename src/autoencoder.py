import pandas as pd
import numpy as np
import os
import pickle
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler

class LSTMAutoencoder(nn.Module):
    def __init__(self, seq_len, n_features, embedding_dim=16):
        super(LSTMAutoencoder, self).__init__()
        self.seq_len = seq_len
        self.n_features = n_features
        self.embedding_dim = embedding_dim

        # Encoder
        self.encoder = nn.LSTM(
            input_size=n_features,
            hidden_size=embedding_dim,
            num_layers=1,
            batch_first=True
        )

        # Decoder
        self.decoder = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=n_features,
            num_layers=1,
            batch_first=True
        )

    def forward(self, x):
        encoded_out, (hidden_n, cell_n) = self.encoder(x)
        hidden_n = hidden_n.squeeze(0).unsqueeze(1) # (batch, 1, hidden_size)
        hidden_n_repeated = hidden_n.repeat(1, self.seq_len, 1) # (batch, seq_len, hidden_size)
        decoded_out, _ = self.decoder(hidden_n_repeated)
        return decoded_out

def create_sequences(data, seq_len):
    """
    Creates overlapping sequences of length seq_len from a 2D numpy array.
    """
    xs = []
    for i in range(len(data) - seq_len + 1):
        xs.append(data[i:(i + seq_len)])
    return np.array(xs)

def build_and_train_model(input_path: str = "data/rule_signals.csv", model_dir: str = "models/", seq_len: int = 10) -> None:
    """
    Trains an LSTM-Autoencoder exclusively on historical 'Successful' Buy setups with a sliding window.
    """
    if not os.path.exists(input_path):
        print(f"Error: Rule signals data not found at {input_path}")
        return

    print("Loading data to isolate successful setups...")
    df = pd.read_csv(input_path, index_col=0, parse_dates=True)
    
    # Ensure there are no NaNs in important feature columns
    # We might have NaNs due to rolling 252 for 52W High/Low
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    # --- Step 1: Filter for Success ---
    # We want a 5% pop in 10 days, but NOT a 3% crash.
    df['Max_Next_10_Days'] = df['Close'].rolling(window=10).max().shift(-10)
    df['Min_Next_10_Days'] = df['Close'].rolling(window=10).min().shift(-10)
    
    # Identify completely valid setups (success)
    success_condition = (df['Rule_Signal'] == 1) & (df['Max_Next_10_Days'] >= df['Close'] * 1.05) & (df['Min_Next_10_Days'] > df['Close'] * 0.97)
    df['Is_Success'] = success_condition
    
    # Extract the indices where success occurred
    success_indices = np.where(df['Is_Success'])[0]
    
    print(f"Total potential buys (signals=1): {len(df[df['Rule_Signal'] == 1])}")
    print(f"Total STRICT SUCCESSFUL setups to train Autoencoder: {len(success_indices)}")
    
    features = [
        'DMA_20', 'DMA_50', 'DMA_100', 'DMA_200', 
        'RSI_14', 'MACD', 'MACD_signal', 'Volume_Change_Pct',
        'Bollinger_Upper', 'Bollinger_Middle', 'Bollinger_Lower',
        'Distance_to_52W_High', 'Distance_to_52W_Low'
    ]
    
    # Drop lookahead columns 
    df.drop(columns=['Max_Next_10_Days', 'Min_Next_10_Days', 'Is_Success'], inplace=True, errors='ignore')
    
    # --- Step 2: Data Prep & Sequence Generation ---
    X_raw = df[features].values
    
    if len(X_raw) < seq_len:
        print("Not enough data to train. Exiting.")
        return

    # Scale data globally
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    
    # Create all sequences
    # Sequence mapping: sequence at index i ends at index i + seq_len - 1.
    X_sequences = create_sequences(X_scaled, seq_len)
    
    # Filter only the sequences that end on a 'Success' day.
    # If success occurs at df index `idx`, the sequence must end at `idx`.
    # Index in X_sequences corresponding to ending at `idx` is `idx - seq_len + 1`.
    valid_seq_indices = [idx - seq_len + 1 for idx in success_indices if idx >= seq_len - 1]
    
    X_train = X_sequences[valid_seq_indices]
    
    if len(X_train) == 0:
        print("Warning: No strict 10-day successful setups found! Relaxing constraint to train a baseline autoencoder on all Rule=1 signals.")
        all_buys_indices = np.where(df['Rule_Signal'] == 1)[0]
        valid_seq_indices = [idx - seq_len + 1 for idx in all_buys_indices if idx >= seq_len - 1]
        X_train = X_sequences[valid_seq_indices]
        print(f"Fallback training on {len(X_train)} setup instances.")
        
    if len(X_train) == 0:
        print("Still no data. Cannot train. Exiting.")
        return

    print(f"Training shapes: {X_train.shape} -> (batch, {seq_len}, {len(features)})")

    X_train_tensor = torch.tensor(X_train, dtype=torch.float32) 
    
    dataset = TensorDataset(X_train_tensor, X_train_tensor)
    data_loader = DataLoader(dataset, batch_size=min(16, len(X_train_tensor)), shuffle=True)
    
    # --- Step 3: Train LSTM-Autoencoder ---
    print("\nInitializing LSTM-Autoencoder...")
    model = LSTMAutoencoder(seq_len=seq_len, n_features=len(features), embedding_dim=16)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005)
    
    epochs = 150
    print(f"Training on {len(X_train_tensor)} valid sequences for {epochs} epochs...")
    model.train()
    for __ in range(epochs):
        for inputs, targets in data_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
    print(f"Final training loss (MSE): {loss.item():.4f}")
    
    # --- Step 4: Save Artifacts ---
    os.makedirs(model_dir, exist_ok=True)
    
    scaler_path = os.path.join(model_dir, "scaler.pkl")
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
        
    model_path = os.path.join(model_dir, "lstm_autoencoder.pt")
    torch.save(model.state_dict(), model_path)
    
    print(f"\nSaved scaling parameters to {scaler_path}")
    print(f"Saved PyTorch LSTM-Autoencoder weights to {model_path}")

if __name__ == "__main__":
    build_and_train_model()
