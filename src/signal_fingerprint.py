import hashlib
import json

def make_signal_fingerprint(symbol, pattern, timeframe, direction):
    payload = {
        "symbol": symbol,
        "pattern": pattern,
        "timeframe": timeframe,
        "direction": direction,
    }
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()
