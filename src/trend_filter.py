import requests
from src.binance_data import get_klines as _bn_klines, parse_klines

_OKX_TF = {"1m":"1m","5m":"5m","15m":"15m","30m":"30m","1h":"1H","2h":"2H","4h":"4H","6h":"6H","12h":"12H","1d":"1D"}
_KC_TF = {"1m":1,"5m":5,"15m":15,"30m":30,"1h":60,"2h":120,"4h":240,"8h":480,"12h":720,"1d":1440}

def _okx_candles(symbol, interval, limit):
    base = symbol[:-4] if symbol.endswith("USDT") else symbol
    r = requests.get("https://www.okx.com/api/v5/market/candles",
        params={"instId": base + "-USDT-SWAP", "bar": _OKX_TF[interval], "limit": min(limit, 300)}, timeout=6)
    r.raise_for_status()
    rows = r.json()["data"][::-1]
    return [{"open_time":int(x[0]),"open":float(x[1]),"high":float(x[2]),"low":float(x[3]),"close":float(x[4]),"volume":float(x[5])} for x in rows]

def _kucoin_candles(symbol, interval, limit):
    import time
    base = symbol[:-4] if symbol.endswith("USDT") else symbol
    base = "XBT" if base == "BTC" else base
    gran = _KC_TF[interval]
    now = int(time.time() * 1000)
    r = requests.get("https://api-futures.kucoin.com/api/v1/kline/query",
        params={"symbol": base + "USDTM", "granularity": gran, "from": now - limit * gran * 60000, "to": now}, timeout=6)
    r.raise_for_status()
    rows = r.json()["data"]
    return [{"open_time":int(x[0]),"open":float(x[1]),"high":float(x[2]),"low":float(x[3]),"close":float(x[4]),"volume":float(x[5])} for x in rows]

def fetch_candles(symbol, interval, limit):
    for fn in (_okx_candles, _kucoin_candles):
        try:
            c = fn(symbol, interval, limit)
            if c and len(c) >= 15:
                return c
        except Exception:
            pass
    return parse_klines(_bn_klines(symbol, interval, limit))

def calculate_ema(closes, period=200):
    if len(closes) < period:
        return sum(closes) / len(closes) if closes else 0.0
    m = 2 / (period + 1)
    ema = sum(closes[:period]) / period
    for c in closes[period:]:
        ema = (c - ema) * m + ema
    return ema

def calculate_atr(candles, period=14):
    if len(candles) < 2:
        return 0.0
    tr = []
    for i in range(1, len(candles)):
        h, l, pc = candles[i]["high"], candles[i]["low"], candles[i-1]["close"]
        tr.append(max(h - l, abs(h - pc), abs(l - pc)))
    return sum(tr[-period:]) / min(len(tr), period) if tr else 0.0

def build_dynamic_trade_levels(entry, candles, side="LONG", atr_multiplier=1.5):
    atr = calculate_atr(candles, 14)
    if atr <= 0:
        atr = entry * 0.015
    risk = atr * atr_multiplier
    g = 1 if side == "LONG" else -1
    return {
        "entry": entry,
        "stop_loss": entry - g * risk,
        "risk": risk,
        "tp1": entry + g * risk * 2.0,
        "tp2": entry + g * risk * 3.0,
        "tp3": entry + g * risk * 4.5,
    }

def apply_trend_and_levels(symbol, side, price):
    try:
        candles = fetch_candles(symbol, "1h", 250)[:-1]
        if price <= 0 or len(candles) < 50:
            return None
        closes = [c["close"] for c in candles]
        ema = calculate_ema(closes, 200)
        if len(closes) >= 200:
            if side == "LONG" and price <= ema:
                return {"blocked": True, "ema_200": ema}
            if side == "SHORT" and price >= ema:
                return {"blocked": True, "ema_200": ema}
        if not validate_volume_spike(candles[-21:], 1.5):
            return {"blocked": True, "reason": "low_volume", "ema_200": ema}
        if not verify_multi_timeframe_confluence(symbol, "BULLISH" if side == "LONG" else "BEARISH"):
            return {"blocked": True, "reason": "no_mtf_confluence", "ema_200": ema}
        lv = build_dynamic_trade_levels(price, candles, side)
        rm = calculate_institutional_risk_matrix(lv["entry"], lv["stop_loss"], [lv["tp1"], lv["tp2"], lv["tp3"]])
        if not rm or not rm.get("approved"):
            return {"blocked": True, "reason": "rrr_too_low", "ema_200": ema}
        lv["ema_200"] = ema
        try:
            sw = detect_liquidity_sweep(candles)
            if sw.get("sweep_detected") and sw.get("direction") == side + "_CANDIDATE":
                lv["sweep"] = sw
        except Exception:
            pass
        return lv
    except Exception:
        return None

def atr_levels_for_pattern(symbol, timeframe, entry):
    if not symbol or not timeframe:
        return None
    candles = fetch_candles(symbol, timeframe, 30)[:-1]
    if len(candles) < 15:
        return None
    return build_dynamic_trade_levels(entry, candles, "LONG")

def validate_volume_spike(candles, volume_multiplier=1.5):
    if len(candles) < 10:
        return True
    avg_volume = sum(float(c["volume"]) for c in candles[:-1]) / len(candles[:-1])
    return float(candles[-1]["volume"]) >= avg_volume * volume_multiplier


def verify_multi_timeframe_confluence(symbol, required_direction="BULLISH"):
    votes = []
    for tf in ("15m", "1h", "4h"):
        cs = fetch_candles(symbol, tf, 60)[:-1]
        if len(cs) < 50:
            return False
        closes = [c["close"] for c in cs]
        now = closes[-1]
        if tf == "15m":
            d = "BULLISH" if now > closes[-2] else "BEARISH"
        else:
            d = "BULLISH" if now > sum(closes[-50:]) / 50 else "BEARISH"
        votes.append(d == required_direction)
    return all(votes)

def detect_liquidity_sweep(candles, lookback=20):
    if len(candles) < lookback + 2:
        return {"sweep_detected": False, "direction": None}
    recent = candles[-(lookback + 2):-2]
    last = candles[-1]
    swing_high = max(float(c["high"]) for c in recent)
    swing_low = min(float(c["low"]) for c in recent)
    if float(last["low"]) < swing_low and float(last["close"]) > swing_low:
        return {"sweep_detected": True, "pattern": "BEAR_TRAP_LIQUIDITY_SWEEP", "direction": "LONG_CANDIDATE", "sweep_level": swing_low}
    if float(last["high"]) > swing_high and float(last["close"]) < swing_high:
        return {"sweep_detected": True, "pattern": "BULL_TRAP_LIQUIDITY_SWEEP", "direction": "SHORT_CANDIDATE", "sweep_level": swing_high}
    return {"sweep_detected": False, "direction": None}

def calculate_institutional_risk_matrix(entry, stop_loss, targets, account_balance=None, risk_percentage=1.0):
    risk = abs(entry - stop_loss)
    if risk <= 0 or not targets:
        return None
    rrr = abs(targets[0] - entry) / risk
    if rrr < 2.0 - 1e-9:
        return {"approved": False, "reason": "RRR %.2f below 2.0" % rrr}
    out = {"approved": True, "risk_to_reward_ratio": round(rrr, 2)}
    if account_balance:
        amt = account_balance * risk_percentage / 100.0
        out["risk_amount_usd"] = round(amt, 2)
        out["position_size_units"] = round(amt / risk, 4)
    return out
