# 🏛️ AI Trading Civilization

Advanced multi-agent AI system for automated trading strategy evolution and backtesting.

## Overview

This project runs a "civilization" of 100 AI trading agents that evolve trading strategies in real-time using market data (XAUUSD and BTC-USD).

- **Key Features**:
  - 100 agents with genetic algorithm-style evolution
  - Supports Risk-Reward ratios from 1:1 to 1:20
  - Continuous backtesting (~every 10 seconds)
  - Rich Gradio dashboard showing live win rates, PNL, fitness, etc.
  - **Automatic saving** of high-winrate (≥80% WR) strategies to the `high_winrate_strategies/` folder
  - Crash-proof, stable, with many bug fixes from previous versions

## Files

- `app.py` — Main application (Gradio web UI + trading engine)
- `requirements.txt` — Python dependencies
- `high_winrate_strategies/` — Folder containing automatically saved top-performing strategy JSON files (e.g. `colony-1_adv_*.json`)

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. (Optional) Set environment variables for GitHub auto-save:
   ```bash
   export GH_TOKEN=your_github_pat_with_repo_scope
   export COLONY_ID=colony-1
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Open the Gradio interface (usually at http://localhost:7860)

## GitHub Integration

High-performing strategies (≥80% win rate) are automatically committed and pushed back to this repository under `high_winrate_strategies/`.

## Tech Stack

- Python 3
- Gradio (UI)
- yfinance (market data)
- asyncio

## License

No license specified.

---

*Last updated: 2026-06-17*
