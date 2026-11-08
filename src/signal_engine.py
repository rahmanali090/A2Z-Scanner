from src.coin_analysis import analyze_coin
from src.cross_exchange import get_cross_exchange_context
from src.anti_chase import evaluate_anti_chase
from src.emergency_intelligence import evaluate_market_shock


def build_signal_context(symbol):
    coin = analyze_coin(symbol)
    change = coin.get("change_percent", 0)
    return {
        "symbol": symbol,
        "coin": coin,
        "cross_exchange": get_cross_exchange_context(symbol),
        "anti_chase": evaluate_anti_chase(change),
        "emergency": evaluate_market_shock(change),
    }


def enrich_signal(symbol, direction, change_percent):
    context = build_signal_context(symbol)
    context["signal"] = {
        "direction": direction,
        "change_percent": float(change_percent or 0),
    }
    return context


def process_signal(symbol, direction, change_percent, timeframe=None, candle=None, pattern_data=None):
    import time as _to
    try:
        if _to.time() - globals().get("_OUT_T", 0) > 1800:
            globals()["_OUT_T"] = _to.time()
            from src.outcome_tracker import evaluate_pending
            evaluate_pending()
    except Exception as _oe:
        print("outcome tracker error:", _oe, flush=True)
    _sd = "LONG" if direction == "BULLISH" else "SHORT" if direction == "BEARISH" else "FLAT"
    import time as _t0
    if timeframe is None and _t0.time() - globals().setdefault("_COOL", {}).get((symbol, _sd), 0) < 14400:
        return {"symbol": symbol, "skipped": "cooldown"}
    signal = enrich_signal(symbol, direction, change_percent)
    if timeframe is None and candle is None and pattern_data is None:
        if abs(float(change_percent or 0)) < 1.5: return signal

    # NORMAL quality gate: deterministic checks only.
    if direction not in ("BULLISH", "BEARISH"):
        return signal
    if timeframe is None and candle is None and pattern_data is None:
        change = abs(float(change_percent or 0))
        anti = signal.get("anti_chase") or {}
        emergency = signal.get("emergency") or {}
        if change < 1.5:
            return signal
        if isinstance(anti, dict) and anti.get("triggered") is True:
            return signal
        if isinstance(emergency, dict) and emergency.get("triggered") is True:
            return signal

    if timeframe is not None and candle is not None and pattern_data is not None:
        from src.database import save_inverted_hammer_candidate
        save_inverted_hammer_candidate(symbol, timeframe, candle, pattern_data)

    from src.telegram_alerts import send_alert
    from src.market_intelligence import collect_binance_intelligence
    intel_cache = globals().setdefault("_INTEL_CACHE", {})
    now = _to.time()
    cached = intel_cache.get(symbol)
    if cached and now - cached["time"] < 300:
        signal["market_intelligence"] = cached["data"]
    else:
        data = collect_binance_intelligence(symbol)
        intel_cache[symbol] = {"time": now, "data": data}
        signal["market_intelligence"] = data

    price = float(signal.get("coin", {}).get("price") or 0)
    side = "LONG" if direction == "BULLISH" else "SHORT" if direction == "BEARISH" else "FLAT"

    from src.trend_filter import apply_trend_and_levels
    _lv = apply_trend_and_levels(symbol, side, price)
    if _lv and _lv.get("blocked"):
        return signal
    if _lv:
        stop_loss, tp1, tp2, tp3 = _lv["stop_loss"], _lv["tp1"], _lv["tp2"], _lv["tp3"]
    else:
        if side == "LONG":
            stop_loss = price * (1 - 0.015)
            tp1 = price * (1 + 0.02)
            tp2 = price * (1 + 0.035)
            tp3 = price * (1 + 0.05)
        elif side == "SHORT":
            stop_loss = price * (1 + 0.015)
            tp1 = price * (1 - 0.02)
            tp2 = price * (1 - 0.035)
            tp3 = price * (1 - 0.05)
        else:
            stop_loss = tp1 = tp2 = tp3 = price

    _sw = (_lv or {}).get("sweep")
    _sweep_line = ("Sweep: %s @ %s\n" % (_sw["pattern"], _sw["sweep_level"])) if _sw else ""
    price_precision = int(signal.get("coin", {}).get("price_precision", 4) or 4)
    formatted_price = lambda v: f"{v:.{price_precision}f}".rstrip("0").rstrip(".")
    price_text, sl_text = formatted_price(price), formatted_price(stop_loss)
    tp1_text, tp2_text, tp3_text = formatted_price(tp1), formatted_price(tp2), formatted_price(tp3)

    alert_text = (
        f"NORMAL SIGNAL ALERT\n"
        f"Coin: {symbol}\n"
        f"Direction: {side}\n"
        f"Entry: {price_text}\n"
        f"SL: {sl_text}\n"
        f"TP1 🎯: {tp1_text}\n"
        f"TP2 👙: {tp2_text}\n"
        f"TP3 🚀: {tp3_text}\n"
        f"Change: {change_percent}%\n"
        f"{_sweep_line}Manual verification required."
    )
    import time as _t
    _c=globals().setdefault("_COOL",{})
    _k=(symbol,side)
    if timeframe is None and _t.time()-_c.get(_k,0)<14400:
        return signal
    _c[_k]=_t.time()
    import json as _json
    from src.database import get_connection
    _sid=f"NORMAL-{symbol}-{side}-{int(_t.time())}"
    _db=get_connection();_db.execute("INSERT INTO signal_events (signal_id,event_type,state,event_timestamp,data) VALUES (?,?,?,?,?)",(_sid,"NORMAL_SIGNAL_EMITTED","CANDIDATE",_t.time(),_json.dumps({"symbol":symbol,"direction":side,"entry":price,"stop_loss":stop_loss,"tp1":tp1,"tp2":tp2,"tp3":tp3,"change_percent":change_percent})));_db.commit();_db.close()
    send_alert(alert_text)
    return signal
