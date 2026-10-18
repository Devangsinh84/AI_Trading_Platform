"""
Shared settings and helpers for the v2 (real results) pipeline.

Fixes compared with the original prototype:
  * Daily returns are real percentage changes of the S&P 500, not differences of scaled prices.
  * The MinMaxScaler is fitted on the TRAINING period only (no look-ahead leakage).
  * Features are stationary (oscillators, ratios, returns, VIX) instead of raw price levels.
  * The VIX index is downloaded so regime behaviour can actually be measured.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data_v2")
MODEL_DIR = os.path.join(HERE, "models_v2")
RESULTS_DIR = os.path.join(HERE, "results_v2")
for _d in (DATA_DIR, MODEL_DIR, RESULTS_DIR):
    os.makedirs(_d, exist_ok=True)

TRAIN_CSV = os.path.join(DATA_DIR, "train_v2.csv")
TEST_CSV = os.path.join(DATA_DIR, "test_v2.csv")

START_DATE = "2016-01-01"
END_DATE = "2026-01-01"
TRAIN_FRACTION = 0.8
TRANSACTION_COST = 0.001        # 0.1% of portfolio value each time the position changes
VIX_REGIME_THRESHOLD = 20.0     # VIX >= 20 is treated as the high-volatility regime
TRADING_DAYS = 252

# Model inputs (all scaled to [0, 1] with a scaler fitted on the training period only)
FEATURES = [
    "RSI_14",          # momentum oscillator
    "MACD_pct",        # MACD line / Close
    "MACDh_pct",       # MACD histogram / Close
    "MACDs_pct",       # MACD signal / Close
    "BB_width",        # Bollinger band width (upper-lower)/middle
    "BB_pctB",         # position of Close inside the Bollinger bands
    "Ret_1d",          # today's return
    "Ret_5d",          # 5-day return
    "Vol_20d",         # 20-day realised volatility
    "Volume_chg",      # log change of volume vs its 20-day mean
    "VIX",             # CBOE volatility index level
]

# Human-readable names used in charts
FEATURE_LABELS = {
    "RSI_14": "RSI (14)", "MACD_pct": "MACD", "MACDh_pct": "MACD histogram",
    "MACDs_pct": "MACD signal", "BB_width": "Bollinger width", "BB_pctB": "Bollinger %B",
    "Ret_1d": "1-day return", "Ret_5d": "5-day return", "Vol_20d": "20-day volatility",
    "Volume_chg": "Volume change", "VIX": "VIX", "Position": "Current position",
}


# ----------------------------------------------------------------------
# Technical indicators (standard definitions, same defaults as pandas-ta)
# ----------------------------------------------------------------------
def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["Close"]

    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["RSI_14"] = 100 - 100 / (1 + gain / loss)

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    df["MACD_pct"] = macd / close
    df["MACDs_pct"] = signal / close
    df["MACDh_pct"] = (macd - signal) / close

    mid = close.rolling(20).mean()
    std = close.rolling(20).std(ddof=0)
    upper, lower = mid + 2 * std, mid - 2 * std
    df["BB_width"] = (upper - lower) / mid
    df["BB_pctB"] = (close - lower) / (upper - lower)

    df["Ret_1d"] = close.pct_change()
    df["Ret_5d"] = close.pct_change(5)
    df["Vol_20d"] = df["Ret_1d"].rolling(20).std()
    # Yahoo reports Volume = 0 on some index days; treat those as missing and carry the last value forward
    volume = df["Volume"].replace(0, np.nan).ffill()
    df["Volume_chg"] = np.log(volume / volume.rolling(20).mean())

    # Return earned by holding the index from today's close to tomorrow's close.
    # This is what an action taken today is paid on.
    df["Next_Ret"] = close.pct_change().shift(-1)

    # Safety net: any division by zero becomes missing, and missing rows are dropped later
    return df.replace([np.inf, -np.inf], np.nan)


# ----------------------------------------------------------------------
# Backtest and metrics
# ----------------------------------------------------------------------
def backtest(positions, next_returns, cost=TRANSACTION_COST, start_value=10_000.0):
    """
    positions[t]    = 1 if invested from day t close to day t+1 close, else 0
    next_returns[t] = real return of the index from day t to day t+1
    Returns the portfolio value series (length len(positions) + 1).
    """
    positions = np.asarray(positions, dtype=float)
    next_returns = np.asarray(next_returns, dtype=float)
    values = [start_value]
    prev = 0.0
    for pos, r in zip(positions, next_returns):
        trade_cost = cost * abs(pos - prev)
        values.append(values[-1] * (1 - trade_cost) * (1 + pos * r))
        prev = pos
    return np.array(values)


def performance_metrics(values, positions):
    values = np.asarray(values, dtype=float)
    daily = values[1:] / values[:-1] - 1
    n_days = len(daily)
    cumulative = values[-1] / values[0] - 1
    annual_return = (1 + cumulative) ** (TRADING_DAYS / n_days) - 1 if n_days > 0 else 0.0
    annual_vol = daily.std(ddof=1) * np.sqrt(TRADING_DAYS) if n_days > 1 else 0.0
    sharpe = (daily.mean() / daily.std(ddof=1)) * np.sqrt(TRADING_DAYS) if daily.std(ddof=1) > 0 else 0.0
    peaks = np.maximum.accumulate(values)
    max_dd = ((peaks - values) / peaks).max()
    positions = np.asarray(positions, dtype=float)
    trades = int(np.abs(np.diff(np.concatenate([[0.0], positions]))).sum())
    return {
        "Cumulative return (%)": round(cumulative * 100, 2),
        "Annualised return (%)": round(annual_return * 100, 2),
        "Annualised volatility (%)": round(annual_vol * 100, 2),
        "Sharpe ratio": round(float(sharpe), 3),
        "Maximum drawdown (%)": round(max_dd * 100, 2),
        "Days invested (%)": round(positions.mean() * 100, 1),
        "Number of trades": trades,
    }


def load_split(path):
    return pd.read_csv(path, index_col="Date", parse_dates=True)
