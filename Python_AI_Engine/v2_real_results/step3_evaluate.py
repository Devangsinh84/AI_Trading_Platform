"""
STEP 3: Compare Buy & Hold, XGBoost and PPO on the unseen test period with REAL returns,
transaction costs, Sharpe ratio and maximum drawdown.

Run:   python step3_evaluate.py
Time:  about 1-2 minutes
Output (in results_v2/):
  results_table.csv       -> new Table 5.2
  equity_curves.csv       -> daily portfolio values of every strategy
  figure_5_1_v2.png       -> new Figure 5.1
  regime_table.csv        -> how each strategy behaved in calm vs high-VIX days
"""
import glob
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import (FEATURES, TRAIN_CSV, TEST_CSV, MODEL_DIR, RESULTS_DIR, VIX_REGIME_THRESHOLD,
                    backtest, performance_metrics, load_split)


def xgboost_positions(train, test):
    import xgboost as xgb
    model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5,
                              random_state=42, eval_metric="logloss")
    model.fit(train[FEATURES], train["Target"])
    return model.predict(test[FEATURES]).astype(int)


def ppo_positions(model_path, test):
    from stable_baselines3 import PPO
    from trading_env_v2 import TradingEnvV2
    model = PPO.load(model_path, device="cpu")
    env = TradingEnvV2(test)
    obs, _ = env.reset()
    positions, done = [], False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        positions.append(int(action))
        obs, _, done, _, _ = env.step(action)
    return np.array(positions)


def regime_breakdown(name, positions, test):
    n = len(positions)
    ret = test["Next_Ret"].to_numpy()[:n]
    vix = test["VIX_raw"].to_numpy()[:n]
    rows = []
    for label, mask in (("Calm (VIX < %g)" % VIX_REGIME_THRESHOLD, vix < VIX_REGIME_THRESHOLD),
                        ("High volatility (VIX >= %g)" % VIX_REGIME_THRESHOLD, vix >= VIX_REGIME_THRESHOLD)):
        if mask.sum() == 0:
            continue
        strat = positions[mask] * ret[mask]
        rows.append({"Strategy": name, "Regime": label, "Days": int(mask.sum()),
                     "Days invested (%)": round(positions[mask].mean() * 100, 1),
                     "Mean daily return (%)": round(strat.mean() * 100, 4)})
    return rows


if __name__ == "__main__":
    train, test = load_split(TRAIN_CSV), load_split(TEST_CSV)
    n = len(test) - 1                       # the environment stops one day before the end
    next_ret = test["Next_Ret"].to_numpy()[:n]

    strategies = {"Buy & Hold": np.ones(n, dtype=int),
                  "XGBoost": xgboost_positions(train, test)[:n]}

    model_paths = sorted(glob.glob(os.path.join(MODEL_DIR, "ppo_v2_*.zip")))
    if not model_paths:
        raise SystemExit("[!] No trained PPO model found. Run step2_train_ppo.py first.")
    for path in model_paths:
        tag = os.path.basename(path).replace("ppo_v2_", "").replace(".zip", "")
        if tag.startswith("risk"):                     # e.g. risk3_seed1
            lam, seed = tag.split("_")
            label = f"PPO risk-aware lambda={lam[4:]} ({seed})"
        else:
            label = f"PPO return-only ({tag})"
        strategies[label] = ppo_positions(path, test)[:n]

    rows, curves, regime_rows = [], {}, []
    for name, pos in strategies.items():
        values = backtest(pos, next_ret)
        curves[name] = values
        rows.append({"Strategy": name, **performance_metrics(values, pos)})
        regime_rows += regime_breakdown(name, pos, test)

    table = pd.DataFrame(rows).set_index("Strategy")
    table.to_csv(f"{RESULTS_DIR}/results_table.csv")
    pd.DataFrame(regime_rows).to_csv(f"{RESULTS_DIR}/regime_table.csv", index=False)
    dates = list(test.index[:n + 1])
    pd.DataFrame(curves, index=dates).rename_axis("Date").to_csv(f"{RESULTS_DIR}/equity_curves.csv")

    print("\n================ TEST PERIOD RESULTS ================")
    print(f"Period: {dates[0].date()} -> {dates[-1].date()}  ({n} trading days, 0.1% cost per trade)")
    print(table.to_string())
    print("\n================ BY VIX REGIME ================")
    print(pd.DataFrame(regime_rows).to_string(index=False))

    # Figure 5.1 (v2)
    fig, ax = plt.subplots(figsize=(11, 6))
    styles = {"Buy & Hold": dict(color="black", linestyle="--", linewidth=2.2, zorder=5),
              "XGBoost": dict(color="darkorange", linewidth=1.8)}
    blues = iter(["#93c5fd", "#3b82f6", "#1e3a8a", "#60a5fa", "#1d4ed8"])
    greens = iter(["#86efac", "#16a34a", "#14532d", "#4ade80", "#15803d"])
    for name, values in curves.items():
        if name in styles:
            style = styles[name]
        elif "risk-aware" in name:
            style = dict(color=next(greens, None), linewidth=2.0)
        else:
            style = dict(color=next(blues, None), linewidth=1.4, linestyle=":")
        ret = table.loc[name, "Cumulative return (%)"]
        ax.plot(dates, values, label=f"{name} ({ret:+.2f}%)", **style)
    # shade high-volatility days
    high = test["VIX_raw"].to_numpy()[:n + 1] >= VIX_REGIME_THRESHOLD
    ax.fill_between(dates, 0, 1, where=high, transform=ax.get_xaxis_transform(),
                    color="red", alpha=0.08, label=f"VIX >= {VIX_REGIME_THRESHOLD:g}")
    ax.set_title("Out-of-sample performance (real returns, 0.1% transaction cost)")
    ax.set_ylabel("Portfolio value ($)")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{RESULTS_DIR}/figure_5_1_v2.png", dpi=200)
    print(f"\n[+] Saved table, curves and figure to {RESULTS_DIR}")
