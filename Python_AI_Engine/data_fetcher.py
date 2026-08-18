import yfinance as yf
import pandas as pd

def get_live_market_data(ticker="AAPL", period="1d", interval="1m"):
    """
    Fetches latest candle data for a given ticker and computes key indicators.
    """
    # FIX: Use yf.Ticker().history() to avoid MultiIndex Series errors
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    
    if data.empty:
        raise ValueError(f"No data retrieved for ticker {ticker}")
        
    # Calculate simple technical indicators for observation space
    data['Returns'] = data['Close'].pct_change()
    
    # Calculate 14-period RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # Calculate MACD (12-period EMA - 26-period EMA)
    ema12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema26 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = ema12 - ema26
    
    # Grab the latest complete snapshot
    latest = data.iloc[-1]
    
    return {
        "ticker": ticker,
        "current_price": float(latest['Close']),
        "rsi": float(latest['RSI']) if not pd.isna(latest['RSI']) else 50.0,
        "macd": float(latest['MACD']) if not pd.isna(latest['MACD']) else 0.0
    }