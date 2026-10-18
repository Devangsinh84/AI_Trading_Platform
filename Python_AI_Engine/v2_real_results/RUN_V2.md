# v2: Real results for the thesis

This folder recomputes the thesis results with the problems of the first prototype fixed.
The original code is untouched; everything here is separate.

| Problem in v1 | Fix in v2 |
|---|---|
| Returns were differences of MinMax-scaled prices x 0.5 | Real daily % returns of the S&P 500 |
| Scaler fitted on all 10 years (look-ahead leakage) | Scaler fitted on the training period only |
| Reward: gains x100, losses x50, penalty for cash | Reward = real portfolio return, symmetric |
| No transaction costs | 0.1% cost every time the position changes |
| Raw price levels as features | Stationary features (RSI, MACD/price, Bollinger %B and width, returns, volatility, volume change, VIX) |
| VIX never used | VIX downloaded, used as a feature and to split results by regime |
| No Sharpe / drawdown for the test period | Sharpe, drawdown, volatility, trades for every strategy |
| SHAP values were random placeholders | Real SHAP (KernelExplainer) on the trained PPO policy |

## One-time setup (about 15 minutes)

Open a terminal in this folder (`Python_AI_Engine/v2_real_results`) and run:

```
python -m venv venv
venv\Scripts\activate          (Windows)   or   source venv/bin/activate   (Mac/Linux)
pip install -r requirements_v2.txt
```

## Run the steps in order

| Step | Command | Time on a laptop |
|---|---|---|
| 1. Data | `python step1_prepare_data.py` | ~1 min (needs internet) |
| 2. Train PPO | `python step2_train_ppo.py --seed 1` (then `--seed 2`, `--seed 3`) | ~10-15 min per seed |
| 3. Evaluate | `python step3_evaluate.py` | ~1-2 min |
| 4. SHAP | `python step4_shap.py` | ~5-20 min |

Slow laptop? Use `python step2_train_ppo.py --steps 100000` and `python step4_shap.py --days 150`.

Extra time? Train more seeds (`--seed 2`, `--seed 3`) before step 3. Step 3 automatically
evaluates every trained seed, which shows whether the result is stable.

## What to send back to Claude

Everything in `results_v2/`:
- `results_table.csv`, `regime_table.csv`, `figure_5_1_v2.png`
- `shap_global.png`, `shap_by_regime.png`, `shap_by_regime.csv`
- plus a copy of what each step printed in the terminal (screenshots are fine)

## Note on training run 1 (18 Oct 2026)

The first run (fixed start date, no entropy bonus, 100k steps) collapsed to a policy that
never traded on the test set: entropy fell to about -0.004 and SHAP showed the agent relied
almost entirely on its own current position. Training now uses random start dates, random
initial positions, one-year episodes and an entropy bonus (ent_coef=0.01). Keep the run 1
outputs (rename `results_v2` to `results_v2_run1`); they are a valid finding for the thesis.

## Note on training run 2 (18 Oct 2026)

Random starts + entropy bonus, return-only reward, 3 seeds x 200k steps. Every seed converged to a
constant policy (seeds 1 and 3 always invested = Buy & Hold, seed 2 always in cash). SHAP values
became tiny (~0.0007), confirming the indicators barely influence the decision. Interpretation:
with real returns and costs, the indicators carry too little directional signal, so a constant
policy is optimal for a return-only objective.

## Run 3: risk-sensitive reward

`python step2_train_ppo.py --seed 1 --risk 3` (and seeds 2, 3). Reward = r - 3*r^2 (mean-variance).
Volatility is far more predictable than direction, so this objective gives the agent a learnable
reason to step out of the market in turbulent periods. Models are saved as `ppo_v2_risk3_seedN`;
step 3 evaluates return-only and risk-aware models side by side.
