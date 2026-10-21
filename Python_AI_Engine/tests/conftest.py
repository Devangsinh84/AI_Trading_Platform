"""
Shared test setup.

The v2 pipeline modules import each other by plain module name (`from common import ...`),
so the v2 folder is put on the import path here, the same way it is when the scripts run.
"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

V2_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "v2_real_results")
if V2_DIR not in sys.path:
    sys.path.insert(0, V2_DIR)


def make_price_frame(n_days=120, seed=0):
    """Synthetic OHLCV data that looks like a daily index series (no network needed)."""
    rng = np.random.default_rng(seed)
    daily = rng.normal(0.0004, 0.01, n_days)
    close = 3000 * np.cumprod(1 + daily)
    dates = pd.bdate_range("2024-01-01", periods=n_days, name="Date")
    return pd.DataFrame(
        {
            "Open": close * (1 - 0.001),
            "High": close * (1 + 0.005),
            "Low": close * (1 - 0.005),
            "Close": close,
            "Volume": rng.integers(1_000_000, 5_000_000, n_days).astype(float),
            "VIX": rng.uniform(12, 30, n_days),
        },
        index=dates,
    )


@pytest.fixture
def price_frame():
    return make_price_frame()


@pytest.fixture
def env_frame():
    """A small, fully populated feature frame for the trading environment."""
    from common import FEATURES

    n = 30
    rng = np.random.default_rng(1)
    data = {name: rng.uniform(0, 1, n) for name in FEATURES}
    data["Next_Ret"] = rng.normal(0.0005, 0.01, n)
    return pd.DataFrame(data)
