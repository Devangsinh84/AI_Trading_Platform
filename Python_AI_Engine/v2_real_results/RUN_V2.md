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
| 2. Train PPO | `python step2_train_ppo.py` | ~20-45 min, leave it running |
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
