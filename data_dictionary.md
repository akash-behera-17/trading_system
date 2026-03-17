# Data Dictionary: Neuro-Symbolic Trading System

This document outlines the data elements, flows, stores, and structures used in the Level 0 and Level 1 Data Flow Diagrams (DFDs) of the stock price direction prediction project.

---

## 1. External Entities
Entities outside the boundaries of the system that supply or consume data.

- **User / Trader**: The person or client application running `predict.py` or the web app, supplying a stock ticker symbol to analyze.
- **Yahoo Finance API**: The external financial source providing real-time and historical stock market data (OHLCV).

---

## 2. Processes (Level 1)
Actionable components of the system that transform inputs into outputs.

- **1.0 Fetch Market Data**: Connects to the Yahoo Finance API, downloading the requested ticker's daily records over a 5-10 year period.
- **2.0 Calculate Technical Indicators**: Parses raw price data and computes structural financial metrics using `pandas` and `ta` libraries.
- **3.0 Evaluate Trading Rules**: Feeds the indicators into the deterministic Mahesh Kaushik Strategy engine to classify the market state and return an initial signal.
- **4.0 Filter Anomalies (LSTM-Autoencoder)**: If Process 3.0 suggests a "Buy," this deep learning model measures the input data's structural similarity against historically successful setups (computing Mean Squared Error).
- **5.0 Generate Final Prediction**: Aggregates rule-based outcomes and neural network veto logic into a final, actionable user recommendation.

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
| **Condition Features** | D2 -> 3.0 (Evaluate) | Current day's values checked by deterministic logic. |
| **Initial Signal** | 3.0 -> 5.0 (Generate) | Decision such as `Rule_Buy`, `Rule_Sell`, or `Wait`. |
| **Sequence Features** | D2 -> 4.0 (Filter) | Standardized array dimensions sent to the LSTM autoencoder. |
| **Model Weights** | D3 -> 4.0 (Filter) | Loaded PyTorch model architecture. |
| **Reconstruction Error** | 4.0 -> 5.0 (Generate) | MSE calculation resulting in an Anomaly `True` (Trap) or `False` (Safe). |
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
