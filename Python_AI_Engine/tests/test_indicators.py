"""Tests for the feature engineering behind the model inputs."""
import numpy as np

from common import FEATURES, add_indicators


def test_add_indicators_creates_every_model_feature(price_frame):
    out = add_indicators(price_frame)
    missing = [name for name in FEATURES + ["Next_Ret"] if name not in out.columns]
    assert missing == []


def test_add_indicators_does_not_modify_the_input(price_frame):
    before = price_frame.copy()
    add_indicators(price_frame)
    assert price_frame.equals(before)


def test_rsi_stays_between_0_and_100(price_frame):
    rsi = add_indicators(price_frame)["RSI_14"].dropna()
    assert len(rsi) > 0
    assert rsi.between(0, 100).all()


def test_next_return_is_tomorrows_return_with_no_look_ahead_in_features(price_frame):
    out = add_indicators(price_frame)
    close = price_frame["Close"]

    # Next_Ret[t] is what an action taken at day t is paid on: close t -> close t+1
    expected = close.iloc[6] / close.iloc[5] - 1
    assert np.isclose(out["Next_Ret"].iloc[5], expected)
    # ...and today's 1-day return feature only uses information up to day t
    assert np.isclose(out["Ret_1d"].iloc[6], expected)
    # the last day has no tomorrow yet
    assert np.isnan(out["Next_Ret"].iloc[-1])


def test_bollinger_percent_b_for_a_price_oscillating_around_100(price_frame):
    oscillating = price_frame.copy()
    oscillating["Close"] = 100.0 + np.tile([1.0, -1.0], len(oscillating) // 2)
    pct_b = add_indicators(oscillating)["BB_pctB"].dropna()
    # middle band = 100, std = 1, bands = 98..102, so closes of 101 / 99 sit at 75% / 25%
    assert set(np.round(pct_b, 6)) == {0.25, 0.75}


def test_zero_volume_days_do_not_produce_infinite_values(price_frame):
    frame = price_frame.copy()
    frame.iloc[40:45, frame.columns.get_loc("Volume")] = 0.0
    out = add_indicators(frame)
    assert not np.isinf(out[FEATURES].to_numpy(dtype=float)).any()
