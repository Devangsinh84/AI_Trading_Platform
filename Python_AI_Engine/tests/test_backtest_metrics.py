"""Tests for the backtester and performance metrics used to report the thesis results."""
import numpy as np
import pytest

from common import TRADING_DAYS, backtest, performance_metrics


def test_backtest_always_in_cash_keeps_capital():
    values = backtest(positions=[0, 0, 0], next_returns=[0.05, -0.02, 0.01])
    assert np.allclose(values, 10_000.0)
    assert len(values) == 4


def test_backtest_buy_and_hold_compounds_returns_and_pays_one_entry_cost():
    returns = [0.01, -0.02, 0.03]
    values = backtest(positions=[1, 1, 1], next_returns=returns, cost=0.001)

    expected = 10_000.0 * (1 - 0.001) * np.prod([1 + r for r in returns])
    assert values[-1] == pytest.approx(expected)
    assert len(values) == len(returns) + 1


def test_backtest_charges_cost_on_every_position_change():
    # in -> out -> in = 3 position changes, market flat so only costs move the value
    values = backtest(positions=[1, 0, 1], next_returns=[0.0, 0.0, 0.0], cost=0.01)
    assert values[-1] == pytest.approx(10_000.0 * 0.99 ** 3)


def test_backtest_without_costs_matches_simple_compounding():
    rng = np.random.default_rng(3)
    returns = rng.normal(0, 0.01, 50)
    positions = rng.integers(0, 2, 50)
    values = backtest(positions, returns, cost=0.0)
    assert values[-1] == pytest.approx(10_000.0 * np.prod(1 + positions * returns))


def test_metrics_report_cumulative_return_drawdown_and_trades():
    values = np.array([100.0, 110.0, 99.0, 121.0])
    metrics = performance_metrics(values, positions=[1, 0, 1])

    assert metrics["Cumulative return (%)"] == pytest.approx(21.0)
    # peak 110 -> trough 99 is the worst drop: 10%
    assert metrics["Maximum drawdown (%)"] == pytest.approx(10.0)
    assert metrics["Number of trades"] == 3
    assert metrics["Days invested (%)"] == pytest.approx(66.7)


def test_metrics_sharpe_matches_definition():
    rng = np.random.default_rng(7)
    daily = rng.normal(0.0005, 0.01, 252)
    values = 100 * np.concatenate([[1.0], np.cumprod(1 + daily)])

    metrics = performance_metrics(values, positions=np.ones(252))
    expected = daily.mean() / daily.std(ddof=1) * np.sqrt(TRADING_DAYS)
    assert metrics["Sharpe ratio"] == pytest.approx(expected, abs=1e-3)


def test_metrics_flat_portfolio_has_zero_sharpe_and_no_drawdown():
    metrics = performance_metrics(np.full(10, 100.0), positions=np.zeros(9))
    assert metrics["Sharpe ratio"] == 0.0
    assert metrics["Maximum drawdown (%)"] == 0.0
    assert metrics["Number of trades"] == 0
