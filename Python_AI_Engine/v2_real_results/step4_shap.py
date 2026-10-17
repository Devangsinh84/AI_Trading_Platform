"""
STEP 4: Compute REAL SHAP explanations for the trained PPO agent.

What is explained: the agent's probability of choosing "invested" (action 1) on each test day.
Method: SHAP KernelExplainer (model-agnostic), background = 100 training days.

Run:   python step4_shap.py                      (uses ppo_v2_seed1)
       python step4_shap.py --model ppo_v2_seed2
       python step4_shap.py --days 150           (fewer days = faster on a slow laptop)
Time:  about 5-20 minutes depending on the laptop
Output (in results_v2/):
  shap_values.csv          -> SHAP value of every feature on every explained day
  shap_global.png          -> global feature importance (replaces Figure 3.3 / 5.4)
  shap_by_regime.png       -> importance in calm vs high-VIX days (tests the thesis claim)
  shap_by_regime.csv
"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import (FEATURES, FEATURE_LABELS, TRAIN_CSV, TEST_CSV, MODEL_DIR, RESULTS_DIR,
                    VIX_REGIME_THRESHOLD, load_split)


def build_states(model, df):
    """Re-create the observations the agent actually saw (features + its own current position)."""
    from trading_env_v2 import TradingEnvV2
    env = TradingEnvV2(df)
    obs, _ = env.reset()
    states, done = [obs], False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, done, _, _ = env.step(action)
        states.append(obs)
    return np.array(states[:-1])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="ppo_v2_seed1")
    ap.add_argument("--days", type=int, default=250)
    ap.add_argument("--nsamples", type=int, default=300)
    args = ap.parse_args()

    import shap
    import torch
    from stable_baselines3 import PPO

    model = PPO.load(f"{MODEL_DIR}/{args.model}", device="cpu")
    train, test = load_split(TRAIN_CSV), load_split(TEST_CSV)

    def prob_invested(X):
        with torch.no_grad():
            obs_t, _ = model.policy.obs_to_tensor(np.asarray(X, dtype=np.float32))
            dist = model.policy.get_distribution(obs_t)
            return dist.distribution.probs[:, 1].cpu().numpy()

    train_states = build_states(model, train)
    test_states = build_states(model, test)

    rng = np.random.default_rng(0)
    background = train_states[rng.choice(len(train_states), size=min(100, len(train_states)), replace=False)]
    idx = np.linspace(0, len(test_states) - 1, num=min(args.days, len(test_states))).astype(int)
    X = test_states[idx]

    print(f"[*] Explaining {len(X)} test days with SHAP (nsamples={args.nsamples})...")
    explainer = shap.KernelExplainer(prob_invested, background)
    sv = np.asarray(explainer.shap_values(X, nsamples=args.nsamples))
    if sv.ndim == 3:                       # some shap versions add an output axis
        sv = sv[..., 0]

    names = FEATURES + ["Position"]
    labels = [FEATURE_LABELS[n] for n in names]
    dates = test.index[idx]
    vix = test["VIX_raw"].to_numpy()[idx]
    pd.DataFrame(sv, columns=names, index=dates).assign(VIX_raw=vix).to_csv(f"{RESULTS_DIR}/shap_values.csv")

    # Global importance
    imp = pd.Series(np.abs(sv).mean(axis=0), index=labels).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.barh(imp.index, imp.values, color="#4f46e5")
    ax.set_xlabel("Mean |SHAP value| (effect on probability of being invested)")
    ax.set_title(f"Global SHAP feature importance, PPO agent ({len(X)} test days)")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{RESULTS_DIR}/shap_global.png", dpi=200)

    # Calm vs high-volatility regimes
    calm, high = vix < VIX_REGIME_THRESHOLD, vix >= VIX_REGIME_THRESHOLD
    reg = pd.DataFrame({
        f"Calm (VIX < {VIX_REGIME_THRESHOLD:g}, n={calm.sum()})":
            np.abs(sv[calm]).mean(axis=0) if calm.any() else np.nan,
        f"High volatility (VIX >= {VIX_REGIME_THRESHOLD:g}, n={high.sum()})":
            np.abs(sv[high]).mean(axis=0) if high.any() else np.nan,
    }, index=labels)
    reg = reg.loc[imp.index]
    reg.to_csv(f"{RESULTS_DIR}/shap_by_regime.csv")
    ax = reg.plot.barh(figsize=(8, 6), color=["#10b981", "#ef4444"])
    ax.set_xlabel("Mean |SHAP value|")
    ax.set_title("SHAP importance by market regime")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/shap_by_regime.png", dpi=200)

    print("\n=========== GLOBAL IMPORTANCE (highest first) ===========")
    print(imp.sort_values(ascending=False).round(4).to_string())
    print("\n=========== BY REGIME ===========")
    print(reg.iloc[::-1].round(4).to_string())
    print(f"\n[+] Saved SHAP results to {RESULTS_DIR}")
