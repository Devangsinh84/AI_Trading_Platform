"""Tests for the corrected reinforcement learning trading environment (v2)."""
import numpy as np
import pytest

from common import FEATURES, backtest
from trading_env_v2 import REWARD_SCALE, TradingEnvV2


def test_reset_for_evaluation_starts_in_cash_on_day_zero(env_frame):
    env = TradingEnvV2(env_frame)
    obs, info = env.reset(seed=0)

    assert env.t == 0
    assert env.position == 0
    assert env.net_worth == 10_000.0
    assert obs.shape == (len(FEATURES) + 1,)
    assert obs.dtype == np.float32
    assert obs[-1] == 0.0  # last observation value is the current position


def test_observation_space_matches_observations(env_frame):
    env = TradingEnvV2(env_frame)
    obs, _ = env.reset(seed=0)
    assert env.observation_space.contains(obs)
    assert env.action_space.n == 2


def test_step_reward_is_the_scaled_portfolio_return_after_costs(env_frame):
    env = TradingEnvV2(env_frame, cost=0.001)
    env.reset(seed=0)
    r = env_frame["Next_Ret"].iloc[0]

    _, reward, terminated, truncated, info = env.step(1)  # buy

    expected_return = (1 - 0.001) * (1 + r) - 1
    assert reward == pytest.approx(expected_return * REWARD_SCALE)
    assert info["net_worth"] == pytest.approx(10_000.0 * (1 + expected_return))
    assert info["position"] == 1
    assert not terminated and not truncated


def test_staying_in_cash_earns_nothing_and_costs_nothing(env_frame):
    env = TradingEnvV2(env_frame, cost=0.001)
    env.reset(seed=0)
    _, reward, _, _, info = env.step(0)
    assert reward == 0.0
    assert info["net_worth"] == 10_000.0


def test_risk_aversion_penalises_large_moves(env_frame):
    neutral = TradingEnvV2(env_frame, risk_aversion=0.0)
    averse = TradingEnvV2(env_frame, risk_aversion=5.0)
    neutral.reset(seed=0)
    averse.reset(seed=0)

    _, r_neutral, *_ = neutral.step(1)
    _, r_averse, *_ = averse.step(1)
    assert r_averse < r_neutral


def test_evaluation_episode_runs_to_the_end_of_the_data(env_frame):
    env = TradingEnvV2(env_frame)
    env.reset(seed=0)
    steps, terminated = 0, False
    while not terminated:
        _, _, terminated, _, _ = env.step(1)
        steps += 1
    assert steps == len(env_frame) - 1


def test_random_start_episodes_stay_inside_the_data(env_frame):
    env = TradingEnvV2(env_frame, random_start=True, episode_length=10)
    for seed in range(20):
        env.reset(seed=seed)
        assert 0 <= env.t
        assert env.end == env.t + 10
        assert env.end < len(env_frame)
        assert env.position in (0, 1)


def test_environment_and_backtester_agree_on_final_value(env_frame):
    """The RL environment and the backtest used for reporting must compute the same portfolio."""
    rng = np.random.default_rng(11)
    env = TradingEnvV2(env_frame, cost=0.001)
    env.reset(seed=0)

    actions, terminated, info = [], False, {}
    while not terminated:
        action = int(rng.integers(0, 2))
        actions.append(action)
        _, _, terminated, _, info = env.step(action)

    values = backtest(actions, env_frame["Next_Ret"].to_numpy()[: len(actions)], cost=0.001)
    assert info["net_worth"] == pytest.approx(values[-1])
