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
        # x is (batch, seq_len, n_features)
        encoded_out, (hidden_n, cell_n) = self.encoder(x)
        
        # We use the final hidden state to recreate the sequence
        # hidden_n is (num_layers, batch, hidden_size)
        hidden_n = hidden_n.squeeze(0).unsqueeze(1) # (batch, 1, hidden_size)
        
        # Repeat the hidden state for each time step in the sequence
        hidden_n_repeated = hidden_n.repeat(1, self.seq_len, 1) # (batch, seq_len, hidden_size)

        decoded_out, _ = self.decoder(hidden_n_repeated)
        return decoded_out

def build_and_train_model(input_path: str = "data/rule_signals.csv", model_dir: str = "models/") -> None:
    """
    Trains an LSTM-Autoencoder exclusively on historical 'Successful' Buy setups.
    """
    if not os.path.exists(input_path):
        print(f"Error: Rule signals data not found at {input_path}")
        return

    print("Loading data to isolate successful setups...")
    df = pd.read_csv(input_path, index_col=0, parse_dates=True)
    
    # --- Step 1: Filter for Success ---
    # We want to find times where Rule_Signal == 1 AND the price popped up by 5% in the next 10 days
    df['Max_Next_10_Days'] = df['Close'].rolling(window=10).max().shift(-10)
    
    # Identify successful setups
    successful_setups = df[(df['Rule_Signal'] == 1) & (df['Max_Next_10_Days'] >= df['Close'] * 1.05)].copy()
    
    print(f"Total potential buys (signals=1): {len(df[df['Rule_Signal'] == 1])}")
    print(f"Total SUCCESSFUL setups to train Autoencoder: {len(successful_setups)}")
    
    if len(successful_setups) == 0:
        print("Warning: No successful setups found! Relaxing constraint to train a baseline autoencoder.")
        # Fallback: train on all buy signals if no strict 5% winners
        successful_setups = df[df['Rule_Signal'] == 1].copy()
        print(f"Fallback training on {len(successful_setups)} setup instances.")

    # Drop lookahead columns to AVOID DATA LEAKAGE for future predictions
    df.drop(columns=['Max_Next_10_Days'], inplace=True, errors='ignore')
    successful_setups.drop(columns=['Max_Next_10_Days'], inplace=True, errors='ignore')
    
    # --- Step 2: Data Prep ---
    features = ['DMA_50', 'DMA_100', 'DMA_200', 'RSI_14', 'MACD', 'MACD_signal', 'Volume_Change_Pct']
    X_train = successful_setups[features].values
    
    if len(X_train) == 0:
        print("Not enough data to train. Exiting.")
        return

    # Scale data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Reshape for LSTM: (samples, timesteps=1, features)
    # Note: To fully leverage LSTMs, we would typically use a sequence of previous days.
    # However, to map purely feature-by-feature right now as defined by the user context, we use a single timestep. 
    # This prevents total system refactoring but still utilizes the LSTM structure.
    X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32).unsqueeze(1) 
    
    dataset = TensorDataset(X_train_tensor, X_train_tensor)
    data_loader = DataLoader(dataset, batch_size=min(16, len(X_train_tensor)), shuffle=True)
    
    # --- Step 3: Train LSTM-Autoencoder ---
    print("\nInitializing LSTM-Autoencoder...")
    # seq_len=1, n_features=7
    model = LSTMAutoencoder(seq_len=1, n_features=len(features), embedding_dim=4)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    epochs = 100
    print(f"Training on {len(X_train_tensor)} valid samples for {epochs} epochs...")
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
    
    # Save Scaler
    scaler_path = os.path.join(model_dir, "scaler.pkl")
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
        
    # Save Model
    model_path = os.path.join(model_dir, "lstm_autoencoder.pt")
    torch.save(model.state_dict(), model_path)
    
    print(f"\nSaved scaling parameters to {scaler_path}")
    print(f"Saved PyTorch LSTM-Autoencoder weights to {model_path}")

if __name__ == "__main__":
    build_and_train_model()
