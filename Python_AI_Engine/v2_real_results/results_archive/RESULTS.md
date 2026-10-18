# v2 results summary (18 Oct 2026)

Data: S&P 500 (^GSPC) and VIX daily, 2016-2025. Chronological 80/20 split.
Test period: 2024-01-04 to 2025-12-30 (498 trading days). Real daily returns,
0.1% transaction cost per position change, scaler fitted on training data only.
All PPO runs: Stable-Baselines3, lr 3e-4, gamma 0.99, clip 0.2, action = {cash, invested}.

**These results are final. No further tuning was done after viewing the test set three times,
to avoid overfitting the test period.**

## Benchmarks

| Strategy | Return | Sharpe | Max DD | Days invested | Trades |
|---|---|---|---|---|---|
| Buy & Hold | +46.94% | 1.297 | 18.90% | 100% | 1 |
| XGBoost | +27.07% | 1.003 | 14.11% | 66.3% | 197 |

## Run 1: fixed start, return-only reward, 100k steps, 1 seed

| PPO | +0.00% | 0.000 | 0.00% | 0% | 0 |
|---|---|---|---|---|---|

Policy collapse: entropy fell to about -0.004 and SHAP attributed almost all of the decision to the
agent's own current position (0.63 vs < 0.012 for every market feature). The agent learned
"keep the current position"; starting in cash on the test set, it never entered.

## Run 2: random starts, entropy bonus 0.01, return-only reward, 200k steps, 3 seeds

| Seed | Return | Sharpe | Max DD | Days invested | Trades |
|---|---|---|---|---|---|
| 1 | +46.94% | 1.297 | 18.90% | 100% | 1 |
| 2 | -0.62% | -1.107 | 0.62% | 0.6% | 1 |
| 3 | +46.94% | 1.297 | 18.90% | 100% | 1 |

Every seed converged to a constant policy (two always invested = Buy & Hold, one always in cash).
SHAP magnitudes were tiny (max 0.0007): market features barely move the decision.

## Run 3: risk-sensitive reward r - 3*r^2, otherwise as run 2, 3 seeds

| Seed | Return | Sharpe | Max DD | Days invested | Trades |
|---|---|---|---|---|---|
| 1 | -6.36% | -0.239 | 18.90% | 25.3% | 3 |
| 2 | +20.61% | 0.844 | 12.86% | 38.6% | 1 |
| 3 | +46.94% | 1.297 | 18.90% | 100% | 1 |

* Entropy stayed higher for longer during training (about -0.07 late in training vs -0.002 in run 2),
  and policies became state-dependent for two of three seeds.
* SHAP (seed 1): market features now matter (Bollinger width 0.086, RSI 0.078, Bollinger %B 0.064,
  VIX 0.062), although current position is still the largest single factor (0.31).
* Regime shift in attributions (n = 124 calm vs 26 high-VIX days): volatility-related features roughly
  double in importance in high-VIX periods (Bollinger width 0.073 -> 0.149, 20-day volatility
  0.026 -> 0.054, MACD histogram 0.008 -> 0.021). Small sample; indicative only.
* Behaviour was not the intended "step out in turbulence": seeds 1 and 2 were invested a larger
  share of high-VIX days than calm days.

## Interpretation

1. The original prototype's 22.83% vs 22.21% came from the scaled-price environment, not learning.
2. With realistic returns and costs, a single PPO agent on daily technical features did not beat
   Buy & Hold on return or Sharpe in any of 7 runs. Outcomes were highly seed-dependent
   (-6% to +47%) and policies made only 0-3 trades.
3. A risk-sensitive objective makes the agent use market features and produces regime-dependent
   SHAP attributions, but did not improve risk-adjusted performance in this window.
4. The test window (2024-2025) was a strong bull market in which high-VIX days had higher mean
   returns (+0.26%/day for Buy & Hold) than calm days (+0.04%/day), driven by sharp rebounds such as
   April 2025. A volatility-avoiding policy is structurally disadvantaged in such a window.
5. These results motivate the thesis's proposed next steps: explicit regime routing (Meta-Controller
   with specialised agents) rather than expecting one agent to discover regimes, walk-forward
   evaluation over several market cycles, more assets, and more seeds.
