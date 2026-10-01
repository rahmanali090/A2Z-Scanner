import requests
from .config import BINANCE_BASE_URL

def get_price(symbol):
    r = requests.get(f"{BINANCE_BASE_URL}/fapi/v1/ticker/price", params={"symbol": symbol}, timeout=10)
    r.raise_for_status()
    return float(r.json()["price"])

def get_24h_ticker(symbol):
    r = requests.get(f"{BINANCE_BASE_URL}/fapi/v1/ticker/24hr", params={"symbol": symbol}, timeout=10)
    r.raise_for_status()
    return r.json()

def get_klines(symbol, interval, limit=100):
    r = requests.get(
        f"{BINANCE_BASE_URL}/fapi/v1/klines",
        params={"symbol": symbol, "interval": interval, "limit": limit},
        timeout=10
    )
    r.raise_for_status()
    return r.json()

def get_open_interest(symbol):
    r = requests.get(
        f"{BINANCE_BASE_URL}/fapi/v1/openInterest",
        params={"symbol": symbol},
        timeout=10
    )
    r.raise_for_status()
    return r.json()

def get_funding_rate(symbol):
    r = requests.get(
        f"{BINANCE_BASE_URL}/fapi/v1/premiumIndex",
        params={"symbol": symbol},
        timeout=10
    )
    r.raise_for_status()
    return r.json()

def get_order_book(symbol, limit=20):
    r = requests.get(
        f"{BINANCE_BASE_URL}/fapi/v1/depth",
        params={"symbol": symbol, "limit": limit},
        timeout=10
    )
    r.raise_for_status()
    return r.json()

def calculate_order_book_imbalance(symbol, limit=20):
    book = get_order_book(symbol, limit)
    bids = book.get("bids", [])
    asks = book.get("asks", [])
    bid_volume = sum(float(x[1]) for x in bids)
    ask_volume = sum(float(x[1]) for x in asks)
    total_volume = bid_volume + ask_volume
    imbalance_percent = ((bid_volume - ask_volume) / total_volume * 100) if total_volume else 0.0
    return {"symbol": symbol, "bid_volume": bid_volume, "ask_volume": ask_volume, "imbalance_percent": imbalance_percent}

def calculate_order_book_spread(symbol, limit=20):
    book = get_order_book(symbol, limit)
    bids = book.get("bids", [])
    asks = book.get("asks", [])
    if not bids or not asks:
        return {"symbol": symbol, "spread": 0.0, "spread_percent": 0.0}
    best_bid = float(bids[0][0])
    best_ask = float(asks[0][0])
    spread = best_ask - best_bid
    spread_percent = (spread / best_bid * 100) if best_bid else 0.0
    return {"symbol": symbol, "best_bid": best_bid, "best_ask": best_ask, "spread": spread, "spread_percent": spread_percent}

def get_exchange_info():
    r = requests.get(
        f"{BINANCE_BASE_URL}/fapi/v1/exchangeInfo",
        timeout=10
    )
    r.raise_for_status()
    return r.json()
def parse_klines(data):
    return [{"open_time": r[0], "open": float(r[1]), "high": float(r[2]), "low": float(r[3]), "close": float(r[4]), "volume": float(r[5]), "close_time": r[6], "quote_volume": float(r[7]), "trades": int(r[8])} for r in data]
def get_market_klines(symbol, intervals=("4h", "1h", "15m"), limit=100):
    return {interval: parse_klines(get_klines(symbol, interval, limit)) for interval in intervals}
def candle_stats(candles):
    if not candles:
        return {}
    return {
        "high": max(c["high"] for c in candles),
        "low": min(c["low"] for c in candles),
        "volume": sum(c["volume"] for c in candles),
        "last_close": candles[-1]["close"],
        "last_volume": candles[-1]["volume"],
    }
def candle_metrics(candles):
    if not candles:
        return {}
    last = candles[-1]
    return {
        "range": last["high"] - last["low"],
        "body": abs(last["close"] - last["open"]),
        "body_pct": abs(last["close"] - last["open"]) / last["open"] * 100,
        "volume_ratio": last["volume"] / (sum(c["volume"] for c in candles[:-1]) / max(len(candles) - 1, 1)) if len(candles) > 1 else 1.0,
    }
def parse_open_interest(data):
    return float(data["openInterest"])

def parse_funding_rate(data):
    return float(data["lastFundingRate"])
def parse_order_book(data):
    bids = [(float(p), float(q)) for p, q in data.get("bids", [])]
    asks = [(float(p), float(q)) for p, q in data.get("asks", [])]
    return {
        "bids": bids,
        "asks": asks,
        "best_bid": bids[0][0] if bids else None,
        "best_ask": asks[0][0] if asks else None,
    }
import time

def data_timestamp():
    return time.time()
def get_usdt_futures_symbols():
    info = get_exchange_info()
    return [
        s["symbol"] for s in info.get("symbols", [])
        if s.get("quoteAsset") == "USDT" and s.get("contractType") == "PERPETUAL" and s.get("status") == "TRADING"
    ]

def detect_inverted_hammer(candle):
    """Detect a completed Inverted Hammer candle as a LONG-side candidate."""
    if not candle:
        return None

    o = float(candle["open"])
    h = float(candle["high"])
    l = float(candle["low"])
    c = float(candle["close"])

    total_range = h - l
    if total_range <= 0:
        return None

    body = abs(c - o)
    upper_wick = h - max(o, c)
    lower_wick = min(o, c) - l

    body_ratio = body / total_range
    upper_wick_ratio = upper_wick / total_range
    lower_wick_ratio = lower_wick / total_range

    is_inverted_hammer = (
        body_ratio <= 0.35
        and upper_wick >= body * 2.0
        and lower_wick <= body
        and upper_wick_ratio >= 0.50
    )

    if not is_inverted_hammer:
        return None

    return {
        "pattern": "INVERTED_HAMMER",
        "direction": "LONG_CANDIDATE",
        "status": "PATTERN_DETECTED",
        "open": o,
        "high": h,
        "low": l,
        "close": c,
        "body": body,
        "upper_wick": upper_wick,
        "lower_wick": lower_wick,
        "body_ratio": body_ratio,
        "upper_wick_ratio": upper_wick_ratio,
        "lower_wick_ratio": lower_wick_ratio,
        "manual_verification_required": True,
    }

def scan_inverted_hammer(symbol, intervals=("1h", "4h", "6h", "12h", "1d", "1w", "1M"), limit=3):
    """Scan the latest completed candle for Inverted Hammer across required timeframes."""
    results = {}

    for interval in intervals:
        candles = parse_klines(get_klines(symbol, interval, limit))
        if len(candles) < 2:
            results[interval] = None
            continue

        completed_candle = candles[-2]
        result = detect_inverted_hammer(completed_candle)

        if result:
            result["symbol"] = symbol
            result["timeframe"] = interval
            result["candle_open_time"] = completed_candle["open_time"]
            result["candle_close_time"] = completed_candle["close_time"]

        results[interval] = result

    return results

def build_inverted_hammer_trade_levels(pattern):
    """Build deterministic LONG levels for a confirmed Inverted Hammer."""
    if not pattern:
        return None

    entry = float(pattern["close"])
    stop_loss = float(pattern["low"])
    risk = entry - stop_loss

    if entry <= stop_loss or risk <= 0:
        return None

    return {
        "entry": entry,
        "stop_loss": stop_loss,
        "risk": risk,
        "tp1": entry + (risk * 1.5),
        "tp2": entry + (risk * 2.0),
    }

def process_inverted_hammer_alert(symbol, pattern):
    if not pattern:
        return False

    from src.database import (
        save_inverted_hammer_candidate,
        inverted_hammer_alert_sent,
        mark_inverted_hammer_alert_sent,
    )
    from src.telegram_alerts import send_inverted_hammer_alert

    levels = build_inverted_hammer_trade_levels(pattern)
    if not levels:
        return False

    candle = {
        "open_time": pattern["candle_open_time"],
        "close_time": pattern["candle_close_time"],
        "open": pattern["open"],
        "high": pattern["high"],
        "low": pattern["low"],
        "close": pattern["close"],
    }

    signal_id = f"IH-{symbol}-{pattern['timeframe']}-{pattern['candle_open_time']}"

    save_inverted_hammer_candidate(
        symbol,
        pattern["timeframe"],
        candle,
        pattern,
    )

    if inverted_hammer_alert_sent(signal_id):
        return False

    alert_pattern = dict(pattern)
    alert_pattern["symbol"] = symbol

    sent = send_inverted_hammer_alert(alert_pattern, levels)

    if sent:
        mark_inverted_hammer_alert_sent(signal_id)

    return sent

def get_futures_market_status():
    info = get_exchange_info()
    return [
        {
            "symbol": s.get("symbol"),
            "status": s.get("status"),
            "quote_asset": s.get("quoteAsset"),
            "contract_type": s.get("contractType"),
            "onboard_date": s.get("onboardDate"),
            "delivery_date": s.get("deliveryDate"),
        }
        for s in info.get("symbols", [])
        if s.get("quoteAsset") == "USDT"
        and s.get("contractType") == "PERPETUAL"
    ]

def get_recent_futures_listings(since_timestamp):
    markets = get_futures_market_status()
    return [
        market for market in markets
        if market.get("onboard_date") is not None
        and market["onboard_date"] >= since_timestamp
    ]

def get_non_trading_futures_markets():
    markets = get_futures_market_status()
    return [
        market for market in markets
        if market.get("status") != "TRADING"
    ]

def detect_rapid_price_move(symbol, interval="15m", threshold_percent=2.0):
    candles = get_klines(symbol, interval=interval, limit=4)
    completed = candles[:-1]
    if len(completed) < 3:
        return None

    start_price = float(completed[-3][1])
    end_price = float(completed[-1][4])
    if start_price == 0:
        return None

    change_percent = ((end_price - start_price) / start_price) * 100

    if change_percent >= threshold_percent:
        direction = "PUMP"
    elif change_percent <= -threshold_percent:
        direction = "DUMP"
    else:
        direction = "NORMAL"

    return {
        "symbol": symbol,
        "interval": interval,
        "change_percent": round(change_percent, 4),
        "direction": direction,
    }

from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_rapid_price_moves(interval="15m", threshold_percent=2.0, max_workers=8):
    symbols = get_usdt_futures_symbols()
    results = []
    failures = []

    def scan(symbol):
        try:
            result = detect_rapid_price_move(
                symbol, interval=interval, threshold_percent=threshold_percent
            )
            return symbol, result, None
        except Exception as exc:
            return symbol, None, str(exc)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(scan, symbol) for symbol in symbols]
        for future in as_completed(futures):
            symbol, result, error = future.result()
            if error:
                failures.append({"symbol": symbol, "error": error})
            elif result and result["direction"] in ("PUMP", "DUMP"):
                results.append(result)

    return {
        "scanned": len(symbols),
        "signals": results,
        "failures": failures,
    }


def calculate_open_interest_change(symbol, interval_seconds=3):
    import time
    first = get_open_interest(symbol)
    time.sleep(interval_seconds)
    second = get_open_interest(symbol)
    before = float(first["openInterest"])
    after = float(second["openInterest"])
    change_percent = ((after - before) / before) * 100 if before else 0.0
    return {"symbol": symbol, "oi_before": before, "oi_after": after, "oi_change_percent": round(change_percent, 6)}
