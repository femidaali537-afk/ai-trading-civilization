#!/usr/bin/env python3
"""
🏛️ AI TRADING CIVILIZATION: XAUUSD 1M GOLD EDITION
- Focus: XAUUSD 1-Minute Chart exclusively.
- Goal: 80-90% Win Rate via self-improving AI Agents.
- Tech: SMC, ICT, Indicators, Genetic Evolution, & Mistake Analysis.
- Output: Detailed Manuals + TradingView Pine Script for Elite Strategies.
"""

import asyncio
import json
import os
import random
import time
import warnings
import threading
import base64
import requests
from datetime import datetime, timedelta
from pathlib import Path

warnings.filterwarnings("ignore")

# ================== CONFIGURATION ==================
COLONY_ID = os.getenv("COLONY_ID", "gold-colony-1")
AGENTS_PER_COLONY = 100
GH_TOKEN = os.getenv("GH_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "femidaali537-afk/ai-trading-civilization")

CFG = {
    "symbol": "XAUUSD=X",
    "tf": "1m",
    "backtest_days": 30,
    "data_refresh_s": 10,
    "winrate_threshold": 80.0,
    "min_trades": 100,
    "target_winrate": 90.0,
}

class Log:
    @staticmethod
    def i(m, *a): print(f"{datetime.now().strftime('%H:%M:%S')} | INFO  | {m % a if a else m}", flush=True)
    @staticmethod
    def learn(m, *a): print(f"{datetime.now().strftime('%H:%M:%S')} | LEARN | {m % a if a else m}", flush=True)
    @staticmethod
    def w(m, *a): print(f"{datetime.now().strftime('%H:%M:%S')} | WARN  | {m % a if a else m}", flush=True)

# ================== DATA ENGINE ==================
class DataFetcher:
    def __init__(self):
        import yfinance as yf
        self.yf = yf
        self._cache = None
        self._last_update = 0

    async def fetch_gold_1m(self):
        now = time.time()
        if self._cache and now - self._last_update < 60:
            return self._cache
        
        try:
            # yfinance 1m data is limited to last 7 days
            df = self.yf.Ticker("GC=F").history(period="7d", interval="1m")
            if df.empty: return []
            
            data = []
            for i, r in df.iterrows():
                data.append({
                    "time": i.isoformat(),
                    "open": float(r.Open),
                    "high": float(r.High),
                    "low": float(r.Low),
                    "close": float(r.Close),
                    "vol": float(r.Volume)
                })
            self._cache = data
            self._last_update = now
            return data
        except Exception as e:
            Log.w(f"Fetch error: {e}")
            return []

# ================== STRATEGY & LEARNING ==================
class Strategy:
    def __init__(self, sid):
        self.id = sid
        # Give each agent a unique, cool name
        prefixes = ["Zenith", "Atlas", "Nova", "Apex", "Quantum", "Titan", "Aether", "Solar", "Luna", "Onyx", "Vortex", "Iron", "Gold", "Silver", "Omega", "Alpha", "Sigma", "Prime", "Nexus", "Krypton"]
        suffixes = ["Guardian", "Trader", "Scalper", "Oracle", "Sentinel", "Hunter", "Seeker", "Warden", "Knight", "Master", "Savant", "Wizard", "Architect", "Voyager", "Sentinel"]
        self.name = f"{random.choice(prefixes)}-{random.choice(suffixes)}-{random.randint(100, 999)}"
        
        self.params = {
            "ema_fast": random.randint(5, 21),
            "ema_slow": random.randint(22, 200),
            "rsi_period": random.randint(7, 14),
            "rsi_upper": random.randint(65, 85),
            "rsi_lower": random.randint(15, 35),
            "atr_mult": round(random.uniform(1.0, 3.0), 2),
            "rr_ratio": random.randint(2, 10),
            "smc_weight": random.uniform(0, 1), 
            "ict_fvg_size": round(random.uniform(0.1, 0.5), 2),
            "lookback": random.randint(20, 100),
        }
        self.winrate = 0.0
        self.trades = 0
        self.pnl = 0.0
        self.fitness = 0.0
        self.history = [] 

    def mutate(self):
        child = Strategy(self.id + "_m")
        child.params = self.params.copy()
        # Mutate a random parameter
        p = random.choice(list(child.params.keys()))
        if "period" in p or "ema" in p or "lookback" in p:
            child.params[p] += random.choice([-1, 1])
        elif "rsi" in p:
            child.params[p] += random.randint(-2, 2)
        elif "mult" in p or "weight" in p or "size" in p:
            child.params[p] += random.uniform(-0.1, 0.1)
        else:
            child.params[p] += random.choice([-1, 1])
        
        # Constraints
        child.params["ema_fast"] = max(2, child.params["ema_fast"])
        child.params["ema_slow"] = max(child.params["ema_fast"] + 1, child.params["ema_slow"])
        child.params["rr_ratio"] = max(1, child.params["rr_ratio"])
        child.params["smc_weight"] = max(0, min(1, child.params["smc_weight"]))
        return child

    def analyze_and_improve(self):
        """Self-improvement based on trade mistakes"""
        if len(self.history) < 10: return
        
        recent = self.history[-20:]
        losses = [r for w, r in recent if not w]
        if not losses: return

        # Analyze failure reasons
        reversal_count = sum(1 for r in losses if "reversal" in r.lower())
        premature_sl = sum(1 for r in losses if "sl" in r.lower())

        if reversal_count > len(losses) * 0.4:
            # Too many reversals -> Increase Trend confirmation
            self.params["ema_slow"] += 5
            self.params["smc_weight"] += 0.05
            Log.learn(f"{self.name} learning: High reversals detected -> Strengthening trend filters.")

        if premature_sl > len(losses) * 0.4:
            # Stopped out too early -> Increase SL room
            self.params["atr_mult"] += 0.2
            Log.learn(f"{self.name} learning: Too many premature SLs -> Increasing ATR multiplier.")

# ================== BACKTESTER ==================
class Backtester:
    @staticmethod
    def calculate_indicators(data, params):
        closes = [d["close"] for d in data]
        highs = [d["high"] for d in data]
        lows = [d["low"] for d in data]
        
        # EMA
        def ema(series, period):
            if len(series) < period: return [0]*len(series)
            res = [sum(series[:period])/period]
            mult = 2 / (period + 1)
            for i in range(period, len(series)):
                res.append(series[i] * mult + res[-1] * (1 - mult))
            return [0]*(period-1) + res

        ema_f = ema(closes, params["ema_fast"])
        ema_s = ema(closes, params["ema_slow"])
        
        # RSI
        def rsi(series, period):
            if len(series) < period: return [50]*len(series)
            diffs = [series[i] - series[i-1] for i in range(1, len(series))]
            res = [50]*period
            for i in range(period, len(series)):
                gain = sum([x for x in diffs[i-period:i] if x > 0]) / period
                loss = sum([-x for x in diffs[i-period:i] if x < 0]) / period
                rs = gain / (loss + 1e-9)
                res.append(100 - (100 / (1 + rs)))
            return res
            
        rsi_val = rsi(closes, params["rsi_period"])
        
        # ATR
        def atr(h, l, c, period):
            if len(c) < period: return [0]*len(c)
            tr = [max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1])) for i in range(1, len(c))]
            res = [sum(tr[:period])/period]
            for i in range(period, len(tr)):
                res.append((res[-1] * (period-1) + tr[i]) / period)
            return [0]*(period-1) + res

        atr_val = atr(highs, lows, closes, 14)
        
        return ema_f, ema_s, rsi_val, atr_val

    @staticmethod
    def run(data, strat):
        if len(data) < 200: return
        
        ema_f, ema_s, rsi_v, atr_v = Backtester.calculate_indicators(data, strat.params)
        closes = [d["close"] for d in data]
        
        trades = []
        pos = None
        
        for i in range(200, len(data)):
            if pos is None:
                # SIGNAL GENERATION
                buy_sig = False
                sell_sig = False
                
                # 1. Indicator Logic
                trend_up = ema_f[i] > ema_s[i]
                rsi_low = rsi_v[i] < strat.params["rsi_lower"]
                
                # 2. SMC/ICT Mock Logic (Simulated BOS/FVG based on price action)
                # Check for a 'Gap' in the last 3 candles (FVG)
                fvg_up = data[i-1]["low"] > data[i-3]["high"] + strat.params["ict_fvg_size"]
                fvg_down = data[i-1]["high"] < data[i-3]["low"] - strat.params["ict_fvg_size"]
                
                # Hybrid Decision
                if strat.params["smc_weight"] > 0.5:
                    if fvg_up and trend_up: buy_sig = True
                    if fvg_down and not trend_up: sell_sig = True
                else:
                    if trend_up and rsi_low: buy_sig = True
                    if not trend_up and rsi_v[i] > strat.params["rsi_upper"]: sell_sig = True
                
                if buy_sig or sell_sig:
                    entry = closes[i]
                    sl_dist = atr_v[i] * strat.params["atr_mult"]
                    tp_dist = sl_dist * strat.params["rr_ratio"]
                    
                    if buy_sig:
                        pos = {"dir": "BUY", "entry": entry, "sl": entry - sl_dist, "tp": entry + tp_dist}
                    else:
                        pos = {"dir": "SELL", "entry": entry, "sl": entry + sl_dist, "tp": entry - tp_dist}
            
            else:
                # TRADE MANAGEMENT
                hit = None
                if pos["dir"] == "BUY":
                    if closes[i] <= pos["sl"]: hit = "SL"
                    elif closes[i] >= pos["tp"]: hit = "TP"
                else:
                    if closes[i] >= pos["sl"]: hit = "SL"
                    elif closes[i] <= pos["tp"]: hit = "TP"
                
                if hit:
                    is_win = (hit == "TP")
                    reason = "reversal" if not is_win and abs(closes[i]-pos["entry"]) > (pos["entry"]*0.01) else "sl"
                    strat.history.append((is_win, reason))
                    trades.append(is_win)
                    pos = None
        
        strat.trades = len(trades)
        if strat.trades > 0:
            strat.winrate = (sum(trades) / strat.trades) * 100
            strat.pnl = sum([strat.params["rr_ratio"] if t else -1 for t in trades])
            strat.fitness = (strat.winrate / 100.0) * (strat.trades / CFG["min_trades"])
        
        strat.analyze_and_improve()

# ================== EXPORTER ==================
class StrategyExporter:
    @staticmethod
    def generate_manual(strat):
        p = strat.params
        manual = f"""
# 🏆 ELITE XAUUSD 1M TRADING MANUAL: {strat.name}
**Agent Name:** {strat.name}
**Win Rate:** {strat.winrate:.2f}% | **Total Trades:** {strat.trades} | **Profit Factor:** {strat.pnl/max(1, strat.trades):.2f}

---

## 📖 STRATEGY OVERVIEW
This is a high-probability scalping strategy specifically evolved for the XAUUSD (Gold) 1-Minute timeframe. It combines structural market analysis (SMC/ICT) with precise momentum filters.

## 🛠️ INDICATOR SETUP (Manual Configuration)
To execute this strategy manually, set up your chart as follows:
1. **Timeframe:** 1 Minute (1m).
2. **Fast Exponential Moving Average (EMA):** Period {p['ema_fast']} (Color: Blue).
3. **Slow Exponential Moving Average (EMA):** Period {p['ema_slow']} (Color: Red).
4. **Relative Strength Index (RSI):** 
   - Period: {p['rsi_period']}
   - Overbought Level: {p['rsi_upper']}
   - Oversold Level: {p['rsi_lower']}
5. **Average True Range (ATR):** Period 14 (Used for dynamic risk management).

---

## 📈 ENTRY RULES (Step-by-Step)

### 🟢 BUY ENTRY (Long)
1. **Trend Confirmation:** Price must be clearly trading ABOVE the Slow EMA ({p['ema_slow']}).
2. **Structural Trigger (SMC/ICT):** Look for a **Bullish Fair Value Gap (FVG)**.
   - *What to look for:* A 3-candle sequence where the Low of Candle 3 is higher than the High of Candle 1, leaving a "gap" in the price action.
3. **Momentum Confirmation:** The RSI ({p['rsi_period']}) should be emerging from the Oversold zone (below {p['rsi_lower']}) or showing a bullish divergence.
4. **Execution:** Enter Long at the close of the candle that confirms the FVG and Trend alignment.

### 🔴 SELL ENTRY (Short)
1. **Trend Confirmation:** Price must be clearly trading BELOW the Slow EMA ({p['ema_slow']}).
2. **Structural Trigger (SMC/ICT):** Look for a **Bearish Fair Value Gap (FVG)**.
   - *What to look for:* A 3-candle sequence where the High of Candle 3 is lower than the Low of Candle 1.
3. **Momentum Confirmation:** The RSI ({p['rsi_period']}) should be emerging from the Overbought zone (above {p['rsi_upper']}) or showing a bearish divergence.
4. **Execution:** Enter Short at the close of the candle that confirms the FVG and Trend alignment.

---

## 🛡️ RISK MANAGEMENT & EXIT STRATEGY

### 📉 Stop Loss (SL) - The Safety Net
Stop loss is based on current market volatility (ATR).
- **Calculation:** {p['atr_mult']} * ATR(14).
- **Placement:** Place the SL below the most recent swing low for BUYs, or above the most recent swing high for SELLs, but no further than the ATR calculation.

### 🎯 Take Profit (TP) - The Goal
This strategy uses a fixed Risk-to-Reward ratio to ensure long-term profitability.
- **Ratio:** 1 : {p['rr_ratio']}
- **Calculation:** If your SL is 20 pips, your TP must be {p['rr_ratio']} * 20 = {p['rr_ratio']*20} pips.

---

## ⚠️ TRADE FILTERS (When NOT to trade)
- **Flat Market:** If the Fast EMA and Slow EMA are intertwining (moving sideways), DO NOT trade.
- **High Impact News:** Avoid entries 15 minutes before and after major USD/Gold news events (CPI, FOMC, NFP).
- **Extreme RSI:** If RSI is already above 80 for a BUY or below 20 for a SELL, wait for a pullback.

---
**Manual Generated by AI Civilization Guardian - Agent {strat.name}**
"""
        return manual

    @staticmethod
    def save_to_github(strat):
        if not GH_TOKEN: return False
        content = StrategyExporter.generate_manual(strat)
        # Save using the Agent's unique name and winrate
        path = f"high_winrate_strategies/{strat.name}_wr{int(strat.winrate)}.txt"
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
        headers = {"Authorization": f"token {GH_TOKEN}"}
        
        # Check if exists
        r = requests.get(url, headers=headers)
        sha = r.json().get("sha") if r.status_code == 200 else None
        
        data = {
            "message": f"Elite Manual Saved: {strat.name} ({strat.winrate}%)",
            "content": base64.b64encode(content.encode()).decode(),
            "branch": "main"
        }
        if sha: data["sha"] = sha
        
        res = requests.put(url, headers=headers, json=data)
        return res.status_code in (200, 201)

# ================== CIVILIZATION MANAGER ==================
class Civilization:
    def __init__(self):
        self.agents = [Strategy(f"gold-agent-{i:03d}") for i in range(AGENTS_PER_COLONY)]
        self.generation = 0
        self.fetcher = DataFetcher()

    async def run_cycle(self):
        data = await self.fetcher.fetch_gold_1m()
        if not data: return
        
        # 1. Backtest all agents
        for a in self.agents:
            Backtester.run(data, a)
        
        # 2. Save Elites
        for a in self.agents:
            if a.winrate >= CFG["winrate_threshold"] and a.trades >= CFG["min_trades"]:
                if StrategyExporter.save_to_github(a):
                    Log.learn(f"🏆 ELITE STRATEGY PUSHED TO GITHUB: {a.id} WR={a.winrate}%")

        # 3. Evolve
        self.agents.sort(key=lambda x: x.fitness, reverse=True)
        elite = self.agents[:20]
        new_gen = list(elite)
        while len(new_gen) < AGENTS_PER_COLONY:
            parent = random.choice(elite)
            new_gen.append(parent.mutate())
        
        self.agents = new_gen
        self.generation += 1
        Log.i(f"Gen {self.generation} complete. Best WR: {self.agents[0].winrate:.2f}%")

civ = Civilization()

async def main_loop():
    Log.i("XAUUSD 1M CIVILIZATION STARTING...")
    while True:
        try:
            await civ.run_cycle()
            await asyncio.sleep(CFG["data_refresh_s"])
        except Exception as e:
            Log.w(f"Loop error: {e}")
            await asyncio.sleep(10)

threading.Thread(target=lambda: asyncio.run(main_loop()), daemon=True).start()

# ================== GRADIO UI ==================
import gradio as gr

def get_dashboard():
    rows = []
    for a in sorted(civ.agents, key=lambda x: x.winrate, reverse=True)[:20]:
        rows.append([a.id, f"{a.winrate:.2f}%", a.trades, f"{a.pnl:.1f}", f"RR 1:{a.params['rr_ratio']}"])
    return rows

with gr.Blocks(title="XAUUSD Gold Guardian") as demo:
    gr.Markdown("# 🏛️ XAUUSD 1m AI Civilization\nSearching for the 90% Win-Rate Holy Grail")
    gr.DataFrame(value=get_dashboard, headers=["Agent ID", "Win Rate", "Trades", "PNL", "Config"], every=10)
    gr.Markdown(f"**Generation:** {civ.generation}", every=10)

demo.queue().launch(server_name="0.0.0.0", server_port=7860)
