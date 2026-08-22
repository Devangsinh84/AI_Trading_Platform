# Architecting a Regime-Aware Deep Reinforcement Learning Microservice Ecosystem for Explainable Algorithmic Trading

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![.NET](https://img.shields.io/badge/.NET-10.0-purple?logo=dotnet)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)

---

## Abstract

## Overview

Modern algorithmic trading systems face a fundamental trilemma: generating consistent alpha, managing downside risk, and remaining interpretable for enterprise risk oversight. Most approaches optimise for one dimension at the cost of the others.

This project implements a **regime-aware microservice architecture** that treats each concern as an independent, composable service. A Deep Reinforcement Learning agent (PPO) trains on financial market data to learn dynamic trading policies, while a VIX-driven regime classifier dynamically routes execution between defensive and aggressive postures at runtime. A C# Meta-Controller acts as an orchestrator and circuit breaker, and every trade signal is accompanied by real-time SHAP/LIME explainability metrics to guarantee transparent decision audits.

The result is a system that is simultaneously adaptive, risk-aware, and explainable — evaluated against Buy & Hold and XGBoost baselines on fully unseen test data.

---

## System Architecture

The platform is composed of three decoupled microservices that communicate over REST. Each service owns a single responsibility and can be developed, tested, and scaled independently.

```
┌─────────────────────────────────────────────────────────────┐
│                    React Dashboard : 5173                   │
│         XAI Charts · Portfolio Metrics · Live Feed         │
└──────────────────────────┬──────────────────────────────────┘
                           │  REST (HTTP GET/POST)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               .NET Meta-Controller API : 5200               │
│     Circuit Breaker · Trade Router · Performance Metrics   │
└──────────────────────────┬──────────────────────────────────┘
                           │  REST (HTTP POST /predict)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Python AI Engine : 8000                    │
│      PPO Agent · XGBoost Baseline · SHAP/LIME · FastAPI    │
└─────────────────────────────────────────────────────────────┘
```

![Architecture Diagram](path/to/architecture_diagram.png)

The React Dashboard polls the .NET Meta-Controller for live market data and performance metrics. The Meta-Controller forwards prediction requests to the Python AI Engine and maintains an in-memory portfolio state tracker. The Python AI Engine hosts the trained PPO model and XGBoost baseline, returning predictions and SHAP feature importance payloads.

---

## Tech Stack

**Python AI Engine**
- Python 3.11+
- Stable-Baselines3 (PPO — Proximal Policy Optimization)
- FastAPI + Uvicorn (REST microservice host)
- pandas-ta (technical indicator generation)
- XGBoost (supervised learning baseline)
- SHAP + LIME (explainable AI)
- yfinance (live market data ingestion)
- PyTorch 2.x (neural network backend)
- Matplotlib (evaluation charting)

**DotNet MetaController**
- C# 11 / .NET 10.0
- ASP.NET Core Web API
- Scalar (OpenAPI explorer)
- In-memory portfolio state tracking
- HttpClient (Python AI Engine proxy)

**React Dashboard**
- React 19 + Vite 8
- Tailwind CSS v4
- Recharts (SHAP/LIME visualisation)
- Lightweight Charts (candlestick feed)
- Lucide React (iconography)

---

## Repository Structure

```
AI_Trading_Platform/
├── Python_AI_Engine/          # Quantitative brain — data, training, XAI, FastAPI
│   ├── data/                  # Processed S&P 500 CSVs + trained XGBoost model
│   ├── models/                # Saved PPO agent + training checkpoints
│   ├── tensorboard_logs/      # PPO training telemetry
│   ├── api_gateway.py         # FastAPI entry point (XGBoost prediction endpoint)
│   ├── main.py                # FastAPI entry point (live PPO prediction endpoint)
│   ├── train_agent.py         # PPO training pipeline
│   ├── evaluate_agent.py      # Post-training evaluation on test data
│   ├── compare_strategies.py  # Buy & Hold vs XGBoost vs PPO showdown
│   ├── trading_env.py         # Custom Gymnasium trading environment
│   ├── baseline_model.py      # XGBoost baseline training
│   ├── data_fetcher.py        # Live market data + indicator computation
│   ├── data_ingestion.py      # Historical data processing pipeline
│   ├── ai_preprocessing.py    # Feature engineering
│   └── requirements.txt
│
├── DotNet_MetaController/     # Execution router — circuit breaker + metrics API
│   └── MetaController.API/
│       ├── Controllers/       # TradingIntelligenceController (live-feed, evaluate)
│       ├── Services/          # PerformanceMetricsService + LivePortfolioState
│       ├── Clients/           # PythonAiClient (HTTP proxy)
│       ├── Models/            # Request/response DTOs
│       └── Program.cs         # Service registration + CORS + endpoints
│
└── React_Dashboard/           # XAI presentation layer
    ├── src/
    │   ├── components/        # Dashboard, TradingChart, PerformanceMetrics
    │   ├── App.jsx
    │   └── main.jsx
    ├── vite.config.js
    └── package.json
```

---

## Getting Started

> **Prerequisites:** Python 3.11+, .NET 10 SDK, Node.js 20+

All three services must be running simultaneously. Start them in the order below.

---

### 1. Python AI Engine

The quantitative core. Hosts the trained PPO agent and XGBoost baseline via FastAPI on port `8000`.

```bash
cd Python_AI_Engine
```

Create and activate a virtual environment:

```bash
python -m venv venv

# For Windows:
.\venv\Scripts\activate

# For Mac/Linux:
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

**Option A — Run the live PPO prediction server (used by the Dashboard):**

```bash
uvicorn main:app --reload --port 8000
```

**Option B — Run the XGBoost trade routing gateway:**

```bash
python api_gateway.py
```

**Optional: Re-train the PPO agent from scratch:**

```bash
python train_agent.py
```

**Optional: Evaluate the trained agent on unseen test data:**

```bash
python evaluate_agent.py
```

**Optional: Run the three-way strategy comparison (Buy & Hold vs XGBoost vs PPO):**

```bash
python compare_strategies.py
```

The FastAPI service will be available at `http://localhost:8000`. You can verify it is online at `http://localhost:8000/` which returns a health-check JSON payload.

---

### 2. DotNet MetaController

The execution router and circuit breaker. Proxies requests between the AI engine and the React frontend. Exposes performance metrics calculated from live price ticks.

```bash
cd DotNet_MetaController/MetaController.API
```

Restore packages and start the API:

```bash
dotnet run
```

The API will start on `http://localhost:5200`.

Key endpoints:
- `GET /api/tradingintelligence/live-feed` — proxies the live prediction from the Python AI Engine and records each price tick
- `GET /api/performance-metrics` — returns live Sharpe Ratio, Max Drawdown, and Cumulative Return calculated from in-memory price history
- `GET /scalar/v1` — Scalar OpenAPI explorer

> The Meta-Controller expects the Python AI Engine to be running on port `8000` before calling the live-feed endpoint.

---

### 3. React Dashboard

The XAI presentation layer. Displays live price data, SHAP feature importance charts, and portfolio performance metrics.

```bash
cd React_Dashboard
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

> CORS is pre-configured in the Meta-Controller to allow requests from `http://localhost:5173`. No additional configuration is needed.

---

### Service Port Summary

| Service | Technology | Port |
|---|---|---|
| Python AI Engine | FastAPI / Uvicorn | `8000` |
| DotNet MetaController | ASP.NET Core | `5200` |
| React Dashboard | Vite Dev Server | `5173` |

---

## Research Pipeline

The following scripts execute the full research workflow from raw data to thesis-ready outputs:

| Step | Script | Purpose |
|---|---|---|
| 1 | `data_ingestion.py` | Download and process 10 years of S&P 500 data |
| 2 | `ai_preprocessing.py` | Generate technical indicators (RSI, MACD, Bollinger Bands) |
| 3 | `baseline_model.py` | Train the XGBoost supervised learning baseline |
| 4 | `train_agent.py` | Run PPO deep reinforcement learning (270,000 timesteps) |
| 5 | `evaluate_agent.py` | Evaluate PPO agent on held-out test data |
| 6 | `compare_strategies.py` | Generate the three-strategy showdown chart |

TensorBoard training logs are written to `Python_AI_Engine/tensorboard_logs/`. To visualise them:

```bash
cd Python_AI_Engine
tensorboard --logdir tensorboard_logs/
```

---

## Future Work

The foundational microservice architecture is designed for extensibility. The current system is trained and evaluated on S&P 500 data (ETF proxy), but the environment, data pipeline, and API contracts are asset-agnostic.

The next development phase has the following items scoped:

- **Dynamic asset switching** — a UI ticker-selection dropdown that allows the user to switch between instruments (equities, crypto, ETFs) at runtime without restarting any service
- **Live VIX regime integration** — replacing the placeholder regime signal with a real-time CBOE VIX feed to drive the circuit-breaker routing logic in the Meta-Controller
- **EU AI Act compliance report generation** — automated PDF export of SHAP/LIME explanations per trade session, formatted for regulatory submission
- **Containerisation** — Docker Compose manifest to orchestrate all three microservices as a single deployable unit

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

![License](https://img.shields.io/badge/license-MIT-blue)

---

## Author & Maintainer

**Devangsinh Gohil**
* GitHub: [@Devangsinh84](https://github.com/Devangsinh84)
* LinkedIn: [https://www.linkedin.com/in/devangsinh-gohil-70a42a239/](https://www.linkedin.com/in/devangsinh-gohil-70a42a239/)
* Project Link: [https://github.com/Devangsinh84/AI_Trading_Platform](https://github.com/Devangsinh84/AI_Trading_Platform)
