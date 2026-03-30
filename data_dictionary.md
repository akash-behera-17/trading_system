# Data Dictionary: Neuro-Symbolic Trading System

This document outlines the data elements, flows, stores, and structures used in the Level 0 and Level 1 Data Flow Diagrams (DFDs) of the stock price direction prediction project.

---

## 1. External Entities
Entities outside the boundaries of the system that supply or consume data.

- **User / Trader**: The person or client application running `predict.py` or the web app, supplying a stock ticker symbol to analyze.
- **Yahoo Finance API**: The external financial source providing real-time and historical stock market data (OHLCV).

---

## 2. Processes (Level 1 & Level 2)
Actionable components of the system that transform inputs into outputs.

### Level 1 Processes
- **1.0 Fetch Market Data**: Connects to the Yahoo Finance API, downloading the requested ticker's daily records over a 5-10 year period.
- **2.0 Calculate Technical Indicators**: Parses raw price data and computes structural financial metrics using `pandas` and `ta` libraries.
- **3.0 Evaluate Trading Rules**: Feeds the indicators into the deterministic Mahesh Kaushik Strategy engine to classify the market state and return an initial signal.
- **4.0 Filter Anomalies (LSTM-Autoencoder)**: If Process 3.0 suggests a "Buy," this deep learning model measures the input data's structural similarity against historically successful setups (computing Mean Squared Error).
- **5.0 Generate Final Prediction**: Aggregates rule-based outcomes and neural network veto logic into a final, actionable user recommendation.

### Level 2 Processes (Process 2.0 Breakdown)
- **2.1 Compute Moving Averages**: Calculates 50, 100, and 200-day SMAs from closing prices.
- **2.2 Compute Momentum Oscillators**: Calculates 14-day RSI and MACD specific values from OHLC inputs.
- **2.3 Compute Volume Metrics**: Derives daily percentage change in volume.
- **2.4 Format Data For Engine**: Merges computed metrics into a standardized DataFrame structure, handling NaN values and date alignment.

### Level 2 Processes (Process 3.0 Breakdown)
- **3.1 Check Zone Conditions**: Applies logical constraints (e.g., Close > 50 DMA > 100 DMA > 200 DMA) to determine Bullish, Bearish, or Unconfirmed zones.
- **3.2 Generate Rule Signal**: Decides preliminary action (Rule_Buy, Rule_Sell, Wait) based on the computed Market Zone.

### Level 2 Processes (Process 4.0 Breakdown)
- **4.1 Scale & Format Sequence**: Applies `StandardScaler` to inputs and shapes them into PyTorch tensors (Sequence length = 1).
- **4.2 LSTM-Autoencoder Forward Pass**: Pushes tensor data through the trained Encoder-Decoder PyTorch architecture.
- **4.3 Calculate Reconstruction Error**: Measures the Mean Squared Error (MSE) between the original input array and the reconstructed output array.
- **4.4 Apply Threshold Logic**: Compares the MSE against the anomaly threshold (e.g., 70th percentile). If MSE > Threshold, it flags the sequence as an anomaly (True).

---

## 3. Data Stores
Repositories where the system holds data for persistent or temporary reference.

- **D1. Raw Price Data**: DataFrame storing unmanipulated daily metrics (Date, Open, High, Low, Close, Volume).
- **D2. Technical Features**: DataFrame storing calculated indicators alongside standard prices, heavily used by downstream decision engines.
- **D3. Trained Model**: The PyTorch model parameters (`autoencoder.pth`) storing the trained weights and biases of the LSTM architecture.

---

## 4. Data Flows
Channels through which data travels between entities, processes, and stores.

| Flow Name | Origin -> Destination | Description |
| :--- | :--- | :--- |
| **Ticker Symbol** | User -> 1.0 (Fetch) | The stock string identifier (e.g., `RELIANCE.NS`). |
| **API Request** | 1.0 (Fetch) -> YF API | HTTP GET request for the specific ticker's history. |
| **Historical OHLCV Data** | YF API -> 1.0 (Fetch) | JSON/CSV structured daily price responses. |
| **Raw Data** | 1.0 -> D1 -> 2.0 | Formatted Pandas DataFrame holding core price variables. |
| **Indicators** | 2.0 -> D2 | Computed technical markers added to the dates. |
| **Consolidated Features** | 2.4 -> D2 | Formatted feature set ready for models. |
| **Current Day Indicators** | D2 -> 3.1 | Single row slice sent to rule logic. |
| **Market Zone** | 3.1 -> 3.2 | Identified state (Bullish/Bearish). |
| **Initial Signal** | 3.2 -> 5.0 (Generate) | Decision such as `Rule_Buy`, `Rule_Sell`, or `Wait`. |
| **Sequence Trigger** | 3.2 -> 4.1 | Activates NN prep if `Rule_Buy` is detected. |
| **T-n Seq Features** | D2 -> 4.1 | Historical window (currently 1 day, mapped to shape (1,7)). |
| **Tensor Data** | 4.1 -> 4.2 | Scaled PyTorch formatted inputs (`X_tensor`). |
| **Model Weights** | D3 -> 4.2 | Loaded PyTorch model architecture. |
| **Reconstructed Output** | 4.2 -> 4.3 | Model's attempt to recreate the input. |
| **Original Input** | 4.1 -> 4.3 | Passed straight to MSE function for comparison. |
| **MSE Value** | 4.3 -> 4.4 | Computed Reconstruction Error. |
| **Anomaly Boolean** | 4.4 -> 5.0 (Generate) | True if MSE > Threshold (Trap), False if safe. |
| **Final Decision** | 5.0 -> User | Ultimate system output (e.g., `STRONG BUY`). |

---

## 5. Data Elements (Fields)
Detailed composition of the data structures passing through the system.

### D1. Raw Price Elements (`StockData`)
- `Date` [Date]: Trading day string formatting (YYYY-MM-DD).
- `Open` [Float]: The starting price of the stock on a given date.
- `High` [Float]: The highest price reached during the day.
- `Low` [Float]: The lowest price reached during the day.
- `Close` [Float]: The final settled price at the end of the day.
- `Volume` [Integer]: Total number of shares traded.

### D2. Technical Feature Elements (`TechnicalIndicators`)
- `DMA_50` [Float]: 50-Day moving average of the `Close` price.
- `DMA_100` [Float]: 100-Day moving average of the `Close` price.
- `DMA_200` [Float]: 200-Day moving average of the `Close` price.
- `RSI` [Float]: Relative Strength Index over a 14-day window (0 to 100).
- `MACD` [Float]: The Moving Average Convergence Divergence line.
- `MACD_Signal` [Float]: The 9-day EMA of the MACD.
- `Volume_Change` [Float]: Percentage change in `Volume` compared to the prior day.

### Evaluative Data Elements
- `MarketZone` [String]: Result domain -> `['Bullish', 'Bearish', 'Unconfirmed']`
- `InitialSignal` [String]: Result domain -> `['Rule_Buy', 'Rule_Sell', 'Wait']`
- `ReconstructionError` [Float]: MSE indicating anomalous structure (e.g., `4.6290`).
- `FinalAction` [String]: Formatted UI output (e.g., `STRONG BUY`, `AVOID (Bull Trap)`).
