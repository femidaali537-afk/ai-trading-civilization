# 🏛️ XAUUSD 1m AI Trading Civilization

This project implements a self-evolving population of 100 AI agents dedicated to finding the "Holy Grail" of Gold (XAUUSD) 1-minute scalping strategies.

## 🚀 How it Works
- **Focus**: Strictly XAUUSD on the 1m timeframe.
- **Intelligence**: Agents combine SMC (Smart Money Concepts), ICT (Inner Circle Trader) patterns like Fair Value Gaps (FVG), and traditional indicators (EMA, RSI, ATR).
- **Evolution**: A genetic algorithm evolves the most profitable parameters across generations.
- **Self-Improvement**: Agents analyze their losses. If they detect too many reversals, they automatically strengthen trend filters. If they are stopped out too early, they adjust their ATR multipliers.
- **Auto-Export**: When an agent hits a win rate of $\ge 80\%$, the system generates a **full manual** and a **TradingView Pine Script** indicator, which is automatically pushed to the `high_winrate_strategies/` folder on GitHub.

## 🛠️ Setup
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run: `python app.py`.
4. Access the dashboard at `http://localhost:7860`.
