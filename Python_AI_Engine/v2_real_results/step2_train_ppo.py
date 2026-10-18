"""
STEP 2: Train the PPO agent on the corrected environment.

Run:   python step2_train_ppo.py --seed 1
       python step2_train_ppo.py --seed 2
       python step2_train_ppo.py --seed 3
Each run: 200,000 steps, roughly 10-15 minutes on a laptop CPU.

Training setup (changed after run 1, where the policy collapsed to "never trade"):
  * Episodes start on a random day, in a random position, and last one trading year (252 days).
  * An entropy bonus (ent_coef=0.01) keeps the agent exploring instead of freezing early.
Evaluation (step 3) still runs the whole test period from day 1, starting in cash.
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
    ap.add_argument("--ent", type=float, default=0.01, help="entropy coefficient")
    ap.add_argument("--episode", type=int, default=252, help="training episode length in days")
    ap.add_argument("--risk", type=float, default=0.0,
                    help="risk aversion lambda: 0 = return only; e.g. 3 = risk-sensitive reward r - 3*r^2")
    args = ap.parse_args()

    train = load_split(TRAIN_CSV)
    env = Monitor(TradingEnvV2(train, random_start=True, episode_length=args.episode,
                               risk_aversion=args.risk))
    name = f"ppo_v2_risk{args.risk:g}_seed{args.seed}" if args.risk > 0 else f"ppo_v2_seed{args.seed}"

    model = PPO(
        "MlpPolicy", env,
        learning_rate=3e-4, gamma=0.99, clip_range=0.2,   # same values as thesis Section 3.7.2
        ent_coef=args.ent,
        seed=args.seed, verbose=1,
        tensorboard_log=f"{RESULTS_DIR}/tensorboard",
        device="cpu",
    )
    print(f"[*] Training {name}: steps={args.steps:,}, ent_coef={args.ent}, risk={args.risk}, "
          f"episode={args.episode} days, random starts...")
    model.learn(total_timesteps=args.steps, tb_log_name=name)
    path = f"{MODEL_DIR}/{name}"
    model.save(path)
    print(f"[+] Saved model to {path}.zip")
