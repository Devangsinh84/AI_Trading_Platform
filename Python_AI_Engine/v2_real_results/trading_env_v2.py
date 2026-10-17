"""
Corrected trading environment.

Action 0 = hold cash, action 1 = hold the S&P 500 index (from today's close to tomorrow's close).
Reward = the real portfolio return for that day, minus a transaction cost whenever the
position changes. Gains and losses are treated symmetrically.
"""
import gymnasium as gym
import numpy as np
from gymnasium import spaces

from common import FEATURES, TRANSACTION_COST

REWARD_SCALE = 100.0   # 1% daily return -> reward of 1.0 (keeps PPO's numbers in a good range)


class TradingEnvV2(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, df, cost=TRANSACTION_COST):
        super().__init__()
        self.X = df[FEATURES].to_numpy(dtype=np.float32)
        self.next_ret = df["Next_Ret"].to_numpy(dtype=np.float64)
        self.cost = cost
        self.action_space = spaces.Discrete(2)
        # features + current position
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf,
                                            shape=(len(FEATURES) + 1,), dtype=np.float32)

    def _obs(self):
        return np.append(self.X[self.t], np.float32(self.position)).astype(np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.t = 0
        self.position = 0
        self.net_worth = 10_000.0
        return self._obs(), {}

    def step(self, action):
        action = int(action)
        trade_cost = self.cost * abs(action - self.position)
        day_return = action * self.next_ret[self.t]
        portfolio_return = (1 - trade_cost) * (1 + day_return) - 1

        self.net_worth *= (1 + portfolio_return)
        self.position = action
        self.t += 1
        terminated = self.t >= len(self.X) - 1

        reward = float(portfolio_return * REWARD_SCALE)
        info = {"net_worth": self.net_worth, "position": self.position}
        return self._obs(), reward, terminated, False, info
