import pandas as pd
import numpy as np
import os
import pickle
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler

class LSTMAutoencoder(nn.Module):
    """
    v2.0: Deeper architecture with 2-layer encoder, larger latent space,
    and dropout for regularization.
    """
    def __init__(self, seq_len, n_features, embedding_dim=32, dropout=0.2):
        super(LSTMAutoencoder, self).__init__()
        self.seq_len = seq_len
        self.n_features = n_features
        self.embedding_dim = embedding_dim

        # Encoder (2-layer for deeper temporal modeling)
        self.encoder = nn.LSTM(
            input_size=n_features,
            hidden_size=embedding_dim,
            num_layers=2,
            batch_first=True,
            dropout=dropout
        )

        # Decoder (2-layer)
        self.decoder = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=n_features,
            num_layers=1,
            batch_first=True
        )

    def forward(self, x):
        encoded_out, (hidden_n, cell_n) = self.encoder(x)
        # Take the last layer's hidden state
        hidden_n = hidden_n[-1].unsqueeze(1)  # (batch, 1, hidden_size)
        hidden_n_repeated = hidden_n.repeat(1, self.seq_len, 1)  # (batch, seq_len, hidden_size)
        decoded_out, _ = self.decoder(hidden_n_repeated)
        return decoded_out


def create_sequences(data, seq_len):
    """Creates overlapping sequences of length seq_len from a 2D numpy array."""
    xs = []
    for i in range(len(data) - seq_len + 1):
        xs.append(data[i:(i + seq_len)])
    return np.array(xs) if xs else np.array([]).reshape(0, seq_len, data.shape[1])


# Feature set used by the autoencoder (original 13 features for compatibility)
AE_FEATURES = [
    'DMA_20', 'DMA_50', 'DMA_100', 'DMA_200',
    'RSI_14', 'MACD', 'MACD_signal', 'Volume_Change_Pct',
    'Bollinger_Upper', 'Bollinger_Middle', 'Bollinger_Lower',
    'Distance_to_52W_High', 'Distance_to_52W_Low'
]


def build_and_train_model(input_path: str = "data/rule_signals.csv", model_dir: str = "models/", seq_len: int = 10) -> None:
    """
    v2.0: Tuned hyperparameters:
    - embedding_dim: 16 -> 32
    - num_layers: 1 -> 2 (encoder)
    - dropout: 0 -> 0.2
    - learning_rate: 0.005 -> 0.001
    - epochs: 150 -> 250
    - batch_size: 32 -> 64
    """
    if not os.path.exists(input_path):
        print(f"Error: Rule signals data not found at {input_path}")
        return

    print("Loading data to isolate successful setups (v2.0 tuned)...")
    df = pd.read_csv(input_path, index_col=0, parse_dates=True)

    if 'Ticker' not in df.columns:
        print("Error: 'Ticker' column not found.")
        return

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    features = AE_FEATURES

    # Fit scaler globally
    print("Fitting global scaler across all tickers...")
    scaler = StandardScaler()
    scaler.fit(df[features].values)

    # Create sequences PER TICKER
    all_train_sequences = []
    total_buys = 0
    total_successes = 0

    for ticker, group in df.groupby('Ticker'):
        group = group.sort_index().copy()

        group['Max_Next_10_Days'] = group['Close'].rolling(window=10).max().shift(-10)
        group['Min_Next_10_Days'] = group['Close'].rolling(window=10).min().shift(-10)

        success_condition = (
            (group['Rule_Signal'] == 1) &
            (group['Max_Next_10_Days'] >= group['Close'] * 1.05) &
            (group['Min_Next_10_Days'] > group['Close'] * 0.97)
        )
        group['Is_Success'] = success_condition

        buy_count = (group['Rule_Signal'] == 1).sum()
        success_indices = np.where(group['Is_Success'].values)[0]
        total_buys += buy_count
        total_successes += len(success_indices)

        if len(success_indices) == 0:
            continue

        X_scaled = scaler.transform(group[features].values)
        X_sequences = create_sequences(X_scaled, seq_len)

        if len(X_sequences) == 0:
            continue

        valid_seq_indices = [idx - seq_len + 1 for idx in success_indices if idx >= seq_len - 1]
        valid_seq_indices = [i for i in valid_seq_indices if 0 <= i < len(X_sequences)]

        if valid_seq_indices:
            all_train_sequences.append(X_sequences[valid_seq_indices])

    print(f"\nTotal Rule-Based Buys across all tickers: {total_buys}")
    print(f"Total STRICT SUCCESSFUL setups for training: {total_successes}")

    if not all_train_sequences:
        print("ERROR: No successful training sequences found. Using fallback.")
        for ticker, group in df.groupby('Ticker'):
            group = group.sort_index()
            buy_indices = np.where(group['Rule_Signal'].values == 1)[0]
            if len(buy_indices) == 0:
                continue
            X_scaled = scaler.transform(group[features].values)
            X_sequences = create_sequences(X_scaled, seq_len)
            if len(X_sequences) == 0:
                continue
            valid = [idx - seq_len + 1 for idx in buy_indices if idx >= seq_len - 1]
            valid = [i for i in valid if 0 <= i < len(X_sequences)]
            if valid:
                all_train_sequences.append(X_sequences[valid])

    if not all_train_sequences:
        print("Still no data. Cannot train. Exiting.")
        return

    X_train = np.concatenate(all_train_sequences, axis=0)
    print(f"\nTraining data shape: {X_train.shape} -> (samples, {seq_len}, {len(features)})")

    # --- TUNED HYPERPARAMETERS ---
    EMBEDDING_DIM = 32
    LEARNING_RATE = 0.001
    EPOCHS = 250
    BATCH_SIZE = min(64, len(X_train))
    DROPOUT = 0.2

    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
    dataset = TensorDataset(X_train_tensor, X_train_tensor)
    data_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    print(f"\nInitializing LSTM-Autoencoder v2.0...")
    print(f"  embedding_dim={EMBEDDING_DIM}, num_layers=2, dropout={DROPOUT}")
    print(f"  lr={LEARNING_RATE}, epochs={EPOCHS}, batch_size={BATCH_SIZE}")

    model = LSTMAutoencoder(seq_len=seq_len, n_features=len(features),
                            embedding_dim=EMBEDDING_DIM, dropout=DROPOUT)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=20, factor=0.5)

    model.train()
    for epoch in range(EPOCHS):
        epoch_loss = 0
        for inputs, targets in data_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        avg_loss = epoch_loss / len(data_loader)
        scheduler.step(avg_loss)

        if (epoch + 1) % 50 == 0:
            print(f"  Epoch {epoch+1}/{EPOCHS} - Loss: {avg_loss:.4f}")

    print(f"Final training loss (MSE): {loss.item():.4f}")

    # Save
    os.makedirs(model_dir, exist_ok=True)
    with open(os.path.join(model_dir, "scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)
    torch.save(model.state_dict(), os.path.join(model_dir, "lstm_autoencoder.pt"))

    # Save hyperparameters for loading
    hp = {'embedding_dim': EMBEDDING_DIM, 'dropout': DROPOUT, 'seq_len': seq_len,
          'n_features': len(features), 'num_layers': 2}
    with open(os.path.join(model_dir, "ae_hyperparams.pkl"), "wb") as f:
        pickle.dump(hp, f)

    print(f"\nSaved all model artifacts to {model_dir}")


if __name__ == "__main__":
    build_and_train_model()
