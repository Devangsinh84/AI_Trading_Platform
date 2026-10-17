"""
STEP 1: Download S&P 500 and VIX data, build features, split 80/20 in time,
and scale with a MinMaxScaler fitted on the training period only.

Run:  python step1_prepare_data.py
Time: about 1 minute (needs internet)
"""
import joblib
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from common import (FEATURES, START_DATE, END_DATE, TRAIN_FRACTION, TRAIN_CSV, TEST_CSV,
                    DATA_DIR, add_indicators)


def download(ticker):
    import yfinance as yf
    df = yf.download(ticker, start=START_DATE, end=END_DATE, auto_adjust=True, progress=False)
    if df.empty:
        raise SystemExit(f"[!] No data for {ticker}. Check your internet connection.")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index.name = "Date"
    return df


def build(spx: pd.DataFrame, vix: pd.DataFrame):
    df = add_indicators(spx[["Open", "High", "Low", "Close", "Volume"]])
    df["VIX"] = vix["Close"].reindex(df.index).ffill()
    df = df.dropna()

    split = int(len(df) * TRAIN_FRACTION)
    train, test = df.iloc[:split].copy(), df.iloc[split:].copy()

    # Fit the scaler on TRAINING data only, then apply it to both periods.
    scaler = MinMaxScaler()
    scaler.fit(train[FEATURES])
    for part in (train, test):
        part["VIX_raw"] = part["VIX"]            # unscaled VIX kept for regime analysis
        part[FEATURES] = scaler.transform(part[FEATURES])
        part["Target"] = (part["Next_Ret"] > 0).astype(int)

    cols = FEATURES + ["Close", "Next_Ret", "VIX_raw", "Target"]
    return train[cols], test[cols], scaler


if __name__ == "__main__":
    print("[*] Downloading S&P 500 (^GSPC) and VIX (^VIX)...")
    spx, vix = download("^GSPC"), download("^VIX")
    train, test, scaler = build(spx, vix)
    train.to_csv(TRAIN_CSV)
    test.to_csv(TEST_CSV)
    joblib.dump(scaler, f"{DATA_DIR}/scaler_v2.pkl")
    print(f"[+] Train: {len(train)} days  {train.index[0].date()} -> {train.index[-1].date()}")
    print(f"[+] Test : {len(test)} days  {test.index[0].date()} -> {test.index[-1].date()}")
    print(f"[+] Saved to {DATA_DIR}")
