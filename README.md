# 🏛️ AI Trading Civilization

**Advanced multi-agent AI system** for automated trading strategy evolution, backtesting, and live signal generation.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Gradio](https://img.shields.io/badge/Gradio-4.x-orange) ![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Overview

This project simulates a "civilization" of **100 AI trading agents** that continuously evolve sophisticated trading strategies in real time using live market data (XAUUSD and BTC-USD).

### Key Features

- **100 Agents** with genetic algorithm-style evolution
- **Flexible Risk-Reward** ratios from **1:1 to 1:20**
- **Continuous backtesting** (~every 10 seconds)
- **Rich Gradio dashboard** with live win rates, PNL, fitness, indicators, and full strategy details
- **Automatic GitHub saving** of high-winrate (≥80% WR) strategies to the `high_winrate_strategies/` folder
- **Crash-proof & stable** — extensive error handling and recovery
- **Technical indicators**: RSI, SMA, EMA, ATR, Bollinger Bands, MACD, Stochastic
- **Lightweight & efficient** — works with real Yahoo Finance data or synthetic fallback

## 📁 Repository Structure

```
ai-trading-civilization/
├── app.py                      # Main app: agents + backtester + Gradio UI
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── LICENSE                     # MIT License
├── .gitignore                  # Production-ready ignores
└── high_winrate_strategies/    # Auto-saved top strategies (JSON)
    ├── colony-1_adv_005_wr100.json
    └── ...
```

## 🚀 Quick Start

### 1. Clone and install

```bash
git clone https://github.com/femidaali537-afk/ai-trading-civilization.git
cd ai-trading-civilization
pip install -r requirements.txt
```

### 2. (Recommended) Set environment variables

```bash
export GH_TOKEN=your_github_pat_with_repo_scope   # for auto-saving high WR strategies
export COLONY_ID=colony-1
```

### 3. Run the application

```bash
python app.py
```

### 4. Open the dashboard

Go to **http://localhost:7860** (or the URL shown in terminal).

The dashboard updates live every ~8 seconds and shows:
- Current prices (XAUUSD / BTC)
- Top agents with win rate, PNL, profit factor, RR, indicators
- Evolution generations
- High performers (≥80% WR) being auto-saved to GitHub

## ⚙️ Configuration

Edit the top of `app.py`:

```python
CFG = {
    "symbols": ["XAUUSD=X", "BTC-USD"],
    "backtest_days": 5,
    "data_refresh_s": 10,
}
AGENTS_PER_COLONY = 100
```

## 🔄 GitHub Auto-Save Feature

High-performing strategies (≥80% win rate) are automatically committed to the `high_winrate_strategies/` folder every few minutes when `GH_TOKEN` is set.

This allows you to:
- Keep a permanent record of winning strategies
- Load them later for live trading
- Share or analyze the best evolved strategies

## 🧠 How the Agents Work

1. **Initialization** — 100 random strategies with 3–6 indicators each + random RR ratio
2. **Backtesting** — Every ~10s, top agents are backtested on recent 5m data
3. **Evolution** — Every ~20 ticks: elite selection + mutation
4. **Signals** — Real-time signals generated from top agents
5. **Persistence** — Top performers saved to GitHub

## 📊 Dashboard Columns

| Column     | Description                          |
|------------|--------------------------------------|
| Agent ID   | Short unique identifier              |
| Strategy Name | Auto-generated from indicators    |
| Win Rate   | Historical win percentage            |
| Total Trades | Number of completed trades        |
| W/L        | Wins / Losses                        |
| PNL        | Total profit/loss                    |
| PF         | Profit Factor                        |
| RR         | Risk-Reward ratio used               |
| Indicators | Key indicators used                  |
| Fitness    | Composite score                      |

## 🛠️ Tech Stack

- **Python 3.10+**
- **Gradio** — Beautiful reactive dashboard
- **yfinance** — Real market data (with synthetic fallback)
- **asyncio** — Concurrent data fetching & backtesting
- **aiohttp** — GitHub API integration

## 🔒 Security Notes

- Never commit real `GH_TOKEN` values
- The `.gitignore` excludes tokens, `.env`, caches, etc.
- All GitHub pushes for strategies use the provided token securely at runtime

## 📜 License

MIT License — see [LICENSE](LICENSE) file.

## 🤝 Contributing

Pull requests and strategy ideas are welcome! Open an issue to discuss improvements.

---

**Last updated:** 2026-06-17  
**Maintained by:** femidaali537-afk
