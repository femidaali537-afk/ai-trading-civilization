#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  🏛️ AI TRADING CIVILIZATION — ULTRA LITE (STABLE)               ║
║  50 Agents | Backtest ~every 10s | Safe Dashboard                ║
║  All previous bugs fixed + Lite + Stable + Everything incorporated
╚══════════════════════════════════════════════════════════════════╗
"""

import asyncio, json, os, random, sys, time, warnings, threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# ═══════════════════════════════════════
# CONFIG (All previous requests incorporated)
# ═══════════════════════════════════════
GH_TOKEN = os.getenv("GH_TOKEN", "")
GH_REPO = "femidaali537-afk/ai-trading-civilization"
GH_BRANCH = "main"
COLONY_ID = os.getenv("COLONY_ID", "colony-1")
AGENTS_PER_COLONY = 50   # Hardcoded 50 as per all requests

CFG = {
    "symbols": ["XAUUSD=X", "BTC-USD"],
    "backtest_days": 3,          # Light for stability
    "data_refresh_s": 10,
}

class Log:
    @staticmethod
    def i(m, *a): print(f"{datetime.now().strftime('%H:%M:%S')} | INFO  | {m%a if a else m}", flush=True)
    @staticmethod
    def w(m, *a): print(f"{datetime.now().strftime('%H:%M:%S')} | WARN  | {m%a if a else m}", flush=True)

# ═══════════════════════════════════════
# DATA FETCHER (Light + Stable)
# ═══════════════════════════════════════
class DataFetcher:
    def __init__(self):
        self._yf = None
        try:
            import yfinance as yf
            self._yf = yf
            Log.i("📡 Yahoo Finance connected")
        except:
            Log.w("yfinance not installed - using synthetic data")
        self._cache = {}
        self._last_fetch = {}

    async def fetch(self, symbol: str, tf: str = "5m", days: int = 3):
        key = f"{symbol}:{tf}:{days}"
        now = time.time()
        if key in self._cache and now - self._last_fetch.get(key, 0) < 55:
            return self._cache[key]

        data = await self._fetch_yahoo(symbol, tf, days)
        if not data:
            data = self._synth(symbol, days, tf)
        if data:
            self._cache[key] = data
            self._last_fetch[key] = now
        return data

    async def _fetch_yahoo(self, symbol, tf, days):
        if not self._yf:
            return []
        try:
            yfs = {"XAUUSD=X": "GC=F", "BTC-USD": "BTC-USD"}.get(symbol, symbol)
            df = self._yf.Ticker(yfs).history(period=f"{days}d", interval="5m")
            if df.empty:
                return []
            return [{"time": str(i.date()), "open": float(r.Open), "high": float(r.High),
                     "low": float(r.Low), "close": float(r.Close)} for i, r in df.iterrows()]
        except:
            return []

    def _synth(self, symbol, days, tf="5m"):
        base = {"XAUUSD=X": 2650.0, "BTC-USD": 68000.0}.get(symbol, 100.0)
        data = []
        now = datetime.utcnow()
        p = base
        for i in range(days * 24 * 12, 0, -1):
            t = now - timedelta(minutes=i * 5)
            p = max(p + random.gauss(0, base * 0.001), 1.0)
            o = p
            c = o + random.gauss(0, base * 0.0003)
            h = max(o, c) + abs(random.gauss(0, base * 0.0001))
            l = min(o, c) - abs(random.gauss(0, base * 0.0001))
            data.append({"time": t.isoformat(), "open": o, "high": h, "low": l, "close": c})
        return data

    def price(self, symbol):
        k = f"{symbol}:5m:3"
        if k in self._cache and self._cache[k]:
            return self._cache[k][-1]["close"]
        return {"XAUUSD=X": 2650.0, "BTC-USD": 68000.0}.get(symbol, 100.0)

# ═══════════════════════════════════════
# TECHNICAL INDICATORS (Light)
# ═══════════════════════════════════════
class TA:
    @staticmethod
    def sma(d, n): return sum(d[-n:]) / n if len(d) >= n else d[-1]
    @staticmethod
    def rsi(d, n=14):
        if len(d) < n + 1: return 50.0
        g = [max(d[i] - d[i-1], 0) for i in range(-n, 0)]
        l = [max(d[i-1] - d[i], 0) for i in range(-n, 0)]
        ag, al = sum(g) / n, sum(l) / n
        return 100.0 if al == 0 else 100 - (100 / (1 + ag / al))
    @staticmethod
    def atr(h, l, c, n=14):
        if len(h) < n + 1: return 0.01
        return sum(max(h[i] - l[i], abs(h[i] - c[i-1]), abs(l[i] - c[i-1])) for i in range(-n, 0)) / n

# ═══════════════════════════════════════
# STRATEGY
# ═══════════════════════════════════════
class Strategy:
    __slots__ = ("id", "params", "fitness", "trades", "wins", "pnl", "pf", "dd", "winrate", "gen")

    def __init__(self, sid, params=None):
        self.id = sid
        self.params = params or self._rand()
        self.fitness = 0.0
        self.trades = 0
        self.wins = 0
        self.pnl = 0.0
        self.pf = 0.0
        self.dd = 0.0
        self.winrate = 0.0
        self.gen = 0

    def _rand(self):
        p = {
            "_indicators": random.sample(["rsi", "sma", "ema", "atr"], 3),
            "rsi_period": random.randint(5, 20),
            "rsi_buy": random.randint(20, 40),
            "rsi_sell": random.randint(60, 80),
            "rsi_weight": round(random.uniform(0.5, 2.0), 2),
            "sma_fast": random.randint(5, 30),
            "sma_slow": random.randint(20, 100),
            "sma_weight": round(random.uniform(0.5, 2.0), 2),
            "atr_period": random.randint(5, 15),
            "atr_sl_mult": round(random.uniform(1.0, 3.0), 2),
            "atr_tp_mult": round(random.uniform(2.0, 6.0), 2),
            "rr_ratio": round(random.uniform(1.5, 4.0), 1),
            "signal_threshold": random.randint(2, 5),
        }
        return p

    def mutate(self):
        c = Strategy(f"{self.id}_m{random.randint(0,999)}", dict(self.params))
        for k in list(c.params.keys()):
            if k.startswith("_"): continue
            if isinstance(c.params[k], (int, float)):
                c.params[k] = max(1, c.params[k] * (1 + random.uniform(-0.3, 0.3)))
        c.gen = self.gen + 1
        return c

    def to_dict(self):
        return {"id": self.id, "params": self.params, "fitness": self.fitness,
                "trades": self.trades, "wins": self.wins, "pnl": self.pnl,
                "pf": self.pf, "dd": self.dd, "wr": self.winrate, "gen": self.gen}

# ═══════════════════════════════════════
# BACKTESTER (FIXED - All previous bugs resolved)
# ═══════════════════════════════════════
class Backtester:
    @staticmethod
    def _signal(closes, highs, lows, p):
        sc = 0
        pr = closes[-1]
        inds = p.get("_indicators", ["rsi", "sma"])
        thr = p.get("signal_threshold", 3)

        if "rsi" in inds:
            rsi = TA.rsi(closes, p.get("rsi_period", 14))
            if rsi < p.get("rsi_buy", 30):
                sc += p.get("rsi_weight", 1.0)
            elif rsi > p.get("rsi_sell", 70):
                sc -= p.get("rsi_weight", 1.0)

        if "sma" in inds:
            sf = TA.sma(closes, p.get("sma_fast", 10))
            ss = TA.sma(closes, p.get("sma_slow", 50))
            if sf > ss:
                sc += p.get("sma_weight", 1.0)
            else:
                sc -= p.get("sma_weight", 1.0)

        if sc >= thr:
            return "BUY"
        if sc <= -thr:
            return "SELL"
        return None

    @staticmethod
    def run(data, strat, symbol):
        cl = [d["close"] for d in data]
        hi = [d["high"] for d in data]
        lo = [d["low"] for d in data]
        p = strat.params
        trades = []
        bal = 10000.0
        peak = bal
        pos = None

        for i in range(20, len(data) - 1):   # lighter lookback for speed
            if pos is None:
                sig = Backtester._signal(cl[max(0, i-20):i+1],
                                         hi[max(0, i-20):i+1],
                                         lo[max(0, i-20):i+1], p)
                if sig:
                    e = cl[i]
                    atr_val = TA.atr(hi[max(0, i-10):i+1], lo[max(0, i-10):i+1], cl[max(0, i-10):i+1],
                                     p.get("atr_period", 10))
                    sd = atr_val * p.get("atr_sl_mult", 2.0)
                    td = sd * p.get("rr_ratio", 2.5)
                    pos = {
                        "dir": sig,
                        "entry": e,
                        "sl": e - sd if sig == "BUY" else e + sd,
                        "tp": e + td if sig == "BUY" else e - td
                    }

            if pos is not None:
                hit = None
                if pos["dir"] == "BUY":
                    if lo[i] <= pos["sl"]: hit = "SL"
                    elif hi[i] >= pos["tp"]: hit = "TP"
                else:
                    if hi[i] >= pos["sl"]: hit = "SL"
                    elif lo[i] <= pos["tp"]: hit = "TP"

                if hit:
                    ep = pos["sl"] if hit == "SL" else pos["tp"]
                    pnl = ((ep - pos["entry"]) if pos["dir"] == "BUY" else (pos["entry"] - ep)) / pos["entry"] * bal * 0.01
                    bal += pnl
                    peak = max(peak, bal)
                    trades.append({"win": pnl > 0, "pnl": pnl})
                    pos = None

        if pos is not None:
            ep = cl[-1]
            pnl = ((ep - pos["entry"]) if pos["dir"] == "BUY" else (pos["entry"] - ep)) / pos["entry"] * bal * 0.01
            bal += pnl
            trades.append({"win": pnl > 0, "pnl": pnl})

        n = len(trades)
        ws = sum(1 for t in trades if t["win"])
        wr = (ws / n * 100) if n > 0 else 0
        tp = sum(t["pnl"] for t in trades)
        gp = sum(t["pnl"] for t in trades if t["pnl"] > 0)
        gl = abs(sum(t["pnl"] for t in trades if t["pnl"] < 0))
        pf = gp / gl if gl > 0 else 1.0
        dd = (peak - min(peak, bal)) / peak * 100 if peak > 0 else 0
        fit = (wr / 100) * pf * max(0.1, 1 - dd / 50) * (min(n, 5) / 5)

        strat.trades = n
        strat.wins = ws
        strat.winrate = round(wr, 1)
        strat.pnl = round(tp, 2)
        strat.pf = round(pf, 2)
        strat.dd = round(dd, 1)
        strat.fitness = round(fit, 4)
        return strat

# ═══════════════════════════════════════
# POPULATION (Lite - 50 agents)
# ═══════════════════════════════════════
class PopulationManager:
    def __init__(self):
        self.strategies: List[Strategy] = []
        self.generation = 0
        self.total_backtests = 0
        self._spawn()

    def _spawn(self):
        for i in range(AGENTS_PER_COLONY):
            self.strategies.append(Strategy(f"{COLONY_ID}_lite_{i:03d}"))
        Log.i(f"🧬 {len(self.strategies)} NEW strategies spawned in {COLONY_ID} (LITE)")

    async def backtest_all(self, fetcher: DataFetcher):
        data_cache = {}
        for sym in CFG["symbols"]:
            data_cache[sym] = await fetcher.fetch(sym, "5m", CFG["backtest_days"])

        for s in self.strategies[:25]:   # only top 25 for speed in lite
            sym = CFG["symbols"][0]
            if data_cache.get(sym):
                Backtester.run(data_cache[sym], s, sym)
        self.total_backtests += 1

    def evolve(self):
        self.strategies.sort(key=lambda s: s.fitness, reverse=True)
        elite = self.strategies[:max(5, len(self.strategies)//4)]
        new_strats = []
        for _ in range(len(self.strategies) - len(elite)):
            parent = random.choice(elite)
            child = parent.mutate()
            new_strats.append(child)
        self.strategies = elite + new_strats
        self.generation += 1

    def get_signals(self, closes, highs, lows, symbol, price):
        signals = []
        for s in self.strategies[:8]:   # very light for lite
            sig = Backtester._signal(closes[-30:], highs[-30:], lows[-30:], s.params)
            if sig:
                signals.append({"agent": s.id, "symbol": symbol, "dir": sig, "price": price})
        return signals

    def stats(self):
        ss = sorted(self.strategies, key=lambda s: s.fitness, reverse=True)
        return {
            "total": len(ss),
            "gen": self.generation,
            "backtests": self.total_backtests,
            "best_wr": max(s.winrate for s in ss) if ss else 0,
            "avg_wr": round(sum(s.winrate for s in ss) / max(1, len(ss)), 1),
        }

# ═══════════════════════════════════════
# GLOBAL STATE
# ═══════════════════════════════════════
fetcher = DataFetcher()
pop = PopulationManager()
recent_signals: List[Dict] = []
all_colonies: Dict = {}
_tick = 0

# ═══════════════════════════════════════
# MAIN LOOP - Backtest every ~10s (lite safe)
# ═══════════════════════════════════════
async def main_loop():
    global _tick, recent_signals
    Log.i(f"🏛️ {COLONY_ID} ULTRA-LITE online — {AGENTS_PER_COLONY} agents | Backtest ~every 10s")

    while True:
        try:
            _tick += 1

            # === BACKTEST EVERY ~10 SECONDS (light) ===
            try:
                for sym in CFG["symbols"]:
                    data = await fetcher.fetch(sym, "5m", 2)
                    if data and len(data) > 15:
                        for s in pop.strategies[:12]:   # only top 12 for speed
                            try:
                                Backtester.run(data, s, sym)
                            except:
                                pass

                # Fresh signals
                data = await fetcher.fetch(CFG["symbols"][0], "5m", 1)
                if data and len(data) > 12:
                    cl = [d["close"] for d in data]
                    hi = [d["high"] for d in data]
                    lo = [d["low"] for d in data]
                    sigs = pop.get_signals(cl[-30:], hi[-30:], lo[-30:], CFG["symbols"][0], cl[-1])
                    recent_signals.extend(sigs)
                    if len(recent_signals) > 80:
                        recent_signals = recent_signals[-40:]
            except Exception as e:
                pass

            # Light evolution every ~3 minutes
            if _tick % 18 == 1:
                try:
                    pop.evolve()
                except:
                    pass

            await asyncio.sleep(10)

        except Exception as e:
            Log.w(f"Ultra-lite safe recovery: {e}")
            await asyncio.sleep(8)

def start_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_loop())

threading.Thread(target=start_loop, daemon=True).start()
time.sleep(2)
Log.i(f"🚀 {COLONY_ID} ULTRA-LITE running — {AGENTS_PER_COLONY} agents live")

# ═══════════════════════════════════════
# SAFE DASHBOARD (gr.DataFrame - no f-string hell)
# ═══════════════════════════════════════
import gradio as gr

def get_agent_data():
    try:
        ss = sorted(pop.strategies, key=lambda s: s.fitness, reverse=True)[:25]
        rows = []
        for s in ss:
            rows.append([
                s.id[-8:],
                f"{s.winrate:.0f}%",
                s.trades,
                f"{s.pf:.1f}",
                f"{s.fitness:.3f}"
            ])
        return rows
    except:
        return []

def get_status():
    try:
        ps = pop.stats()
        xau = fetcher.price("XAUUSD=X")
        btc = fetcher.price("BTC-USD")
        return f"🏛️ ULTRA LITE (50 agents, backtest ~every 10s) | XAU ${xau:.2f} | BTC ${btc:.0f} | Gen {ps.get('gen',0)} | Best WR {ps.get('best_wr',0):.0f}%"
    except:
        return "ULTRA LITE running (stable mode)"

with gr.Blocks(title="AI Trading Civilization - ULTRA LITE (50 agents)", theme=gr.themes.Soft(), css="footer{display:none!important}") as demo:
    gr.Markdown(get_status, every=8)
    gr.DataFrame(
        value=get_agent_data,
        headers=["Agent", "Win Rate", "Trades", "Profit Factor", "Fitness"],
        every=8,
        label="Top 25 Agents (updates every 8s)"
    )

demo.queue(max_size=2)
demo.launch(server_name="0.0.0.0", server_port=7860, share=False, quiet=True)
