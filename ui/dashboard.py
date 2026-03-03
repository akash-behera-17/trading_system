import streamlit as st
import requests
import pandas as pd
import datetime

# --- Configuration ---
API_URL = "http://localhost:5000/predict"

st.set_page_config(
    page_title="Neuro-Symbolic Trading Dashboard",
    page_icon="📈",
    layout="wide",
)

# --- Header ---
st.title("📈 Neuro-Symbolic Trading System")
st.markdown("""
This dashboard interfaces with the hybrid backend that combines a **Rule-Based Expert System** 
(Moving Average + Price constraints) with an **Unsupervised Deep Learning Filter** (LSTM-Autoencoder) 
to detect and veto Bull Traps.
""")
st.divider()

# --- Inputs ---
st.sidebar.header("Inference Parameters")
ticker = st.sidebar.text_input("Ticker Symbol", value="RELIANCE.NS", help="e.g., AAPL, TSLA, RELIANCE.NS")

# Optional: Adding period for future backend expansion 
# Currently the backend fetches a default 500 days to calculate 200 DMA.
period = st.sidebar.selectbox("Analysis Period", options=["1y", "2y", "5y", "max"], index=0)

if st.sidebar.button("Fetch Prediction", type="primary"):
    with st.spinner(f"Analyzing {ticker}..."):
        try:
            # 1. Ping the Flask API
            payload = {"ticker": ticker, "period": period}
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # --- Metrics Display ---
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Latest Date", data.get("date", "N/A"))
                
                with col2:
                    close_price = data.get("close_price")
                    st.metric("Close Price", f"Rs. {close_price:.2f}" if close_price else "N/A")
                    
                with col3:
                    rule_desc = data.get("rule_description", "N/A")
                    st.metric("Base Rule Signal", rule_desc)
                
                st.divider()
                
                # --- Detailed Analysis ---
                st.subheader("Deep Learning Verification")
                
                if data.get("ml_filtered"):
                    recon_error = data.get("reconstruction_error")
                    is_anomaly = data.get("ml_anomaly")
                    final_rec = data.get("final_recommendation")
                    
                    st.write("The base rule-engine triggered a **Potential Buy**. Passing structural data to the LSTM-Autoencoder...")
                    
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        st.info(f"**Reconstruction Error:** {recon_error:.4f}")
                    
                    with col_dl2:
                        if is_anomaly:
                            st.error(f"**ML Filter Result:** ANOMALY DETECTED (Bull Trap Vetoed)")
                        else:
                            st.success(f"**ML Filter Result:** STRUCTURE VERIFIED")
                    
                    st.markdown("### Final Recommendation")
                    if is_anomaly:
                        st.error(f"🚨 {final_rec}")
                    else:
                        st.success(f"✅ {final_rec}")
                        
                else:
                    st.write("ML verification is only run on 'Potential Buy' signals from the rule engine. Currently, the rule engine is not signaling a buy.")
                    st.markdown("### Final Recommendation")
                    
                    # Display based on current rule
                    if data.get("rule_signal") == -1:
                        st.error(f"🔴 {rule_desc}")
                    else:
                        st.warning(f"🟡 {rule_desc}")
                
            else:
                st.error(f"Backend Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to the Flask API. Please ensure `flask run` is active on port 5000.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
