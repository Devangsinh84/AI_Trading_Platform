import yfinance as yf
import pandas as pd
import pandas_ta as ta
import os

class DataIngestionEngine:
    def __init__(self, ticker_symbol, start_date, end_date):
        """
        Initializes the Engine with the specific asset we want to pull.
        """
        self.ticker = ticker_symbol
        self.start_date = start_date
        self.end_date = end_date
        os.makedirs("data", exist_ok=True)

    def fetch_data(self):
        """
        Connects to Yahoo Finance and downloads the raw OHLCV data.
        """
        print(f"[*] Fetching data for {self.ticker} from {self.start_date} to {self.end_date}...")
        df = yf.download(self.ticker, start=self.start_date, end=self.end_date)
        
        if df.empty:
            raise ValueError(f"[!] Failed to fetch data. Check symbol or connection.")
            
        # Flatten the MultiIndex columns from the new yfinance update
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        print(f"[+] Successfully downloaded {len(df)} rows of market data.")
        return df

    def engineer_features(self, df):
        """
        Uses pandas-ta to calculate technical indicators for the AI to learn from.
        """
        print("[*] Calculating Technical Indicators (RSI, MACD, Bollinger Bands)...")
        
        # Calculate 14-day RSI
        df.ta.rsi(length=14, append=True)
        # Calculate MACD
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        # Calculate Bollinger Bands
        df.ta.bbands(length=20, append=True)
        
        # Drop any rows that have NaN values
        df.dropna(inplace=True)
        print("[+] Feature engineering complete.")
        return df

    def save_data(self, df, filename):
        """
        Saves the final pristine dataset to a CSV file.
        """
        filepath = os.path.join("data", filename)
        df.to_csv(filepath)
        print(f"[+] Data successfully saved to {filepath}")

# ==========================================
# Execution Block
# ==========================================
if __name__ == "__main__":
    # We use ^GSPC (S&P 500 Index) for our MVP training data.
    engine = DataIngestionEngine(ticker_symbol="^GSPC", start_date="2016-01-01", end_date="2026-01-01")
    
    try:
        raw_data = engine.fetch_data()
        processed_data = engine.engineer_features(raw_data)
        engine.save_data(processed_data, "SP500_10yr_processed.csv")
        
        print("\n[SUCCESS] Task 2.1 Data Ingestion completed flawlessly.")
        
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}")