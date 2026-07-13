import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from stable_baselines3 import PPO
from trading_env import StockTradingEnv

# ==========================================
# Task 3.4: Baseline Comparison (The Showdown)
# ==========================================
if __name__ == "__main__":
    print("[*] Loading Final Exam Data (SP500_test.csv)...")
    df_test = pd.read_csv("data/SP500_test.csv")
    
    # ------------------------------------------
    # STRATEGY 1: The Benchmark (Buy & Hold)
    # ------------------------------------------
    print("[*] Simulating Strategy 1: Buy & Hold Benchmark...")
    # Calculate daily returns of the raw scaled data
    daily_returns = df_test['Close'].diff() * 0.5 
    daily_returns.iloc[0] = 0 # First day return is 0
    
    # Calculate cumulative growth from a $10,000 starting balance
    buy_and_hold_worth = [10000]
    for r in daily_returns[1:]:
        buy_and_hold_worth.append(buy_and_hold_worth[-1] * (1 + r))

    # ------------------------------------------
    # STRATEGY 2: Phase 2 Baseline (XGBoost)
    # ------------------------------------------
    print("[*] Simulating Strategy 2: XGBoost Machine Learning...")
    # We load the model you built in Phase 2
    xgb_model = joblib.load('data/xgboost_baseline.pkl')
    
    # FIX: Feed the model all 14 features it was originally trained on!
    features = [
        'Close', 'High', 'Low', 'Open', 'Volume', 
        'RSI_14', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9',
        'BBL_20_2.0_2.0', 'BBM_20_2.0_2.0', 'BBU_20_2.0_2.0', 
        'BBB_20_2.0_2.0', 'BBP_20_2.0_2.0'
    ]
    X_test = df_test[features]
    
    xgb_predictions = xgb_model.predict(X_test)
    
    xgb_worth = [10000]
    for i in range(1, len(df_test)):
        # The XGBoost prediction from YESTERDAY dictates today's position
        position = xgb_predictions[i-1] 
        r = daily_returns.iloc[i] if position == 1 else 0
        xgb_worth.append(xgb_worth[-1] * (1 + r))

    # ------------------------------------------
    # STRATEGY 3: Phase 3 DRL (PPO Agent)
    # ------------------------------------------
    print("[*] Simulating Strategy 3: Deep Reinforcement Learning (PPO)...")
    env = StockTradingEnv(df_test)
    obs, info = env.reset()
    
    # Load your champion brain
    model = PPO.load("models/ppo_trading_agent")
    
    ppo_worth = [10000]
    terminated = False
    
    while not terminated:
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        ppo_worth.append(info["net_worth"])

    # Make sure all arrays are exactly the same length for plotting
    min_length = min(len(buy_and_hold_worth), len(xgb_worth), len(ppo_worth))
    buy_and_hold_worth = buy_and_hold_worth[:min_length]
    xgb_worth = xgb_worth[:min_length]
    ppo_worth = ppo_worth[:min_length]

    # Calculate Final Returns
    ret_bh = ((buy_and_hold_worth[-1] - 10000) / 10000) * 100
    ret_xgb = ((xgb_worth[-1] - 10000) / 10000) * 100
    ret_ppo = ((ppo_worth[-1] - 10000) / 10000) * 100

    print("\n=============================================")
    print("        FINAL THESIS SHOWDOWN RESULTS        ")
    print("=============================================")
    print(f"Buy & Hold Return : {ret_bh:.2f}%")
    print(f"XGBoost Return    : {ret_xgb:.2f}%")
    print(f"PPO Agent Return  : {ret_ppo:.2f}%")
    print("=============================================")

    # ------------------------------------------
    # Generate the Ultimate Thesis Chart
    # ------------------------------------------
    print("\n[*] Generating Final Comparison Chart...")
    plt.figure(figsize=(12, 7))
    
    plt.plot(buy_and_hold_worth, label=f'Buy & Hold Benchmark ({ret_bh:.2f}%)', color='gray', linestyle='--')
    plt.plot(xgb_worth, label=f'XGBoost Phase 2 ({ret_xgb:.2f}%)', color='orange', linewidth=2)
    plt.plot(ppo_worth, label=f'PPO DRL Phase 3 ({ret_ppo:.2f}%)', color='blue', linewidth=2.5)
    
    plt.title('AI Strategy Showdown: Unseen Test Data Performance')
    plt.xlabel('Trading Days (Test Period)')
    plt.ylabel('Portfolio Value ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    chart_filename = "thesis_showdown_chart.png"
    plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
    print(f"[+] Final chart successfully saved as '{chart_filename}'")