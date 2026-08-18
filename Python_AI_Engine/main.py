from fastapi import FastAPI
import yfinance as yf
import random

app = FastAPI()

@app.get("/predict")
def get_live_prediction():
    # 1. Fetch Live Market Data (S&P 500 ETF)
    ticker = yf.Ticker("ETH-USD")
    # Fetching the latest 1-minute candle
    hist = ticker.history(period="1d", interval="1m")
    
    if hist.empty:
        current_price = 500.00 # Fallback just in case the market is closed or offline
    else:
        current_price = round(hist['Close'].iloc[-1], 2)

    # 2. Live State routing
    # This proves the pipeline works dynamically before you drop in the heavy RL model
    agent_state = "BULL MARKET" if current_price % 2 == 0 else "BEAR MARKET"
    
    # 3. Dynamic SHAP Payload (Ready for React Recharts)
    return {
        "price": current_price,
        "agent": agent_state,
        "shap_values": [
            {"feature": "VIX Volatility", "importance": round(random.uniform(0.6, 0.9), 4)},
            {"feature": "RSI", "importance": round(random.uniform(0.4, 0.7), 4)},
            {"feature": "MACD", "importance": round(random.uniform(0.2, 0.5), 4)},
            {"feature": "Volume", "importance": round(random.uniform(0.05, 0.3), 4)}
        ]
    }