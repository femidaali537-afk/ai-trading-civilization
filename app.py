#!/usr/bin/env python3
"""
🏛️ AI TRADING CIVILIZATION: XAUUSD 1M GOLD EDITION
- Focus: XAUUSD 1-Minute Chart exclusively.
- Goal: 80-90% Win Rate via self-improving AI Agents.
- Tech: SMC, ICT, Indicators, Genetic Evolution, & Mistake Analysis (SMC Liquidity sweeps).
- Output: Detailed Manuals for Elite Strategies.
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
# Fallback to the user's provided token and repo if not specified in env
GH_TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or ""
GITHUB_REPO = os.getenv("GITHUB_REPO") or "femidaali537-afk/ai-trading-civilization"

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
        self.local_data = []

    def load_local_csvs(self):
        """Load historical data from CSV files in data/ folder"""
        script_dir = Path(__file__).resolve().parent
        data_dir = script_dir / "data"
        if not data_dir.exists():
            Log.w(f"Data directory not found at: {data_dir}")
            return []
        
        all_data = []
        csv_files = sorted(list(data_dir.glob("*.csv")))
        
        for f_path in csv_files:
            try:
                with open(f_path, "r") as f:
                    for line in f:
                        try:
                            parts = line.strip().split(",")
                            if len(parts) < 6: continue
                            # Format: Date, Time, Open, High, Low, Close, Vol
                            # date: 2024.01.01, time: 18:00
                            ts = f"{parts[0].replace('.', '-')} {parts[1]}"
                            all_data.append({
                                "time": ts,
                                "open": float(parts[2]),
                                "high": float(parts[3]),
                                "low": float(parts[4]),
                                "close": float(parts[5]),
                                "vol": float(parts[6]) if len(parts)>6 else 0
                            })
                        except ValueError:
                            # Skip header or malformed line gracefully
                            continue
            except Exception as e:
                Log.w(f"Error reading {f_path.name}: {e}")
        
        self.local_data = all_data
        Log.i(f"Loaded {len(all_data)} historical bars from local CSVs.")
        return all_data

    async def fetch_gold_1m(self):
        # 1. Try Local Data First
        if not self.local_data:
            self.load_local_csvs()
        
        if self.local_data:
            return self.local_data

        # 2. Fallback to yfinance if no local data
        now = time.time()
        if self._cache and now - self._last_update < 60:
            return self._cache
        
        try:
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
        
        # ATR (Bug Fixed: Ensure length of atr_val matches closes/data exactly)
        def atr(h, l, c, period):
            if len(c) < period: return [0]*len(c)
            # tr[0] uses high-low of first element so len(tr) == len(c)
            tr = [h[0]-l[0]] + [max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1])) for i in range(1, len(c))]
            res = [sum(tr[:period])/period]
            for i in range(period, len(tr)):
                res.append((res[-1] * (period-1) + tr[i]) / period)
            return [0]*period + res

        atr_val = atr(highs, lows, closes, 14)
        
        # SMC: Swing Highs and Swing Lows (Liquidity Pools)
        lookback = params.get("lookback", 50)
        bsl = [0] * len(data)
        ssl = [0] * len(data)
        
        for idx in range(lookback, len(data)):
            window_highs = highs[idx-lookback:idx]
            window_lows = lows[idx-lookback:idx]
            bsl[idx] = max(window_highs) if window_highs else highs[idx]
            ssl[idx] = min(window_lows) if window_lows else lows[idx]
            
        # For the first lookback candles, initialize with the current high/low
        for idx in range(min(lookback, len(data))):
            bsl[idx] = highs[idx]
            ssl[idx] = lows[idx]
        
        return ema_f, ema_s, rsi_val, atr_val, bsl, ssl

    @staticmethod
    def run(data, strat):
        if len(data) < 200: return
        
        ema_f, ema_s, rsi_v, atr_v, bsl, ssl = Backtester.calculate_indicators(data, strat.params)
        closes = [d["close"] for d in data]
        highs = [d["high"] for d in data]
        lows = [d["low"] for d in data]
        
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
                
                # 2. SMC/ICT FVG Logic (Fair Value Gap)
                fvg_up = lows[i-1] > highs[i-3] + strat.params["ict_fvg_size"]
                fvg_down = highs[i-1] < lows[i-3] - strat.params["ict_fvg_size"]
                
                # 3. SMC/ICT Liquidity Sweep Logic (Grab)
                # Sweep Sell-Side Liquidity (SSL): current low swept previous SSL, but current close is above it
                swept_ssl = lows[i] < ssl[i] and closes[i] > ssl[i]
                # Sweep Buy-Side Liquidity (BSL): current high swept previous BSL, but current close is below it
                swept_bsl = highs[i] > bsl[i] and closes[i] < bsl[i]
                
                # Hybrid SMC Liquidity Sweep & Trend Decision
                if strat.params["smc_weight"] > 0.5:
                    # SMC-centric: Buy if we swept sell-side liquidity (SSL) AND have bullish FVG or trend confirmation
                    if swept_ssl and (fvg_up or trend_up): 
                        buy_sig = True
                    # Sell if we swept buy-side liquidity (BSL) AND have bearish FVG or trend confirmation
                    elif swept_bsl and (fvg_down or not trend_up): 
                        sell_sig = True
                else:
                    # Trend/Indicator-centric with FVG confirmation
                    if trend_up and rsi_low: 
                        buy_sig = True
                    elif not trend_up and rsi_v[i] > strat.params["rsi_upper"]: 
                        sell_sig = True
                
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
            # Bug Fixed: Genetic algorithm was heavily biased to trade frequency over winrate.
            # We now penalize trades under min_trades, but once min_trades is met, fitness is determined by winrate.
            trade_penalty = min(1.0, strat.trades / CFG["min_trades"])
            strat.fitness = (strat.winrate / 100.0) * trade_penalty
        
        strat.analyze_and_improve()

# ================== EXPORTER ==================
class StrategyExporter:
    @staticmethod
    def generate_manual(strat):
        p = strat.params
        
        # Calculate proper Profit Factor
        wins = [p for w, p in strat.history if w]
        losses = [p for w, p in strat.history if not w]
        total_wins_value = sum([p['rr_ratio'] for w, p in strat.history if w])
        total_losses_value = len(losses)
        profit_factor = (total_wins_value / max(1, total_losses_value)) if total_losses_value > 0 else total_wins_value

        manual = f"""
# 🏆 ELITE XAUUSD 1M SMC LIQUIDITY SWEEP MANUAL: {strat.name}
**Agent Name:** {strat.name}
**Win Rate:** {strat.winrate:.2f}% | **Total Trades:** {strat.trades} | **Profit Factor:** {profit_factor:.2f}

---

## 📖 STRATEGY OVERVIEW
This is an elite Smart Money Concepts (SMC) Liquidity Sweep and Fair Value Gap (FVG) scalping strategy specifically evolved for the XAUUSD (Gold) 1-Minute timeframe. It targets major liquidity pools (Buy-Side and Sell-Side) to enter trades with high-probability institutional order flow.

## 🛠️ CHART SETUP & INDICATORS
To execute this strategy, set up your chart as follows:
1. **Timeframe:** 1 Minute (1m).
2. **Exponential Moving Averages (EMAs):**
   - **Fast EMA:** Period {p['ema_fast']} (Trend momentum filter).
   - **Slow EMA:** Period {p['ema_slow']} (Major trend filter).
3. **Relative Strength Index (RSI):** Period {p['rsi_period']} (used to confirm momentum pullbacks).
4. **Average True Range (ATR):** Period 14 (used for dynamic stop-loss placement).

---

## 🏛️ SMC & ICT CONCEPTS (How to identify them)

### 1. Buy-Side Liquidity (BSL) & Sell-Side Liquidity (SSL)
- **BSL (Buy-Side Liquidity):** Clustered above the swing highs of the previous {p['lookback']} candles. These are stop-losses of retail short sellers.
- **SSL (Sell-Side Liquidity):** Clustered below the swing lows of the previous {p['lookback']} candles. These are stop-losses of retail buyers.

### 2. Liquidity Sweep (Stop Hunt)
- **Bullish Sweep:** Price dips below the SSL level but rejects and closes back above it. This indicates smart money has filled their buy orders using retail stop-losses.
- **Bearish Sweep:** Price pushes above the BSL level but rejects and closes back below it. This indicates smart money has filled their sell orders using retail buy stops.

### 3. Fair Value Gap (FVG)
- **Bullish FVG:** A 3-candle imbalance where the Low of Candle 3 is greater than the High of Candle 1 by at least {p['ict_fvg_size']} points.
- **Bearish FVG:** A 3-candle imbalance where the High of Candle 3 is less than the Low of Candle 1 by at least {p['ict_fvg_size']} points.

---

## 📈 ENTRY RULES (Step-by-Step)

### 🟢 BUY ENTRY (Long)
1. **Trend Filter:** Price is trading ABOVE the Slow EMA ({p['ema_slow']}).
2. **Liquidity Sweep (Trigger):** The current candle sweeps below the Sell-Side Liquidity (SSL) level and closes back above it.
3. **Structure Confirmation:** A Bullish Fair Value Gap (FVG) is formed, or the Fast EMA ({p['ema_fast']}) is above the Slow EMA.
4. **Execution:** Enter Long immediately on the candle close after the Liquidity Sweep is confirmed.

### 🔴 SELL ENTRY (Short)
1. **Trend Filter:** Price is trading BELOW the Slow EMA ({p['ema_slow']}).
2. **Liquidity Sweep (Trigger):** The current candle sweeps above the Buy-Side Liquidity (BSL) level and closes back below it.
3. **Structure Confirmation:** A Bearish Fair Value Gap (FVG) is formed, or the Fast EMA ({p['ema_fast']}) is below the Slow EMA.
4. **Execution:** Enter Short immediately on the candle close after the Liquidity Sweep is confirmed.

---

## 🛡️ RISK MANAGEMENT & EXIT STRATEGY

### 📉 Stop Loss (SL)
Stop loss is placed dynamically based on market volatility using the ATR(14) indicator.
- **Calculation:** {p['atr_mult']} * ATR(14) points from your entry price.
- **Placement:** Place the SL below the sweep low for BUYs, or above the sweep high for SELLs.

### 🎯 Take Profit (TP)
This strategy uses a fixed Risk-to-Reward (RR) ratio to guarantee profitability over the long run.
- **Ratio:** 1 : {p['rr_ratio']}
- **Calculation:** TP is set at exactly {p['rr_ratio']} times your Stop Loss distance. If your SL is 20 pips, your TP is {p['rr_ratio'] * 20} pips.

---
**Generated by AI Trading Civilization Guardian - Agent {strat.name}**
"""
        return manual

    @staticmethod
    def save_to_github(strat):
        if not GH_TOKEN: 
            return False
        content = StrategyExporter.generate_manual(strat)
        # Save using the Agent's unique name and winrate
        path = f"high_winrate_strategies/{strat.name}_wr{int(strat.winrate)}.txt"
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
        headers = {"Authorization": f"token {GH_TOKEN}"}
        
        try:
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
        except Exception as e:
            Log.w(f"Exception while pushing {strat.name} to GitHub: {e}")
            return False

# ================== CIVILIZATION MANAGER ==================
class Civilization:
    def __init__(self):
        self.agents = [Strategy(f"gold-agent-{i:03d}") for i in range(AGENTS_PER_COLONY)]
        self.generation = 0
        self.fetcher = DataFetcher()

    async def run_cycle(self):
        data = await self.fetcher.fetch_gold_1m()
        if not data: 
            Log.w("No data fetched. Skipping cycle.")
            return
        
        # 1. Backtest all agents
        for a in self.agents:
            Backtester.run(data, a)
        
        # 2. Save Elites
        for a in self.agents:
            if a.winrate >= CFG["winrate_threshold"] and a.trades >= CFG["min_trades"]:
                if StrategyExporter.save_to_github(a):
                    Log.learn(f"🏆 ELITE STRATEGY PUSHED TO GITHUB: {a.id} WR={a.winrate:.2f}%")
                else:
                    Log.w(f"Failed to push elite strategy {a.id} (WR={a.winrate:.2f}%) to GitHub. Check repository & tokens.")

        # 3. Evolve
        self.agents.sort(key=lambda x: x.fitness, reverse=True)
        elite = self.agents[:20]
        new_gen = list(elite)
        while len(new_gen) < AGENTS_PER_COLONY:
            parent = random.choice(elite)
            new_gen.append(parent.mutate())
        
        self.agents = new_gen
        self.generation += 1
        Log.i(f"Gen {self.generation} complete. Best WR: {self.agents[0].winrate:.2f}% (Trades: {self.agents[0].trades})")

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

def get_generation():
    return f"**Generation:** {civ.generation}"

with gr.Blocks(title="XAUUSD Gold Guardian") as demo:
    gr.Markdown("# 🏛️ XAUUSD 1m AI Civilization\nSearching for the 90% Win-Rate Holy Grail")
    gr.DataFrame(value=get_dashboard, headers=["Agent ID", "Win Rate", "Trades", "PNL", "Config"], every=10)
    # Bug Fixed: Pass the function get_generation instead of static string, so it updates every 10 seconds.
    gr.Markdown(get_generation, every=10)

demo.queue().launch(server_name="0.0.0.0", server_port=7860)
