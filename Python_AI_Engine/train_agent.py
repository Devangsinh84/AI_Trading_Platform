import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback # <-- CRITICAL IMPORT

# Import the custom environment you built in Task 3.1!
from trading_env import StockTradingEnv 

# ==========================================
# Task 3.2: Train the PPO Trading Agent
# ==========================================
if __name__ == "__main__":
    print("[*] Loading historical S&P 500 Data for Training...")
    df = pd.read_csv("data/SP500_train.csv")
    
    print("[*] Initializing the Gym Environment...")
    env = DummyVecEnv([lambda: StockTradingEnv(df)])
    
    print("[*] Booting up PPO (Proximal Policy Optimization) Neural Network...")
    
    # FIX: Added tensorboard_log so the web UI actually gets data!
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003, tensorboard_log="./tensorboard_logs/")
    
    # FIX: Backup the brain every 50,000 steps
    checkpoint_callback = CheckpointCallback(
        save_freq=50000,
        save_path="./models/checkpoints/",
        name_prefix="ppo_model"
    )
    
    print("[*] Beginning Deep Reinforcement Learning Simulation...")
    print("    Note: Running a massive 500,000 timestep production training run.")
    print("    The AI will play the market, make mistakes, and learn from the rewards.\n")
    
    # FIX: Train the AI and pass the callback!
    model.learn(total_timesteps=270000, callback=checkpoint_callback)
    
    print("\n[+] Training Complete!")
    
    # Save the trained brain to the hard drive
    import os
    os.makedirs("models", exist_ok=True)
    MODEL_PATH = "models/ppo_trading_agent"
    model.save(MODEL_PATH)
    
    print(f"[+] AI Agent successfully saved to: {MODEL_PATH}.zip")