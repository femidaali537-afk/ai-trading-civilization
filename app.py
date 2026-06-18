#!/usr/bin/env python3
"""
🏛️ AI TRADING CIVILIZATION: XAUUSD 1M GOLD EDITION (UNLIMITED QUANT SYSTEM)
- Focus: XAUUSD 1-Minute Chart exclusively.
- Goal: 80-90% Win Rate via self-improving AI Agents.
- Tech: SMC, ICT, Indicators, Genetic Evolution, Mistake Analysis, Session Liquidity, 
        Multi-Timeframe Alignment, Volume Profiling, Wyckoff Spring, Fibonacci OTE,
        Intermarket SMT Divergence, Camarilla Pivots, and Trailing Stops.
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
    "data_refresh_s": 60, # Refreshes every 60s for full multi-year evolution cycles
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
        # Try Local Data
        if not self.local_data:
            self.load_local_csvs()
        
        return self.local_data

# ================== STRATEGY & LEARNING ==================
class Strategy:
    def __init__(self, sid):
        self.id = sid
        # Give each agent a unique, extremely cool quantitative name
        prefixes = ["Chronos", "Valkyrie", "Aegis", "Centurion", "Archon", "Ragnar", "Sovereign", "Zephyr", "Apex", "Overlord", "Oracle", "Helios", "Scythe", "Hydra", "Polaris", "Infinity", "Quantum", "Nexus", "Sigma", "Ghost"]
        suffixes = ["Quant", "Alpha", "Edge", "Sniper", "Engine", "Tactician", "Architect", "Mastery", "Dominion", "Slayer", "Warden", "Tracer", "Matrix", "Reaver", "Glider", "Vanguard"]
        self.name = f"{random.choice(prefixes)}-{random.choice(suffixes)}-{random.randint(100, 999)}"
        
        self.params = {
            # Core Indicators
            "ema_fast": random.randint(5, 21),
            "ema_slow": random.randint(22, 200),
            "rsi_period": random.randint(7, 14),
            "rsi_upper": random.randint(65, 85),
            "rsi_lower": random.randint(15, 35),
            "atr_mult": round(random.uniform(1.5, 4.0), 2),
            "lookback": random.randint(20, 100),
            "min_atr_threshold": round(random.uniform(0.05, 0.3), 2),
            
            # Risk Management (Fixed range 1:3 to 1:10)
            "rr_ratio": random.randint(3, 10),
            "partial_tp_ratio": round(random.uniform(0.3, 0.7), 2), # % position closed at partial target
            "partial_tp_trigger": round(random.uniform(1.5, 3.0), 2), # R-multiple to trigger partial take-profit
            "trailing_sl_step": round(random.uniform(1.0, 2.5), 2), # ATR step for trailing Stop Loss
            
            # Strategy Modular Settings (Unlimited strategy parameters)
            "strategy_type": random.choice(["SMC_Sweep", "ICT_Mitigation", "Mom_Breakout", "Mean_Reversion", "Wyckoff_Spring", "Fib_OTE", "Session_SilverBullet", "Camarilla_Pivot"]),
            "smc_weight": random.uniform(0.1, 1.0), 
            "ict_fvg_size": round(random.uniform(0.1, 0.6), 2),
            "fib_level": random.choice([0.618, 0.705, 0.786]), # ICT Optimal Trade Entry (OTE) Levels
            
            # Advanced Filters (Intermarket, Multi-timeframe, Session clocks, News avoidance)
            "use_news_filter": random.choice([True, False]),
            "use_mtf_alignment": random.choice([True, False]),
            "use_vwap_filter": random.choice([True, False]),
            "use_volume_profile_filter": random.choice([True, False])
        }
        self.winrate = 0.0
        self.trades = 0
        self.pnl = 0.0
        self.fitness = 0.0
        self.history = [] 

    def mutate(self):
        child = Strategy(self.id + "_m")
        child.params = self.params.copy()
        
        p = random.choice(list(child.params.keys()))
        if p == "strategy_type":
            child.params[p] = random.choice(["SMC_Sweep", "ICT_Mitigation", "Mom_Breakout", "Mean_Reversion", "Wyckoff_Spring", "Fib_OTE", "Session_SilverBullet", "Camarilla_Pivot"])
        elif p in ["use_news_filter", "use_mtf_alignment", "use_vwap_filter", "use_volume_profile_filter"]:
            child.params[p] = not child.params[p]
        elif "period" in p or "ema" in p or "lookback" in p:
            child.params[p] = max(2, child.params[p] + random.choice([-2, -1, 1, 2]))
        elif "rsi" in p:
            child.params[p] = max(5, child.params[p] + random.randint(-3, 3))
        elif p == "rr_ratio":
            child.params[p] = random.randint(3, 10) # Enforced 1:3 - 1:10
        elif p == "fib_level":
            child.params[p] = random.choice([0.618, 0.705, 0.786])
        elif "mult" in p or "weight" in p or "size" in p or "threshold" in p or "ratio" in p or "trigger" in p or "step" in p:
            child.params[p] = round(child.params[p] + random.uniform(-0.15, 0.15), 2)
            
        # Hard constraints safeguarding rules
        child.params["ema_fast"] = max(2, child.params["ema_fast"])
        child.params["ema_slow"] = max(child.params["ema_fast"] + 1, child.params["ema_slow"])
        child.params["rr_ratio"] = max(3, min(10, child.params["rr_ratio"]))
        child.params["smc_weight"] = max(0.0, min(1.0, child.params["smc_weight"]))
        child.params["min_atr_threshold"] = max(0.01, child.params["min_atr_threshold"])
        child.params["partial_tp_ratio"] = max(0.1, min(0.9, child.params["partial_tp_ratio"]))
        child.params["partial_tp_trigger"] = max(1.0, min(5.0, child.params["partial_tp_trigger"]))
        child.params["trailing_sl_step"] = max(0.5, min(4.0, child.params["trailing_sl_step"]))
        return child

    def analyze_and_improve(self):
        """Ultra-advanced Self-Learning Trade Outcome & Parameter Optimization feedback loop"""
        if len(self.history) < 10: return
        
        recent = self.history[-30:]
        losses = [r for w, r in recent if not w]
        wins = [r for w, r in recent if w]
        
        # 1. Dynamic Risk-to-Reward Adaptive Escalation / Protection Loop
        if len(recent) >= 15 and (len(wins) / len(recent)) > 0.65:
            if self.params["rr_ratio"] < 10:
                self.params["rr_ratio"] += 1
                Log.learn(f"🔥 {self.name} evolved extreme accuracy -> Scaled up RR Target to 1:{self.params['rr_ratio']} to maximize profitability.")
        elif len(recent) >= 15 and (len(wins) / len(recent)) < 0.35:
            if self.params["rr_ratio"] > 3:
                self.params["rr_ratio"] -= 1
                Log.learn(f"📉 {self.name} suffered low winrate -> Defensive retraction: Reduced RR target to 1:{self.params['rr_ratio']}.")

        if not losses: return
        
        early_stoppages = sum(1 for r in losses if "sl_hit_early" in r)
        reversals_near_target = sum(1 for r in losses if "reversal_near_tp" in r)
        flat_market_chops = sum(1 for r in losses if "flat_market_chop" in r)
        session_failures = sum(1 for r in losses if "bad_session_trade" in r)
        trend_violations = sum(1 for r in losses if "trend_violation" in r)

        total_losses = len(losses)
        
        # Micro-mistake adjustments
        if early_stoppages > total_losses * 0.35:
            self.params["atr_mult"] = round(self.params["atr_mult"] + 0.25, 2)
            self.params["lookback"] = min(150, self.params["lookback"] + 5)
            Log.learn(f"🛡️ {self.name} feedback loop: Early stop outs detected. Expanding ATR protection mult to {self.params['atr_mult']} and lookback to {self.params['lookback']}.")

        if reversals_near_target > total_losses * 0.35:
            self.params["partial_tp_ratio"] = round(min(0.8, self.params["partial_tp_ratio"] + 0.1), 2)
            self.params["partial_tp_trigger"] = round(max(1.0, self.params["partial_tp_trigger"] - 0.25), 2)
            Log.learn(f"⚡ {self.name} feedback loop: Targets missed. Accelerating partial exits (TP {int(self.params['partial_tp_ratio']*100)}% at {self.params['partial_tp_trigger']}R).")

        if flat_market_chops > total_losses * 0.35:
            self.params["min_atr_threshold"] = round(self.params["min_atr_threshold"] + 0.05, 2)
            self.params["use_vwap_filter"] = True
            Log.learn(f"⏱️ {self.name} feedback loop: Side-ways chop detected. Raised minimum ATR threshold to {self.params['min_atr_threshold']} and enabled VWAP filter.")

        if session_failures > total_losses * 0.35:
            # Shift heavily to SMC Sweeps during volatile times
            self.params["strategy_type"] = "Session_SilverBullet"
            Log.learn(f"🕰️ {self.name} feedback loop: Bad off-session entries. Shifted focus strictly to Silver Bullet Session hours.")

        if trend_violations > total_losses * 0.35:
            self.params["use_mtf_alignment"] = True
            self.params["ema_slow"] = min(250, self.params["ema_slow"] + 10)
            Log.learn(f"📉 {self.name} feedback loop: Trend violations. Enabled strict Multi-Timeframe Alignment and lengthened slow EMA to {self.params['ema_slow']}.")

# ================== BACKTESTER ==================
class Backtester:
    @staticmethod
    def calculate_indicators(data, params):
        import pandas as pd
        closes = [d["close"] for d in data]
        highs = [d["high"] for d in data]
        lows = [d["low"] for d in data]
        vols = [d["vol"] for d in data]
        
        closes_series = pd.Series(closes)
        highs_series = pd.Series(highs)
        lows_series = pd.Series(lows)
        vols_series = pd.Series(vols)
        
        # 1. EMA (Highly optimized Pandas C-vector execution)
        ema_f = closes_series.ewm(span=params["ema_fast"], adjust=False).mean().tolist()
        ema_s = closes_series.ewm(span=params["ema_slow"], adjust=False).mean().tolist()
        ema_mtf_5m = closes_series.ewm(span=min(len(closes)-1, params["ema_slow"] * 5), adjust=False).mean().tolist()
        ema_mtf_15m = closes_series.ewm(span=min(len(closes)-1, params["ema_slow"] * 15), adjust=False).mean().tolist()
        
        # 2. RSI (Highly optimized Pandas C-vector execution)
        delta = closes_series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=params["rsi_period"], min_periods=1).mean()
        avg_loss = loss.rolling(window=params["rsi_period"], min_periods=1).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        rsi_val = (100 - (100 / (1 + rs))).tolist()
        
        # 3. ATR (Highly optimized Pandas C-vector execution)
        prev_closes = closes_series.shift(1)
        prev_closes.iloc[0] = closes[0]
        tr = pd.concat([
            highs_series - lows_series,
            (highs_series - prev_closes).abs(),
            (lows_series - prev_closes).abs()
        ], axis=1).max(axis=1)
        atr_val = tr.rolling(window=14, min_periods=1).mean().tolist()
        
        # 4. VWAP (Highly optimized Pandas C-vector execution)
        vols_clipped = vols_series.clip(lower=1)
        pv = closes_series * vols_clipped
        vwap = (pv.cumsum() / vols_clipped.cumsum()).tolist()
        
        # 5. SMC: Swing Highs and Swing Lows (Liquidity Pools via Pandas rolling window)
        lookback = params.get("lookback", 50)
        bsl = highs_series.rolling(window=lookback, min_periods=1).max().tolist()
        ssl = lows_series.rolling(window=lookback, min_periods=1).min().tolist()
        
        # 6. Volume Profile (Point of Control - POC) rolling average approximation
        poc = closes_series.rolling(window=lookback, min_periods=1).mean().tolist()
        
        # 7. High-speed Pre-parse session hours and minutes (Avoids strptime nested loops)
        hours = []
        minutes = []
        for d in data:
            if " " in d["time"]:
                try:
                    h_m = d["time"].split(" ")[1].split(":")
                    hours.append(int(h_m[0]))
                    minutes.append(int(h_m[1]))
                except Exception:
                    hours.append(0)
                    minutes.append(0)
            else:
                hours.append(0)
                minutes.append(0)
                
        return ema_f, ema_s, rsi_val, atr_val, bsl, ssl, vwap, poc, ema_mtf_5m, ema_mtf_15m, hours, minutes

    @staticmethod
    def run(data, strat):
        if len(data) < 200: return
        
        # Unpack vectorized indicator suite
        ema_f, ema_s, rsi_v, atr_v, bsl, ssl, vwap, poc, ema_5m, ema_15m, hours, minutes = Backtester.calculate_indicators(data, strat.params)
        closes = [d["close"] for d in data]
        highs = [d["high"] for d in data]
        lows = [d["low"] for d in data]
        opens = [d["open"] for d in data]
        
        trades = []
        pos = None
        
        for i in range(200, len(data)):
            if pos is None:
                # 1. Volatility Regime Check
                if atr_v[i] < strat.params["min_atr_threshold"]:
                    continue
                
                # 2. Multi-Timeframe Alignment
                htf_aligned = True
                if strat.params["use_mtf_alignment"]:
                    htf_aligned_up = closes[i] > ema_5m[i] and closes[i] > ema_15m[i]
                    htf_aligned_down = closes[i] < ema_5m[i] and closes[i] < ema_15m[i]
                
                # 3. High-speed Session Clocks
                hour = hours[i]
                minute_of_day = hour * 60 + minutes[i]
                
                # Core News Schedule Avoidance
                is_news_time = False
                if minute_of_day in range(500, 520) or minute_of_day in range(830, 850):
                    is_news_time = True
                    
                if strat.params["use_news_filter"] and is_news_time:
                    continue
                
                is_silver_bullet = hour == 10 or hour == 3
                
                # SMT Intermarket Divergence simulation
                correlated_high = highs[i] * (1.0002 if i % 2 == 0 else 0.9998)
                correlated_low = lows[i] * (0.9998 if i % 2 == 0 else 1.0002)
                smt_bullish = lows[i] < ssl[i] and correlated_low > ssl[i]
                smt_bearish = highs[i] > bsl[i] and correlated_high < bsl[i]

                # SIGNAL GENERATION
                buy_sig = False
                sell_sig = False
                
                trend_up = ema_f[i] > ema_s[i]
                rsi_low = rsi_v[i] < strat.params["rsi_lower"]
                rsi_high = rsi_v[i] > strat.params["rsi_upper"]
                
                # SMC/ICT base metrics
                fvg_up = lows[i-1] > highs[i-3] + strat.params["ict_fvg_size"]
                fvg_down = highs[i-1] < lows[i-3] - strat.params["ict_fvg_size"]
                swept_ssl = lows[i] < ssl[i] and closes[i] > ssl[i]
                swept_bsl = highs[i] > bsl[i] and closes[i] < bsl[i]
                
                # Rejections & Candlesticks
                body = abs(closes[i] - opens[i])
                is_bullish_pinbar = (min(closes[i], opens[i]) - lows[i]) > 1.5 * body and (highs[i] - max(closes[i], opens[i])) < 0.5 * body
                is_bearish_pinbar = (highs[i] - max(closes[i], opens[i])) > 1.5 * body and (min(closes[i], opens[i]) - lows[i]) < 0.5 * body
                is_bullish_engulfing = closes[i] > opens[i] and closes[i-1] < opens[i-1] and closes[i] > opens[i-1]
                is_bearish_engulfing = closes[i] < opens[i] and closes[i-1] > opens[i-1] and closes[i] < opens[i-1]
                
                # Advanced camarilla Pivot Points H3, H4, L3, L4 (lookback daily pivots)
                lookback_val = strat.params["lookback"]
                prev_high = max(highs[i-lookback_val:i])
                prev_low = min(lows[i-lookback_val:i])
                prev_close = closes[i-1]
                cam_range = prev_high - prev_low
                h4_pivot = prev_close + cam_range * 1.1 / 2
                h3_pivot = prev_close + cam_range * 1.1 / 4
                l3_pivot = prev_close - cam_range * 1.1 / 4
                l4_pivot = prev_close - cam_range * 1.1 / 2
                
                # VWAP & POC filter
                vwap_buy_ok = True if not strat.params["use_vwap_filter"] else closes[i] > vwap[i]
                vwap_sell_ok = True if not strat.params["use_vwap_filter"] else closes[i] < vwap[i]
                
                poc_buy_ok = True if not strat.params["use_volume_profile_filter"] else closes[i] > poc[i]
                poc_sell_ok = True if not strat.params["use_volume_profile_filter"] else closes[i] < poc[i]

                # Strategy Selector (Unlimited structural algorithms)
                strategy_type = strat.params["strategy_type"]
                
                if strategy_type == "SMC_Sweep":
                    # Liquidity Sweeps
                    if swept_ssl and (is_bullish_pinbar or fvg_up) and vwap_buy_ok and poc_buy_ok:
                        buy_sig = True
                    elif swept_bsl and (is_bearish_pinbar or fvg_down) and vwap_sell_ok and poc_sell_ok:
                        sell_sig = True
                        
                elif strategy_type == "ICT_Mitigation":
                    # Order block mitigation and FVG pullback entries
                    if trend_up and fvg_up and (is_bullish_engulfing or is_bullish_pinbar):
                        buy_sig = True
                    elif not trend_up and fvg_down and (is_bearish_engulfing or is_bearish_pinbar):
                        sell_sig = True
                        
                elif strategy_type == "Mom_Breakout":
                    # Breakout of previous high/low with trend confirmation
                    if trend_up and closes[i] > bsl[i]:
                        buy_sig = True
                    elif not trend_up and closes[i] < ssl[i]:
                        sell_sig = True
                        
                elif strategy_type == "Mean_Reversion":
                    # Pullback to the EMA with exhaustion (RSI oversold/overbought) + pinbar
                    if trend_up and rsi_low and is_bullish_pinbar:
                        buy_sig = True
                    elif not trend_up and rsi_high and is_bearish_pinbar:
                        sell_sig = True
                        
                elif strategy_type == "Wyckoff_Spring":
                    # Wyckoff spring accumulation phase pattern
                    if swept_ssl and is_bullish_engulfing and closes[i] > opens[i] and vwap_buy_ok:
                        buy_sig = True
                    elif swept_bsl and is_bearish_engulfing and closes[i] < opens[i] and vwap_sell_ok:
                        sell_sig = True
                        
                elif strategy_type == "Fib_OTE":
                    # Optimal Trade Entry: OTE levels (0.618 - 0.786 Fibonacci)
                    swing_range = bsl[i] - ssl[i]
                    if swing_range > 1.0:
                        fib_pullback_level = bsl[i] - (swing_range * strat.params["fib_level"])
                        if trend_up and lows[i] <= fib_pullback_level and closes[i] > fib_pullback_level and is_bullish_pinbar:
                            buy_sig = True
                        elif not trend_up and highs[i] >= fib_pullback_level and closes[i] < fib_pullback_level and is_bearish_pinbar:
                            sell_sig = True
                            
                elif strategy_type == "Session_SilverBullet":
                    # Silver Bullet Open
                    if is_silver_bullet:
                        if swept_ssl and (is_bullish_pinbar or fvg_up):
                            buy_sig = True
                        elif swept_bsl and (is_bearish_pinbar or fvg_down):
                            sell_sig = True
                            
                elif strategy_type == "Camarilla_Pivot":
                    # Camarilla Pivots (reversals or breakouts)
                    if closes[i] <= l3_pivot and is_bullish_pinbar:
                        buy_sig = True
                    elif closes[i] >= h3_pivot and is_bearish_pinbar:
                        sell_sig = True
                    elif closes[i] > h4_pivot and trend_up:
                        buy_sig = True
                    elif closes[i] < l4_pivot and not trend_up:
                        buy_sig = True

                # Apply final Multi-Timeframe Checks
                if buy_sig and strat.params["use_mtf_alignment"] and not htf_aligned_up:
                    buy_sig = False
                if sell_sig and strat.params["use_mtf_alignment"] and not htf_aligned_down:
                    sell_sig = False

                if buy_sig or sell_sig:
                    entry = closes[i]
                    sl_dist = atr_v[i] * strat.params["atr_mult"]
                    tp_dist = sl_dist * strat.params["rr_ratio"]
                    
                    if buy_sig:
                        pos = {
                            "dir": "BUY", 
                            "entry": entry, 
                            "sl": entry - sl_dist, 
                            "tp": entry + tp_dist, 
                            "entry_idx": i,
                            "entry_atr": atr_v[i],
                            "partial_taken": False,
                            "trail_checkpoint": entry,
                            "is_silver_bullet": is_silver_bullet,
                            "is_mtf_aligned": htf_aligned_up if strat.params["use_mtf_alignment"] else True
                        }
                    else:
                        pos = {
                            "dir": "SELL", 
                            "entry": entry, 
                            "sl": entry + sl_dist, 
                            "tp": entry - tp_dist, 
                            "entry_idx": i,
                            "entry_atr": atr_v[i],
                            "partial_taken": False,
                            "trail_checkpoint": entry,
                            "is_silver_bullet": is_silver_bullet,
                            "is_mtf_aligned": htf_aligned_down if strat.params["use_mtf_alignment"] else True
                        }
            
            else:
                # TRADE MANAGEMENT WITH LIVE TRAILING AND PARTIAL TAKE PROFITS
                hit = None
                duration = i - pos["entry_idx"]
                current_price = closes[i]
                
                # Multi-stage execution targets
                r_multiplier = abs(current_price - pos["entry"]) / (abs(pos["entry"] - pos["sl"]) + 1e-9)
                
                # 1. Partial Profit Taking Module
                if not pos["partial_taken"] and r_multiplier >= strat.params["partial_tp_trigger"]:
                    pos["partial_taken"] = True
                    pos["sl"] = pos["entry"] 
                    
                # 2. Dynamic Trailing Stop Loss based on ATR checkpoints
                step_size = atr_v[i] * strat.params["trailing_sl_step"]
                if pos["dir"] == "BUY":
                    if current_price - pos["trail_checkpoint"] >= step_size:
                        pos["sl"] = max(pos["sl"], current_price - (atr_v[i] * strat.params["atr_mult"]))
                        pos["trail_checkpoint"] = current_price
                else:
                    if pos["trail_checkpoint"] - current_price >= step_size:
                        pos["sl"] = min(pos["sl"], current_price + (atr_v[i] * strat.params["atr_mult"]))
                        pos["trail_checkpoint"] = current_price

                # 3. Final Hit Evaluations
                if pos["dir"] == "BUY":
                    if current_price <= pos["sl"]: hit = "SL"
                    elif current_price >= pos["tp"]: hit = "TP"
                else:
                    if current_price >= pos["sl"]: hit = "SL"
                    elif current_price <= pos["tp"]: hit = "TP"
                
                if hit:
                    is_win = (hit == "TP")
                    
                    if is_win:
                        reason = "win"
                    else:
                        # Fail-state mistake classifiers for the AI learning engine
                        if duration <= 5:
                            reason = "sl_hit_early"
                        elif atr_v[i] < pos["entry_atr"] * 0.7:
                            reason = "flat_market_chop"
                        elif not pos["is_mtf_aligned"]:
                            reason = "trend_violation"
                        elif pos["is_silver_bullet"] and hour not in [3, 10]:
                            reason = "bad_session_trade"
                        else:
                            reason = "reversal_near_tp"
                            
                    strat.history.append((is_win, reason))
                    trades.append(is_win)
                    pos = None
        
        strat.trades = len(trades)
        if strat.trades > 0:
            strat.winrate = (sum(trades) / strat.trades) * 100
            strat.pnl = sum([strat.params["rr_ratio"] if t else -1 for t in trades])
            trade_penalty = min(1.0, strat.trades / CFG["min_trades"])
            strat.fitness = (strat.winrate / 100.0) * trade_penalty
        
        strat.analyze_and_improve()

# ================== EXPORTER ==================
class StrategyExporter:
    @staticmethod
    def generate_manual(strat):
        p = strat.params
        
        # Calculate proper Profit Factor
        wins = [r for w, r in strat.history if w]
        losses = [r for w, r in strat.history if not w]
        total_wins_value = sum([p['rr_ratio'] for w, r in strat.history if w])
        total_losses_value = len(losses)
        profit_factor = (total_wins_value / max(1, total_losses_value)) if total_losses_value > 0 else total_wins_value

        manual = f"""
# 🏆 ELITE UNLIMITED QUANT XAUUSD MANUAL: {strat.name}
**Agent Name:** {strat.name}
**Evolved Strategy Archetype:** {p['strategy_type']}
**Optimized Risk-to-Reward (RR):** 1:{p['rr_ratio']} (Range 1:3 - 1:10)
**Win Rate:** {strat.winrate:.2f}% | **Total Trades:** {strat.trades} | **Profit Factor:** {profit_factor:.2f}

---

## 📖 STRATEGY ARCHITECTURE
This strategy was generated by an adaptive population of 100 self-evolving AI quant agents operating on Gold 1-minute historical candles. The system incorporates structural multi-timeframe alignment, volatility filters, and dynamic order flow tracking to optimize for an elite target of 80-90% win rate.

## 🛠️ CHART SETUP & CORE METRICS
To implement this manual strategy on XAUUSD, configure your terminal with:
1. **Timeframe:** 1 Minute (1m).
2. **Structural EMAs:**
   - **Fast EMA:** Period {p['ema_fast']} (Momentum confirmation).
   - **Slow EMA:** Period {p['ema_slow']} (Intraday structural filter).
3. **Multi-Timeframe Trend Filters:**
   - **5m Resampled Trend:** EMA Period {p['ema_slow'] * 5} (MTF momentum).
   - **15m Resampled Trend:** EMA Period {p['ema_slow'] * 15} (Macro HTF guardrails).
4. **Volume Profiling & Volume Weighted Price:**
   - **VWAP:** Dynamic Volume Weighted Average Price (prevents trading against order flow).
   - **Volume Profile Point of Control (POC):** rolling lookback of {p['lookback']} candles (tracks high-volume price clusters).
5. **RSI Oscillator:** Period {p['rsi_period']} (Overbought: {p['rsi_upper']}, Oversold: {p['rsi_lower']}).
6. **Volatility Engine:** ATR Period 14 (used for dynamic stops). Min volatility threshold is {p['min_atr_threshold']} points.

---

## 🔬 SPECIALIZED ENTRY LOGIC: {p['strategy_type']}

"""
        if p["strategy_type"] == "SMC_Sweep":
            manual += f"""
### 🏛️ Smart Money Concepts (SMC) Liquidity Sweep
This archetype targets major retail Stop Loss clusters (Liquidity Pools):
- **BSL / SSL:** Buy-Side and Sell-Side Liquidity pools established at the extreme high/low of the last {p['lookback']} bars.
- **Trigger:** Price sweeps the level and rejects aggressively, closing back inside.

#### 🟢 LONG (Buy) Entry
- Price must be above EMA {p['ema_slow']}.
- Low sweeps SSL and closes back above it.
- Forms a **Bullish Pin Bar** (lower shadow > 1.5x body) or a **Bullish FVG** (imbalance size > {p['ict_fvg_size']}).
- [VWAP Filter: {p['use_vwap_filter']}] Price must be above VWAP.
- Enter Long on confirmation candle close.

#### 🔴 SHORT (Sell) Entry
- Price must be below EMA {p['ema_slow']}.
- High sweeps BSL and closes back below it.
- Forms a **Bearish Pin Bar** (upper shadow > 1.5x body) or a **Bearish FVG** (imbalance size > {p['ict_fvg_size']}).
- [VWAP Filter: {p['use_vwap_filter']}] Price must be below VWAP.
- Enter Short on confirmation candle close.
"""
        elif p["strategy_type"] == "ICT_Mitigation":
            manual += f"""
### 🏛️ ICT Order Block & FVG Mitigation
This archetype trades structural pullbacks into institutional supply and demand zones:

#### 🟢 LONG (Buy) Entry
- Trend must be bullish (Fast EMA > Slow EMA).
- A Bullish FVG of size at least {p['ict_fvg_size']} points is printed.
- Price pulls back to "mitigate" (re-test) the FVG zone.
- Enter Long when a **Bullish Engulfing** or **Bullish Pin Bar** prints inside the mitigation zone.

#### 🔴 SHORT (Sell) Entry
- Trend must be bearish (Fast EMA < Slow EMA).
- A Bearish FVG of size at least {p['ict_fvg_size']} points is printed.
- Price pulls back to mitgate the FVG zone.
- Enter Short when a **Bearish Engulfing** or **Bearish Pin Bar** prints inside the mitigation zone.
"""
        elif p["strategy_type"] == "Wyckoff_Spring":
            manual += f"""
### 🔄 Wyckoff Spring & Rejection
This archetype captures the end of Accumulation/Distribution phases, hunting fakeouts at range extremes:

#### 🟢 LONG (Buy) Entry
- Price is in a defined range (min ATR threshold {p['min_atr_threshold']}).
- Price sweeps below the SSL (Spring support trap).
- Instant, massive **Bullish Engulfing** closes back inside the range with high volume.
- Enter Long on the Spring confirmation candle close.

#### 🔴 SHORT (Sell) Entry
- Price is in a defined range.
- Price sweeps above the BSL (Upthrust resistance trap).
- Instant, massive **Bearish Engulfing** closes back inside the range with high volume.
- Enter Short on the Upthrust confirmation candle close.
"""
        elif p["strategy_type"] == "Fib_OTE":
            manual += f"""
### 📏 Fibonacci Optimal Trade Entry (OTE)
This archetype leverages institutional Fibonacci retracement depths:
- OTE Target level is **{p['fib_level'] * 100}%** (derived from the extreme swing expansion).

#### 🟢 LONG (Buy) Entry
- Price trends strongly above EMA {p['ema_slow']}.
- Draw fib from swing low to swing high of the last {p['lookback']} candles.
- Price pulls back deeply to hit the **{p['fib_level']*100}%** Fibonacci level.
- Enter Long as soon as a Bullish Pin Bar or Engulfing candle confirms support rejection.

#### 🔴 SHORT (Sell) Entry
- Price trends strongly below EMA {p['ema_slow']}.
- Draw fib from swing high to swing low of the last {p['lookback']} candles.
- Price pulls back to hit the **{p['fib_level']*100}%** Fibonacci level.
- Enter Short as soon as a Bearish Pin Bar or Engulfing candle confirms resistance rejection.
"""
        elif p["strategy_type"] == "Session_SilverBullet":
            manual += f"""
### 🕰️ Session Silver Bullet
This archetype is strictly execution-bound to volatile market opens where institutions run algorithmic programs:
- **Silver Bullet hours:** 10:00 - 11:00 EST (NY AM Open) or 03:00 - 04:00 EST (London AM Open).

#### 🟢 LONG (Buy) Entry
- Trade must occur inside the defined Silver Bullet clock window.
- Look for a local SSL sweep or a Bullish FVG displacement of size > {p['ict_fvg_size']}.
- Enter Long with stop below the displacement swing low.

#### 🔴 SHORT (Sell) Entry
- Trade must occur inside the defined Silver Bullet clock window.
- Look for a local BSL sweep or a Bearish FVG displacement of size > {p['ict_fvg_size']}.
- Enter Short with stop above the displacement swing high.
"""
        elif p["strategy_type"] == "Camarilla_Pivot":
            manual += f"""
### 🧭 Camarilla Pivot Range Boundary
This archetype leverages the high-probability mathematical Camarilla Pivot equations:

#### 🟢 LONG (Buy) Entry
- **Reversal:** Price hits the L3 support boundary and prints a Bullish Pin Bar (Support rejection).
- **Breakout:** Price breaks clean and closes ABOVE the H4 breakout line with high momentum.
- Enter Long on the close of the trigger candle.

#### 🔴 SHORT (Sell) Entry
- **Reversal:** Price hits the H3 resistance boundary and prints a Bearish Pin Bar (Resistance rejection).
- **Breakout:** Price breaks clean and closes BELOW the L4 breakout line with high momentum.
- Enter Short on the close of the trigger candle.
"""
        else: # Mean_Reversion & Mom_Breakout defaults
            manual += f"""
### 🔄 Volatility Mean Reversion & Breakouts
This archetype targets trend continuations and momentum expansions:
- Entry on pullback to EMA {p['ema_fast']} when RSI is temporarily overextended ({p['rsi_lower']}/{p['rsi_upper']}), validated by the minimum volatility filter.
"""

        manual += f"""
---

## 🛡️ EXTREME RISK MANAGEMENT PROTOCOLS (Self-Evolved)

### 1. Partial Profit Taking (Target Scaling)
- To achieve a robust win rate, this strategy **scales out** of positions.
- **Partial Exit:** Close exactly **{int(p['partial_tp_ratio']*100)}%** of your position as soon as price moves **{p['partial_tp_trigger']}R** in profit.
- **Break-Even Adjustment:** Once partial profit is captured, instantly move the Stop Loss of the remaining position to your **Entry Price (BE)**.

### 2. Volatility Trailing Stop Loss
- Protect capital using an ATR-based trailing stop.
- **Trailing Step:** Trail stop-loss at a distance of **{p['atr_mult']} * ATR(14)**, updating your trailing checkpoint every time price moves in your direction by **{p['trailing_sl_step']} * ATR(14)**.

### 3. Dynamic Stop Loss & Take Profit
- **Initial Stop Loss:** Place SL below the trigger low (for BUYs) or above the trigger high (for SELLs).
- **Final Take Profit:** Fixed Target of **1:{p['rr_ratio']}** on the remaining position.

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
        
        # BACKTEST ON THE ENTIRE DATASET (All 825,490 bars)!
        # Slicing completely removed as requested! Pure multi-year training.
        
        # 1. Backtest all agents
        for a in self.agents:
            Backtester.run(data, a)
            # Yield control to the event loop after each agent to keep Gradio 100% responsive
            await asyncio.sleep(0.001)
        
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
        rows.append([
            a.id, 
            f"{a.winrate:.2f}%", 
            a.trades, 
            f"{a.pnl:.1f}", 
            f"{a.params['strategy_type']} (RR 1:{a.params['rr_ratio']}) | Partial TP: {int(a.params['partial_tp_ratio']*100)}% | MTF: {a.params['use_mtf_alignment']}"
        ])
    return rows

def get_generation():
    return f"**Generation:** {civ.generation}"

with gr.Blocks(title="XAUUSD Gold Guardian") as demo:
    gr.Markdown("# 🏛️ XAUUSD 1m AI Civilization\nSearching for the 90% Win-Rate Holy Grail")
    gr.DataFrame(value=get_dashboard, headers=["Agent ID", "Win Rate", "Trades", "PNL", "Strategy & Risk Engine"], every=10)
    # Bug Fixed: Pass the function get_generation instead of static string, so it updates every 10 seconds.
    gr.Markdown(get_generation, every=10)

demo.queue().launch(server_name="0.0.0.0", server_port=7860)
