import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
import os

class StockTradingEnv(gym.Env):
    """A Custom Stock Trading Environment for OpenAI Gymnasium"""
    metadata = {'render_modes': ['human']}

    def __init__(self, df, initial_balance=10000):
        super(StockTradingEnv, self).__init__()
        
        # Ensure the index is sequential for step-by-step processing
        self.df = df.reset_index(drop=True) 
        self.initial_balance = initial_balance
        
        # ACTION SPACE:
        # 0 = Go to Cash (Sell all / Hold Cash)
        # 1 = Be Invested (Buy / Hold S&P 500)
        self.action_space = spaces.Discrete(2)
        
        # OBSERVATION SPACE (What the AI sees):
        # The AI sees the 14 columns from your CSV + its current position + its account balance.
        # Total = 16 data points per day.
        self.features = [
            'Close', 'High', 'Low', 'Open', 'Volume', 
            'RSI_14', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9',
            'BBL_20_2.0_2.0', 'BBM_20_2.0_2.0', 'BBU_20_2.0_2.0', 
            'BBB_20_2.0_2.0', 'BBP_20_2.0_2.0'
        ]
        
        # The Box space just means it's an array of continuous numbers
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(len(self.features) + 2,), dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        """Resets the environment back to Day 1 with $10,000"""
        super().reset(seed=seed)
        self.current_step = 0
        self.position = 0          # Start in cash
        self.net_worth = self.initial_balance
        
        return self._next_observation(), {}

    def _next_observation(self):
        """Bundles up today's CSV row and the portfolio data to hand to the AI"""
        frame = self.df.loc[self.current_step, self.features].values
        
        # We divide net_worth by initial_balance to keep the number small (Neural Nets love small numbers)
        obs = np.append(frame, [self.position, self.net_worth / self.initial_balance])
        return obs.astype(np.float32)

    def step(self, action):
        """Executes one day of trading, calculates profit/loss, and moves to tomorrow"""
        current_price = self.df.loc[self.current_step, 'Close']
        
        # Move forward one day in the CSV
        self.current_step += 1
        
        # Check if we reached the end of our historical data
        terminated = self.current_step >= len(self.df) - 1
        
        if not terminated:
            next_price = self.df.loc[self.current_step, 'Close']
            
            # FIX: Because our data is scaled between 0 and 1, division causes extreme % swings.
            # We use the raw difference to calculate a stable, simulated return.
            price_diff = next_price - current_price
            
            # We multiply by 0.5 to keep the daily simulated swings realistic for the portfolio
            market_return = price_diff * 0.5 
        else:
            market_return = 0

         # ==========================================
        # REWARD FUNCTION (The "Asymmetric Risk" Logic)
        # ==========================================
        reward = 0
        if action == 1: # Invested
            if market_return > 0:
                # Big reward for catching an up-trend
                reward = market_return * 100 
            else:
                # Mild penalty for holding during a drop (don't traumatize the AI)
                reward = market_return * 50 
            
            self.net_worth = self.net_worth * (1 + market_return)
        else: # Cash
            # Opportunity cost (Inflation). Slowly bleeds the AI to force it to trade.
            reward = -0.05

        # FATAL ERROR CHECK
        if self.net_worth <= self.initial_balance * 0.1:
            terminated = True
            reward = -100 

        self.position = action


        obs = self._next_observation()
        info = {"net_worth": self.net_worth, "position": self.position}
        
        return obs, reward, terminated, False, info

# ==========================================
# Execution Block: Let's test the environment!
# ==========================================
if __name__ == "__main__":
    print("[*] Loading historical S&P 500 Data...")
    df = pd.read_csv("data/SP500_train.csv")
    
    print("[*] Booting up the Gym Trading Environment...")
    env = StockTradingEnv(df)
    obs, info = env.reset()
    
    print("[+] Environment successfully initialized.")
    print(f"    Starting Portfolio Value: ${info.get('net_worth', 10000)}")
    print(f"    Observation Space Shape: {env.observation_space.shape}")
    print(f"    Action Space: {env.action_space}")
    
    # Run a quick 5-day dummy simulation where the AI always chooses '1' (Buy)
    print("\n[*] Running 5-day dummy simulation (Action: Always Buy)...")
    for i in range(5):
        action = 1 
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"    Day {i+1}: Action={action}, Reward={reward:.4f}, Net Worth=${info['net_worth']:.2f}")