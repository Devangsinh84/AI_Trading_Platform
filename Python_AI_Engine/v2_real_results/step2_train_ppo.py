"""
STEP 2: Train the PPO agent on the corrected environment.

Run:   python step2_train_ppo.py                 (seed 1, 200,000 steps)
       python step2_train_ppo.py --seed 2        (optional extra seeds, if you have time)
       python step2_train_ppo.py --steps 100000  (shorter run for a slow laptop)
Time:  roughly 20-45 minutes per run on a laptop CPU. You can leave it running.
"""
import argparse

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from common import TRAIN_CSV, MODEL_DIR, RESULTS_DIR, load_split
from trading_env_v2 import TradingEnvV2

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--steps", type=int, default=200_000)
    args = ap.parse_args()

    train = load_split(TRAIN_CSV)
    env = Monitor(TradingEnvV2(train))

    model = PPO(
        "MlpPolicy", env,
        learning_rate=3e-4, gamma=0.99, clip_range=0.2,   # same values as thesis Section 3.7.2
        seed=args.seed, verbose=1,
        tensorboard_log=f"{RESULTS_DIR}/tensorboard",
        device="cpu",
    )
    print(f"[*] Training PPO, seed={args.seed}, steps={args.steps:,}. This takes a while...")
    model.learn(total_timesteps=args.steps, tb_log_name=f"PPO_v2_seed{args.seed}")
    path = f"{MODEL_DIR}/ppo_v2_seed{args.seed}"
    model.save(path)
    print(f"[+] Saved model to {path}.zip")
