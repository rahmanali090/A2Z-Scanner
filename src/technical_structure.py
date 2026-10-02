STRUCTURE_FIELDS = ("support", "resistance", "trend", "breakout", "breakdown", "retest", "compression", "expansion", "volume", "momentum", "vwap", "volatility")
TIMEFRAMES = ("15m", "30m", "45m", "1h", "2h", "4h", "5h", "1d", "3d", "1w", "1M")

def build_structure(timeframe, **values):
    if timeframe not in TIMEFRAMES:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    return {"timeframe": timeframe, **{k: values.get(k) for k in STRUCTURE_FIELDS}}


def build_multi_timeframe_structure(data=None):
    data = data or {}
    return {tf: build_structure(tf, **data.get(tf, {})) for tf in TIMEFRAMES}
