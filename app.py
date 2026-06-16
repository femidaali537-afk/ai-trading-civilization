#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  🏛️  AI TRADING CIVILIZATION — 1000+ Agent Swarm            ║
║  XAUUSD + BTCUSD | 1m/3m/5m/15m | Multi-Colony Sync         ║
║  GitHub Shared DB | Duplicate = 3000 Agents | One Dashboard  ║
╚══════════════════════════════════════════════════════════════════╝

HOW IT WORKS:
  1. Each HF Space = 1 Colony (1000 agents)
  2. Duplicate Space → New Colony (another 1000)
  3. All colonies push stats to GitHub shared DB
  4. Dashboard shows ALL colonies combined

DUPLICATE SPACES - 3 Steps:
  1. HF Space → Settings → "Duplicate this Space"
  2. New Space → Settings → Repository secrets:
     COLONY_ID = colony-2  (unique for each duplicate)
  3. Factory reboot → auto-connects to same GitHub DB

DATA FLOW:
  Colony-1 (1000) ─┐
  Colony-2 (1000) ─┼→ GitHub Repo (shared DB) → Dashboard (all 3000)
  Colony-3 (1000) ─┘
"""

import asyncio, json, os, random, sys, time, warnings, threading, math, hashlib, base64
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# ═══════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════
GH_TOKEN = os.getenv("GH_TOKEN", "")  # Set in HF Space Secrets
GH_REPO = "femidaali537-afk/ai-trading-civilization"
GH_BRANCH = "main"
COLONY_ID = os.getenv("COLONY_ID", "colony-1")
AGENTS_PER_COLONY = int(os.getenv("AGENTS_PER_COLONY", "1000"))
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "120"))  # push to GitHub every 120s

CFG = {
    "symbols": ["XAUUSD=X", "BTC-USD"],
    "yf_symbols": {"XAUUSD": "GC=F", "BTCUSD": "BTC-USD"},
    "timeframes": ["1m", "3m", "5m", "15m"],
    "backtest_days": 30,     # 30 days of minute data
    "evolution_cycles": 5,   # evolve every 5 cycles
    "data_refresh_s": 60,
    "dashboard_refresh_s": 10,
}

# ═══════════════════════════════════════
# LOGGER
# ═══════════════════════════════════════
class Log:
    @staticmethod
    def i(m,*a): print(f"{datetime.now().strftime('%H:%M:%S')} | INFO  | {m%a if a else m}",flush=True)
    @staticmethod
    def w(m,*a): print(f"{datetime.now().strftime('%H:%M:%S')} | WARN  | {m%a if a else m}",flush=True)
    @staticmethod
    def e(m,*a): print(f"{datetime.now().strftime('%H:%M:%S')} | ERROR | {m%a if a else m}",flush=True)

# ═══════════════════════════════════════
# DATA FETCHER (Yahoo + Binance + Synthetic)
# ═══════════════════════════════════════
class DataFetcher:
    def __init__(self):
        self._yf=None
        try: import yfinance as yf; self._yf=yf; Log.i("📡 Yahoo Finance connected")
        except: Log.w("yfinance not installed")
        self._cache={}
        self._last_fetch={}

    async def fetch(self,symbol:str,tf:str="5m",days:int=30)->List[dict]:
        key=f"{symbol}:{tf}:{days}"
        now=time.time()
        if key in self._cache and now-self._last_fetch.get(key,0)<55: return self._cache[key]
        data=await self._fetch_yahoo(symbol,tf,days)
        if not data: data=await self._fetch_binance(symbol,tf,days)
        if not data: data=self._synth(symbol,days,tf)
        if data: self._cache[key]=data; self._last_fetch[key]=now
        return data

    async def _fetch_yahoo(self,symbol,tf,days):
        if not self._yf: return []
        try:
            yfs={"XAUUSD=X":"GC=F","BTC-USD":"BTC-USD"}.get(symbol,symbol)
            im={"1m":"1m","3m":"5m","5m":"5m","15m":"15m"}
            df=self._yf.Ticker(yfs).history(period=f"{days}d",interval=im.get(tf,"5m"))
            if df.empty: return []
            return [{"time":str(i.date()),"open":float(r.Open),"high":float(r.High),
                     "low":float(r.Low),"close":float(r.Close),"volume":float(r.get("Volume",0))}
                    for i,r in df.iterrows()]
        except: return []

    async def _fetch_binance(self,symbol,tf,days):
        try:
            import aiohttp
            bs={"XAUUSD=X":"PAXGUSDT","BTC-USD":"BTCUSDT"}.get(symbol,symbol)
            tm={"1m":"1m","3m":"3m","5m":"5m","15m":"15m"}
            lim=min(days*24*12,1000)
            url=f"https://api.binance.com/api/v3/klines?symbol={bs}&interval={tm.get(tf,'5m')}&limit={lim}"
            async with aiohttp.ClientSession() as s:
                async with s.get(url,timeout=10) as r:
                    if r.status!=200: return []
                    kl=await r.json()
                    return [{"time":str(k[0]),"open":float(k[1]),"high":float(k[2]),
                             "low":float(k[3]),"close":float(k[4]),"volume":float(k[5])} for k in kl]
        except: return []

    def _synth(self,symbol,days,tf="5m"):
        base={"XAUUSD=X":2650.0,"BTC-USD":68000.0}.get(symbol,100.0)
        vol=base*0.001
        data=[];now=datetime.utcnow();p=base
        tf_min={"1m":1,"3m":3,"5m":5,"15m":15}[tf]
        for i in range(days*24*60//tf_min,0,-1):
            t=now-timedelta(minutes=i*tf_min)
            p=max(p+random.gauss(0,vol),1.0)
            o=p;c=o+random.gauss(0,vol*0.3)
            h=max(o,c)+abs(random.gauss(0,vol*0.1))
            l=min(o,c)-abs(random.gauss(0,vol*0.1))
            data.append({"time":t.isoformat(),"open":o,"high":h,"low":l,"close":c,"volume":random.uniform(10,500)})
        return data

    def price(self,symbol):
        k=f"{symbol}:5m:30"
        if k in self._cache and self._cache[k]: return self._cache[k][-1]["close"]
        return {"XAUUSD=X":2650.0,"BTC-USD":68000.0}.get(symbol,100.0)

# ═══════════════════════════════════════
# TECHNICAL INDICATORS (Vectorized)
# ═══════════════════════════════════════
class TA:
    @staticmethod
    def sma(d,n): return sum(d[-n:])/n if len(d)>=n else d[-1]
    @staticmethod
    def ema(d,n):
        if len(d)<n: return d[-1]
        k=2/(n+1);e=sum(d[:n])/n
        for p in d[n:]: e=(p-e)*k+e
        return e
    @staticmethod
    def rsi(d,n=14):
        if len(d)<n+1: return 50.0
        g=[max(d[i]-d[i-1],0) for i in range(-n,0)]
        l=[max(d[i-1]-d[i],0) for i in range(-n,0)]
        ag,al=sum(g)/n,sum(l)/n
        return 100.0 if al==0 else 100-(100/(1+ag/al))
    @staticmethod
    def atr(h,l,c,n=14):
        if len(h)<n+1: return 0.01
        return sum(max(h[i]-l[i],abs(h[i]-c[i-1]),abs(l[i]-c[i-1])) for i in range(-n,0))/n
    @staticmethod
    def bollinger(d,n=20,k=2.0):
        if len(d)<n: return d[-1]*1.02,d[-1],d[-1]*0.98
        ma=TA.sma(d,n)
        std=(sum((x-ma)**2 for x in d[-n:])/n)**0.5
        return ma+k*std,ma,ma-k*std
    @staticmethod
    def adx(h,l,c,n=14):
        if len(c)<n+1: return 20.0
        trs,pdm,ndm=[],[],[]
        for i in range(-n,0):
            tr=max(h[i]-l[i],abs(h[i]-c[i-1]),abs(l[i]-c[i-1]))
            up=h[i]-h[i-1];dn=l[i-1]-l[i]
            pdm.append(up if up>dn and up>0 else 0)
            ndm.append(dn if dn>up and dn>0 else 0)
            trs.append(tr)
        atr=sum(trs)/n
        pdi=(sum(pdm)/n)/atr*100 if atr>0 else 0
        ndi=(sum(ndm)/n)/atr*100 if atr>0 else 0
        dx=abs(pdi-ndi)/(pdi+ndi)*100 if(pdi+ndi)>0 else 0
        return dx
    @staticmethod
    def macd(d):
        e12=TA.ema(d,12);e26=TA.ema(d,26)
        l=e12-e26
        return l,l,l-l

# ═══════════════════════════════════════
# STRATEGY = Just parameters + stats (lightweight)
# ═══════════════════════════════════════
class Strategy:
    __slots__=("id","params","fitness","trades","wins","pnl","pf","dd","winrate","gen")
    def __init__(self,sid,params=None):
        self.id=sid
        self.params=params or self._rand()
        self.fitness=0.0;self.trades=0;self.wins=0;self.pnl=0.0
        self.pf=0.0;self.dd=0.0;self.winrate=0.0;self.gen=0

    @staticmethod
    def _make_name(indicators):
        short={"rsi":"R","sma":"S","ema":"E","atr":"A","adx":"D","bb":"B","macd":"M","stoch":"K","cci":"C","mfi":"F","ichimoku":"I","vwap":"V","pivot":"P","fibonacci":"Fi","volume":"Vo","price_action":"PA"}
        parts=[short.get(i,i[:2].upper()) for i in indicators[:5]]
        return ''.join(parts[:4])+'_'+str(random.randint(100,999))

    def _rand(self):
        all_indicators=["rsi","sma","ema","atr","adx","bb","macd","stoch","cci","mfi","ichimoku","vwap","pivot","fibonacci","volume","price_action"]
        chosen=random.sample(all_indicators,random.randint(3,8))
        p={"_indicators":chosen,"_name":Strategy._make_name(chosen)}
        for ind in chosen:
            if ind=="rsi":p.update({"rsi_period":random.randint(5,30),"rsi_buy":random.randint(10,50),"rsi_sell":random.randint(50,90),"rsi_weight":round(random.uniform(0.2,3.0),2)})
            elif ind=="sma":p.update({"sma_fast":random.randint(2,60),"sma_slow":random.randint(10,300),"sma_weight":round(random.uniform(0.2,2.5),2)})
            elif ind=="ema":p.update({"ema_fast":random.randint(2,50),"ema_slow":random.randint(10,200),"ema_weight":round(random.uniform(0.2,2.5),2)})
            elif ind=="atr":p.update({"atr_period":random.randint(5,30),"atr_sl_mult":round(random.uniform(0.5,4.0),2),"atr_tp_mult":round(random.uniform(0.5,8.0),2)})
            elif ind=="adx":p.update({"adx_period":random.randint(7,30),"adx_threshold":random.randint(10,50),"adx_weight":round(random.uniform(0.3,2.5),2)})
            elif ind=="bb":p.update({"bb_period":random.randint(10,40),"bb_std":round(random.uniform(1.0,3.5),2),"bb_weight":round(random.uniform(0.3,2.5),2)})
            elif ind=="macd":p.update({"macd_fast":random.randint(5,20),"macd_slow":random.randint(15,40),"macd_signal":random.randint(5,15),"macd_weight":round(random.uniform(0.3,2.5),2)})
            elif ind=="stoch":p.update({"stoch_k":random.randint(5,21),"stoch_d":random.randint(3,9),"stoch_ob":random.randint(65,95),"stoch_os":random.randint(5,35)})
            elif ind=="volume":p.update({"vol_ma_period":random.randint(5,50),"vol_threshold":round(random.uniform(1.2,3.0),2)})
            elif ind=="price_action":p.update({"pa_sr_lookback":random.randint(10,100),"pa_breakout_pct":round(random.uniform(0.001,0.02),4)})
            elif ind=="ichimoku":p.update({"ichi_tk":random.randint(5,15),"ichi_kj":random.randint(20,40),"ichi_sb":random.randint(40,80)})
        p["rr_ratio"]=round(random.uniform(1.0,30.0),1)
        p["max_hold_bars"]=random.randint(5,200)
        p["trailing_stop"]=random.choice([True,False])
        p["ts_activation"]=round(random.uniform(0.3,0.8),2) if p["trailing_stop"] else 0
        p["signal_threshold"]=random.randint(2,7)
        return p

    def mutate(self):
        c=Strategy(f"{self.id}_m{random.randint(0,9999)}",dict(self.params))
        n=random.randint(1,5)
        keys=[k for k in list(c.params.keys()) if not k.startswith("_") and k!="rr_ratio"]
        if not keys:keys=["rr_ratio"]
        for _ in range(n):
            k=random.choice(keys);ov=c.params[k]
            if isinstance(ov,bool):c.params[k]=not ov
            elif isinstance(ov,(int,float)):
                cp=random.uniform(-0.5,0.5)
                if isinstance(ov,int):c.params[k]=max(1,int(ov*(1+cp)))
                else:c.params[k]=round(ov*(1+cp),4)
        c.params["rr_ratio"]=round(c.params.get("rr_ratio",2.0)*random.uniform(0.7,1.5),1)
        c.params["rr_ratio"]=max(1.0,min(30.0,c.params["rr_ratio"]))
        c.gen=self.gen+1;return c

    def crossover(self,other):
        cp={k:self.params[k] if random.random()<0.5 else other.params[k] for k in self.params if k in other.params}
        c=Strategy(f"{self.id}_x{random.randint(0,9999)}",cp)
        c.gen=max(self.gen,other.gen)+1;return c

    def to_dict(self):
        return {"id":self.id,"params":self.params,"fitness":self.fitness,"trades":self.trades,"wins":self.wins,"pnl":self.pnl,"pf":self.pf,"dd":self.dd,"wr":self.winrate,"gen":self.gen}

class Backtester:
    @staticmethod
    def _signal(closes,highs,lows,p):
        sc=0;pr=closes[-1]
        indicators = p.get("_indicators", ["rsi","sma","atr"])
        threshold = p.get("signal_threshold", 3)

        if "rsi" in indicators:
            rsi=TA.rsi(closes, p.get("rsi_period",14))
            if rsi<p.get("rsi_buy",35):sc+=p.get("rsi_weight",1.0)
            elif rsi>p.get("rsi_sell",65):sc-=p.get("rsi_weight",1.0)

        if "sma" in indicators:
            sf=TA.sma(closes,p.get("sma_fast",10))
            ss=TA.sma(closes,p.get("sma_slow",50))
            if sf>ss:sc+=p.get("sma_weight",1.0)
            else:sc-=p.get("sma_weight",1.0)

        if "ema" in indicators:
            ef=TA.ema(closes,p.get("ema_fast",8))
            es=TA.ema(closes,p.get("ema_slow",21))
            if ef>es:sc+=p.get("ema_weight",1.0)
            else:sc-=p.get("ema_weight",1.0)

        if "adx" in indicators:
            adx=TA.adx(highs,lows,closes,p.get("adx_period",14))
            if adx>p.get("adx_threshold",25):sc+=p.get("adx_weight",1.0) if pr>TA.sma(closes,20) else -p.get("adx_weight",1.0)

        if "bb" in indicators:
            bb_u,bb_m,bb_l=TA.bollinger(closes,p.get("bb_period",20),p.get("bb_std",2.0))
            bbw=(bb_u-bb_l)/bb_m if bb_m>0 else 1
            if pr<bb_l:sc+=p.get("bb_weight",1.0)
            elif pr>bb_u:sc-=p.get("bb_weight",1.0)

        if "macd" in indicators:
            ml,msl,mh=TA.macd(closes)
            if mh>0:sc+=p.get("macd_weight",1.0)
            else:sc-=p.get("macd_weight",1.0)

        if "stoch" in indicators:
            k_period=p.get("stoch_k",14)
            if len(closes)>=k_period:
                hh=max(highs[-k_period:]);ll=min(lows[-k_period:])
                stoch=((pr-ll)/(hh-ll)*100) if hh>ll else 50
                if stoch<p.get("stoch_os",20):sc+=1.5
                elif stoch>p.get("stoch_ob",80):sc-=1.5

        if "volume" in indicators:
            if len(closes)>=p.get("vol_ma_period",20):
                vol_avg=sum(1 for _ in range(p.get("vol_ma_period",20)))/p.get("vol_ma_period",20)
                if pr>TA.sma(closes,10):sc+=0.5

        if "price_action" in indicators:
            lookback=p.get("pa_sr_lookback",50)
            if len(closes)>=lookback:
                sr_low=min(lows[-lookback:]);sr_high=max(highs[-lookback:])
                if abs(pr-sr_low)/pr<p.get("pa_breakout_pct",0.005):sc+=1.5
                elif abs(pr-sr_high)/pr<p.get("pa_breakout_pct",0.005):sc-=1.5

        if sc>=threshold:return"BUY"
        if sc<=-threshold:return"SELL"
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

        for i in range(100, len(data) - 1):
            w = cl[max(0, i - 100):i + 1]
            hw = hi[max(0, i - 100):i + 1]
            lw = lo[max(0, i - 100):i + 1]
            cpw = cl[max(0, i - 14):i + 1]
            hpw = hi[max(0, i - 14):i + 1]
            lpw = lo[max(0, i - 14):i + 1]

            if pos is None:
                sig = Backtester._signal(w, hw, lw, p)
                if sig:
                    e = cl[i]
                    atr_val = TA.atr(hpw, lpw, cpw, p.get("atr_period", 14))
                    sl_mult = p.get("atr_sl_mult", 1.5)
                    tp_mult = p.get("atr_tp_mult", 3.0)
                    sd = atr_val * sl_mult
                    td = sd * p.get("rr_ratio", 2.0)

                    # FIX: Properly open the position
                    pos = {
                        "dir": sig,
                        "entry": e,
                        "sl": e - sd if sig == "BUY" else e + sd,
                        "tp": e + td if sig == "BUY" else e - td
                    }

            # Only check exits if we have an open position
            if pos is not None:
                hit = None
                if pos["dir"] == "BUY":
                    if lo[i] <= pos["sl"]:
                        hit = "SL"
                    elif hi[i] >= pos["tp"]:
                        hit = "TP"
                else:  # SELL
                    if hi[i] >= pos["sl"]:
                        hit = "SL"
                    elif lo[i] <= pos["tp"]:
                        hit = "TP"

                if hit:
                    ep = pos["sl"] if hit == "SL" else pos["tp"]
                    pnl = ((ep - pos["entry"]) if pos["dir"] == "BUY" else (pos["entry"] - ep)) / pos["entry"] * bal * 0.01
                    bal += pnl
                    peak = max(peak, bal)
                    trades.append({"win": pnl > 0, "pnl": pnl})
                    pos = None

        # Close any open position at the end
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
        fit = (wr / 100) * pf * max(0.1, 1 - dd / 50) * (min(n, 10) / 10)

        strat.trades = n
        strat.wins = ws
        strat.winrate = round(wr, 1)
        strat.pnl = round(tp, 2)
        strat.pf = round(pf, 2)
        strat.dd = round(dd, 1)
        strat.fitness = round(fit, 4)
        return strat

# ═══════════════════════════════════════
# GITHUB SYNC — Shared Database
# ═══════════════════════════════════════
class GitHubDB:
    """All colonies read/write to same GitHub repo."""
    def __init__(self):
        self.api=f"https://api.github.com/repos/{GH_REPO}/contents/colonies"
        self.headers={"Authorization":f"token {GH_TOKEN}","Accept":"application/vnd.github.v3+json"}
        self._session=None
        self.colony_file=f"colonies/{COLONY_ID}.json"
        self.all_file="colonies/_all.json"

    async def _get_session(self):
        if self._session is None:
            import aiohttp; self._session=aiohttp.ClientSession()
        return self._session

    async def push_agents(self,strategies:List[Strategy]):
        """Push this colony's agent data to GitHub."""
        try:
            agents_data=[s.to_dict() for s in strategies[:50]]  # Top 50
            payload={
                "colony_id":COLONY_ID,
                "ts":datetime.utcnow().isoformat(),
                "total_agents":len(strategies),
                "agents_data":agents_data[:500],"all_params_saved":len(strategies),
                "stats":{
                    "avg_wr":round(sum(s.winrate for s in strategies)/max(1,len(strategies)),1),
                    "best_wr":max(s.winrate for s in strategies) if strategies else 0,
                    "best_fitness":max(s.fitness for s in strategies) if strategies else 0,
                    "agents_above_70":sum(1 for s in strategies if s.winrate>=70),
                    "total_trades":sum(s.trades for s in strategies),
                }
            }
            content=json.dumps(payload)
            encoded=base64.b64encode(content.encode()).decode()

            # Check if file exists
            url=f"{self.api}/{COLONY_ID}.json"
            s=await self._get_session()
            sha=None
            async with s.get(url,headers=self.headers) as r:
                if r.status==200: sha=(await r.json()).get("sha")

            body={"message":f"🔄 {COLONY_ID} sync","content":encoded,"branch":GH_BRANCH}
            if sha: body["sha"]=sha
            async with s.put(url,headers=self.headers,json=body) as r:
                if r.status in (200,201): return True
            return False
        except: return False

    async def pull_all_colonies(self)->Dict:
        """Read all colony data from GitHub."""
        try:
            s=await self._get_session()
            url=f"{self.api}"
            async with s.get(url,headers=self.headers) as r:
                if r.status!=200: return {}
                files=await r.json()
            colonies={}
            for f in files:
                if f["name"].endswith(".json") and not f["name"].startswith("_"):
                    async with s.get(f["url"],headers=self.headers) as r2:
                        if r2.status==200:
                            data=json.loads(base64.b64decode((await r2.json())["content"]).decode())
                            colonies[f["name"].replace(".json","")]=data
            return colonies
        except: return {}

# ═══════════════════════════════════════
# POPULATION MANAGER — Handles 1000+ strategies
# ═══════════════════════════════════════
class PopulationManager:
    """Manages 1000+ strategies as a population (batch processing)."""
    def __init__(self):
        self.strategies:List[Strategy]=[]
        self.generation=0
        self.total_backtests=0
        self._spawn()

    def _spawn(self):
        # TRY RESTORE FROM DISK FIRST
        disk_path = Path(f"/tmp/civ_colony_{COLONY_ID}.json")
        restored = False
        if disk_path.exists():
            try:
                data = json.loads(disk_path.read_text())
                for sd in data.get("strategies", []):
                    s = Strategy(sd["id"], sd["params"])
                    s.fitness = sd.get("fitness", 0)
                    s.trades = sd.get("trades", 0)
                    s.wins = sd.get("wins", 0)
                    s.pnl = sd.get("pnl", 0)
                    s.pf = sd.get("pf", 0)
                    s.dd = sd.get("dd", 0)
                    s.winrate = sd.get("wr", 0)
                    s.gen = sd.get("gen", 0)
                    self.strategies.append(s)
                self.generation = data.get("generation", 0)
                self.total_backtests = data.get("total_backtests", 0)
                restored = True
                Log.i(f"💾 RESTORED {len(self.strategies)} strategies from disk (Gen {self.generation})")
            except Exception as e:
                Log.w(f"Disk restore failed: {e}")

        if not restored and GH_TOKEN:
            # TRY RESTORE FROM GITHUB
            try:
                Log.i("📡 Disk empty — trying GitHub restore...")
                import aiohttp, base64
                async def gh_restore():
                    url = f"https://api.github.com/repos/{GH_REPO}/contents/colonies/{COLONY_ID}.json"
                    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
                    async with aiohttp.ClientSession() as s:
                        async with s.get(url, headers=headers) as r:
                            if r.status == 200:
                                j = await r.json()
                                content = json.loads(base64.b64decode(j["content"]).decode())
                                agents = content.get("agents_data", []) or content.get("top_agents", [])
                                if agents:
                                    for sd in agents:
                                        st = Strategy(sd.get("id", "gh"), sd.get("params", {}))
                                        st.fitness = sd.get("fitness", 0); st.trades = sd.get("trades", 0)
                                        st.wins = sd.get("wins", 0); st.pnl = sd.get("pnl", 0)
                                        st.pf = sd.get("pf", 0); st.dd = sd.get("dd", 0)
                                        st.winrate = sd.get("wr", 0); st.gen = sd.get("gen", 0)
                                        self.strategies.append(st)
                                    self.generation = content.get("stats", {}).get("generation", 0) or content.get("generation", 0)
                                    self.total_backtests = content.get("stats", {}).get("total_backtests", 0)
                                    return True
                            return False
                loop = asyncio.new_event_loop()
                restored = loop.run_until_complete(gh_restore())
                loop.close()
                if restored:
                    Log.i(f"☁️  RESTORED {len(self.strategies)} strategies from GITHUB (Gen {self.generation})")
                else:
                    Log.w("GitHub restore failed — no colony data found")
            except Exception as e:
                Log.w(f"GitHub restore error: {e}")

        if not restored:
            half=AGENTS_PER_COLONY//2
            for i in range(half):
                for sym in CFG["symbols"]:
                    sym_short=sym.split('=')[0].split('-')[0]
                    sid=f"{COLONY_ID}_{sym_short}_{i:04d}"
                    self.strategies.append(Strategy(sid))
            Log.i(f"🧬 {len(self.strategies)} NEW strategies spawned in {COLONY_ID}")
        
        self._disk_path = disk_path

    async def backtest_all(self,fetcher:DataFetcher):
        """Batch backtest all strategies."""
        data_cache={}
        for sym in CFG["symbols"]:
            data_cache[sym]=await fetcher.fetch(sym,"5m",CFG["backtest_days"])
        for s in self.strategies:
            sym=s.id.split("_")[1]
            sym_key=[k for k in data_cache if sym in k][0] if any(sym in k for k in data_cache) else CFG["symbols"][0]
            if data_cache.get(sym_key):
                Backtester.run(data_cache[sym_key],s,sym)
        self.total_backtests+=len(self.strategies); self.save_to_disk()
        Log.i(f"🔬 {len(self.strategies)} strategies backtested [SAVED] 💾")

    def save_to_disk(self):
        try:
            data = {
                "colony_id": COLONY_ID,
                "ts": datetime.utcnow().isoformat(),
                "generation": self.generation,
                "total_backtests": self.total_backtests,
                "total_agents": len(self.strategies),
                "strategies": [{
                    "id": s.id, "params": s.params, "fitness": s.fitness,
                    "trades": s.trades, "wins": s.wins, "pnl": s.pnl,
                    "pf": s.pf, "dd": s.dd, "wr": s.winrate, "gen": s.gen
                } for s in self.strategies]
            }
            self._disk_path.write_text(json.dumps(data))
            return True
        except: return False

    def evolve(self):
        """Genetic evolution — top 25% survive, breed, replace bottom."""
        self.strategies.sort(key=lambda s:s.fitness,reverse=True)
        top_n=max(10,len(self.strategies)//4)
        elite=self.strategies[:top_n]
        new_strats=[]
        for _ in range(len(self.strategies)-top_n):
            parent=random.choice(elite)
            child=parent.mutate()
            if random.random()<0.3 and len(elite)>1:
                p2=random.choice([e for e in elite if e!=parent])
                child=parent.crossover(p2)
            child.id=f"{COLONY_ID}_gen{self.generation}_{len(new_strats):04d}"
            new_strats.append(child)
        self.strategies=elite+new_strats
        self.generation+=1; self.save_to_disk()
        Log.i(f"🧬 Gen {self.generation}: {len(elite)} survived + {len(new_strats)} new")

    def get_signals(self,closes,highs,lows,symbol,price):
        """Generate live signals from top strategies."""
        signals=[]
        for s in self.strategies[:200]:  # Top 200 only for signals
            sig=Backtester._signal(closes,highs,lows,s.params)
            if sig:
                atr_val=TA.atr(highs,lows,closes,s.params.get("atr_period",14))
                sl_mult=s.params.get("atr_sl_mult",1.5)
                tp_mult=s.params.get("atr_tp_mult",3.0)
                sd=atr_val*sl_mult;td=sd*s.params.get("rr_ratio",2.0)
                signals.append({
                    "agent":s.id,"symbol":symbol,"dir":sig,"price":price,
                    "sl":round(price-sd if sig=="BUY" else price+sd,2),
                    "tp":round(price+td if sig=="BUY" else price-td,2),
                    "confidence":min(0.95,s.winrate/100),"fitness":s.fitness
                })
        return signals

    def consensus(self,symbol,recent_signals):
        rel=[s for s in recent_signals[-200:] if s.get("symbol")==symbol]
        if not rel:return{"dir":"NEUTRAL","str":0,"n":0}
        b=sum(1 for s in rel if s["dir"]=="BUY")
        s=len(rel)-b;t=len(rel)
        return{"dir":"BUY" if b>s else "SELL" if s>b else "NEUTRAL",
               "str":round(max(b,s)/t*100,1),"n":t}

    def stats(self):
        ss=sorted(self.strategies,key=lambda s:s.fitness,reverse=True)
        return{
            "total":len(ss),"gen":self.generation,"backtests":self.total_backtests,
            "best_wr":max(s.winrate for s in ss) if ss else 0,
            "avg_wr":round(sum(s.winrate for s in ss)/max(1,len(ss)),1),
            "best_fit":ss[0].fitness if ss else 0,
            "above_70":sum(1 for s in ss if s.winrate>=70),
            "above_80":sum(1 for s in ss if s.winrate>=80),
            "above_90":sum(1 for s in ss if s.winrate>=90),
            "top5":[s.to_dict() for s in ss[:5]],
        }

# ═══════════════════════════════════════
# GLOBAL STATE
# ═══════════════════════════════════════
fetcher=DataFetcher()
pop=PopulationManager()
ghdb=GitHubDB()
recent_signals:List[Dict]=[]
all_colonies:Dict={}
_loop=None;_started=datetime.utcnow()
_tick=0

# ═══════════════════════════════════════
# MAIN LOOP (background thread)
# ═══════════════════════════════════════
async def main_loop():
    global _tick,recent_signals,all_colonies
    Log.i(f"🏛️  {COLONY_ID} online — {AGENTS_PER_COLONY} agents | XAUUSD+BTCUSD | 1m/3m/5m/15m")
    await pop.backtest_all(fetcher)

    while True:
        try:
            _tick+=1

            # Data refresh + signals (every 60s)
            if _tick%6==1:
                for sym in CFG["symbols"]:
                    try:
                        data=await fetcher.fetch(sym,"5m",3)
                        if data and len(data)>100:
                            cl=[d["close"] for d in data];hi=[d["high"] for d in data];lo=[d["low"] for d in data]
                            sigs=pop.get_signals(cl,hi,lo,sym,cl[-1])
                            recent_signals.extend(sigs)
                            if len(recent_signals)>2000:recent_signals=recent_signals[-1000:]
                    except:pass

            # Evolution (every 5th tick)
            if _tick%30==1:
                pop.evolve()

            # Backtest (every 10th tick)
            if _tick%60==1:
                await pop.backtest_all(fetcher)

            # GitHub sync (every SYNC_INTERVAL)
            if _tick%12==1:
                await ghdb.push_agents(pop.strategies)
                all_colonies=await ghdb.pull_all_colonies()
                pop.save_to_disk()  # Triple backup: disk + GitHub + stats

            await asyncio.sleep(10)
        except Exception as e:
            Log.e(f"Loop: {e}")
            await asyncio.sleep(10)

def start_loop():
    global _loop
    _loop=asyncio.new_event_loop();asyncio.set_event_loop(_loop)
    _loop.run_until_complete(main_loop())

threading.Thread(target=start_loop,daemon=True).start()
time.sleep(2)
Log.i(f"🚀 {COLONY_ID} running — {AGENTS_PER_COLONY} agents live")

# ═══════════════════════════════════════
# GRADIO DASHBOARD
# ═══════════════════════════════════════
import gradio as gr

def dashboard():
    ss=sorted(pop.strategies,key=lambda s:s.fitness,reverse=True)
    ps=pop.stats()
    xau_price=fetcher.price("XAUUSD=X")
    btc_price=fetcher.price("BTC-USD")

    # Consensus
    rel_xau=[s for s in recent_signals[-200:] if"XAU" in s.get("symbol","")]
    rel_btc=[s for s in recent_signals[-200:] if"BTC" in s.get("symbol","")]
    xau_b=sum(1 for s in rel_xau if s["dir"]=="BUY");xau_s=len(rel_xau)-xau_b
    btc_b=sum(1 for s in rel_btc if s["dir"]=="BUY");btc_s=len(rel_btc)-btc_b

    def con(n,b,s):
        if n==0:return("NEUTRAL","#888",0)
        d="BUY" if b>s else"SELL"
        c="#0f0" if d=="BUY" else"#f44"
        return(d,c,round(max(b,s)/n*100,1))

    xd,xc,xp=con(len(rel_xau),xau_b,xau_s)
    bd,bc,bp=con(len(rel_btc),btc_b,btc_s)

    # Top agents HTML
    # ALL AGENTS TABLE (scrollable)
    all_rows=""
    for i,s in enumerate(ss):
        wr=s.winrate;c="#0f0" if wr>=70 else"#ff0" if wr>=50 else"#f44"
        p=s.params
        # Agent's self-chosen name from its indicators
        style=p.get("_name","AUTO")
        sym_raw=s.id.split("_")[1] if len(s.id.split("_"))>1 else "?"
        sym_display="XAU" if "XAU" in sym_raw else "BTC" if "BTC" in sym_raw else sym_raw[:4]
        win=s.wins;loss=s.trades-s.wins;wlr=round(win/max(1,loss),2)
        all_rows+=f"""<div class="ar" title="Click for full strategy | Indicators: {p.get('_indicators',['?'])} | Threshold: {p.get('signal_threshold',3)} | RR: 1:{p.get('rr_ratio',2.0):.0f} | Trailing: {p.get('trailing_stop',False)}"><span class="rk">#{i+1}</span><span class="id">{s.id[-10:]}</span>
        <span class="sym">{sym_display}</span><span class="st">{style}</span>
        <span class="wr" style="color:{c}">{wr:.0f}%</span>
        <span class="td">{s.trades}</span><span class="wl">{win}W/{loss}L</span>
        <span class="rr">1:{p.get('rr_ratio',0):.0f}</span><span class="pf">PF:{s.pf:.1f}</span><span class="ft">F:{s.fitness:.3f}</span></div>"""

    # Colony cards
    colony_cards=""
    c_total=0;c_above70=0
    for cid,cd in all_colonies.items():
        c_total+=1
        st=cd.get("stats",{})
        c_above70+=st.get("agents_above_70",0)
        colony_cards+=f"""<div class="cc"><span class="ccn">🏛️ {cid}</span>
        <span class="ccs">{st.get('total_agents','?')} agents | Best: {st.get('best_wr','?')}% WR | ≥70%: {st.get('agents_above_70','?')}</span></div>"""
    if not colony_cards:colony_cards="""<div class="cc"><span class="ccn">🏛️ {COLONY_ID} (only)</span>
    <span class="ccs">Duplicate this HF Space → more colonies will appear here</span></div>"""

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>🏛️ AI Trading Civilization</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#060810;color:#c0c0c0;font-family:'Segoe UI',system-ui,monospace;min-height:100vh}}
.bnr{{background:linear-gradient(135deg,#0a1020,#0d2018);padding:16px;text-align:center;border-bottom:2px solid #0f0}}
.bnr h1{{color:#0f0;font-size:20px}} .bnr p{{color:#6a6;font-size:10px;margin-top:3px}}
.badge{{display:inline-block;background:#0f0;color:#000;padding:3px 10px;border-radius:10px;font-size:10px;font-weight:bold;margin:3px 2px}}
.pr{{display:flex;justify-content:center;gap:20px;padding:10px;background:#0a0c18;border-bottom:1px solid #1a1a33}}
.pc{{text-align:center;padding:8px 20px;background:#0d0d1a;border:1px solid #1a1a33;border-radius:8px}}
.pc .sym{{color:#0f0;font-size:14px;font-weight:bold}} .pc .val{{color:#fff;font-size:18px;font-weight:bold}}
.cn{{display:flex;justify-content:center;gap:15px;padding:8px}}
.cnb{{padding:4px 16px;border-radius:6px;font-size:12px;font-weight:bold}}
.sec{{padding:10px 15px}} .sec h2{{color:#0f0;font-size:13px;margin-bottom:6px;border-bottom:1px solid #1a1a33;padding-bottom:4px}}
.ar{{display:grid;grid-template-columns:30px 70px 30px 65px 40px 35px 50px 45px 45px 50px;gap:4px;padding:3px 8px;font-size:10px;border-bottom:1px solid #111;align-items:center}}
.ar:hover{{background:#111}}.ar .rk{{color:#888}}.ar .id{{color:#0cf;font-size:9px}}
.ar .wr{{font-weight:bold}}.ar .td{{color:#888}}.ar .pf{{color:#0cf;font-size:9px}}.ar .ft{{color:#0f0;font-size:9px}}
.sr{{display:flex;gap:12px;flex-wrap:wrap}}.sb{{background:#0d0d1a;border:1px solid #1a1a33;border-radius:8px;padding:8px 14px;text-align:center;min-width:90px}}
.sb .num{{color:#0f0;font-size:20px;font-weight:bold}}.sb .lbl{{color:#888;font-size:8px}}
.cc{{background:#0d0d1a;border:1px solid #1a1a33;border-radius:8px;padding:10px 14px;margin:6px 0}}
.cc .ccn{{color:#0f0;font-size:13px;font-weight:bold;display:block}}.cc .ccs{{color:#aaa;font-size:10px}}
.ar.hdr{{position:sticky;top:0;background:#0a0c18;z-index:10;border-bottom:2px solid #0f0;font-weight:bold;color:#0f0;font-size:9px}}
.wl{{color:#aaa;font-size:9px}}.rr{{color:#ff0;font-size:9px}}.st{{color:#aaa;font-size:8px}}.sym{{color:#ff0;font-weight:bold;font-size:10px}}
.ft{{text-align:center;padding:8px;color:#444;font-size:8px;border-top:1px solid #1a1a33;margin-top:8px}}
</style></head>
<body>
<div class="bnr"><h1>🏛️ AI TRADING CIVILIZATION</h1>
<p>XAUUSD + BTCUSD | 1000+ Agents per Colony | 1m/3m/5m/15m | Multi-Space Sync</p>
<span class="badge">🟢 {COLONY_ID}</span><span class="badge">🧬 Gen {ps['gen']}</span><span class="badge">🔬 {ps['backtests']}</span></div>

<div class="pr">
<div class="pc"><span class="sym">🥇 XAUUSD</span><br><span class="val">${xau_price:.2f}</span></div>
<div class="pc"><span class="sym">₿ BTCUSD</span><br><span class="val">${btc_price:.0f}</span></div>
</div>

<div class="cn">
<div class="cnb" style="background:{xc}20;color:{xc};border:1px solid{xc}">🥇 XAUUSD: <b>{xd}</b> ({xp}%/ {len(rel_xau)})</div>
<div class="cnb" style="background:{bc}20;color:{bc};border:1px solid{bc}">₿ BTCUSD: <b>{bd}</b> ({bp}%/ {len(rel_btc)})</div>
</div>

<div class="sec"><h2>🌍 ALL COLONIES ({c_total} connected)</h2>{colony_cards}</div>

<div class="sec"><h2>🏆 ALL {ps['total']} SELF-DESIGNED AGENTS ({COLONY_ID}) — Each agent creates its own strategy</h2>
<div style="max-height:500px;overflow-y:auto;border:1px solid #1a1a33;border-radius:8px;margin:5px 0">
<div class="ar hdr"><span>#</span><span>AGENT</span><span>SYM</span><span>STYLE</span><span>WR</span><span>TRD</span><span>W/L</span><span>RR</span><span>PF</span><span>FIT</span></div>
{all_rows}</div><div style="text-align:center;color:#888;font-size:9px;padding:2px">🖱️ Scroll to see all {ps['total']} agents | Hover any row for strategy details</div></div>


top5_strats=""
for i,s in enumerate(ss[:5]):
    wr=s.winrate;win=s.wins;loss=s.trades-s.wins
    p_clean={k:(round(v,4) if isinstance(v,float) else v) for k,v in s.params.items()}
    strat_json=json.dumps({"agent":s.id,"symbol":s.id.split("_")[1] if len(s.id.split("_"))>1 else "?","winrate":wr,"trades":s.trades,"wins":win,"losses":loss,"pf":s.pf,"fitness":s.fitness,"rr":"1:"+str(int(p_clean.get("rr_ratio",0))),"signal_threshold":p_clean.get("signal_threshold","?"),"trailing_stop":p_clean.get("trailing_stop","?"),"indicators":p_clean.get("_indicators",[]),"parameters":p_clean},indent=2)
    top5_strats+=f'''<div class="cc" style="cursor:pointer;margin:4px 0" onclick="var t=this.querySelector('pre');t.style.display=t.style.display==='none'?'block':'none'">
<span class="ccn" style="color:#0f0">#{i+1} {s.id[-12:]} — WR:{wr:.0f}% | Trades:{s.trades} | 1:{int(p_clean.get('rr_ratio',0))} | PF:{s.pf:.1f}</span>
<pre style="display:none;background:#000;color:#0f0;padding:8px;border-radius:4px;font-size:9px;margin-top:5px;white-space:pre-wrap;max-height:200px;overflow-y:auto">{strat_json}</pre></div>'''

<div class="sec"><h2>📋 TOP 5 STRATEGIES (Click to expand → Copy JSON)</h2>{top5_strats}</div>
<div class="sec"><h2>📊 {COLONY_ID} STATS</h2><div class="sr">
<div class="sb"><div class="num">{ps['total']}</div><div class="lbl">Agents</div></div>
<div class="sb"><div class="num">{ps['gen']}</div><div class="lbl">Generations</div></div>
<div class="sb"><div class="num">{ps['best_wr']:.0f}%</div><div class="lbl">Best WR</div></div>
<div class="sb"><div class="num">{ps['avg_wr']:.0f}%</div><div class="lbl">Avg WR</div></div>
<div class="sb"><div class="num">{ps['above_70']}</div><div class="lbl">≥70% WR</div></div>
<div class="sb"><div class="num">{ps['above_80']}</div><div class="lbl">≥80% WR</div></div>
<div class="sb"><div class="num">{ps['above_90']}</div><div class="lbl">≥90% WR</div></div>
<div class="sb"><div class="num">{ps['best_fit']:.3f}</div><div class="lbl">Best Fitness</div></div>
</div></div>

<div class="ft">🏛️ AI Trading Civilization | {c_total} Colonies | 1000+ Agents each | GitHub Synced | Duplicate Space → auto-merge<br>
How to add colony: Duplicate this Space → set COLONY_ID=colony-X → Factory reboot → auto-connects!</div>
</body></html>"""

with gr.Blocks(title="🏛️ AI Trading Civilization",theme=gr.themes.Soft(),css="footer{display:none!important}") as demo:
    gr.HTML(dashboard,every=8)

demo.queue(max_size=5)
demo.launch(server_name="0.0.0.0",server_port=7860,share=False,quiet=True)
