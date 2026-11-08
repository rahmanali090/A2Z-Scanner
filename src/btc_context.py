BTC_CONTEXT_FIELDS = ("trend", "support", "resistance", "hh_hl", "lh_ll", "volume", "oi", "funding", "liquidations", "liquidity", "vwap", "momentum", "verified_catalysts", "relative_strength", "relative_weakness")
TIMEFRAMES = ("15m", "30m", "45m", "1h", "2h", "4h", "5h", "1d", "3d", "1w", "1M")

def build_btc_context(data=None):
    data = data or {}
    return {"timeframes": {tf: data.get(tf, {}) for tf in TIMEFRAMES}, "fields": {k: data.get(k) for k in BTC_CONTEXT_FIELDS}}

def btc_context_is_advisory(context):
    return True
