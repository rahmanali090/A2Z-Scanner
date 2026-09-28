def spread_pct(bid, ask):
    if bid is None or ask is None or bid <= 0:
        return None
    return ((ask - bid) / bid) * 100

def liquidity_status(bid, ask, max_spread_pct=0.5):
    spread = spread_pct(bid, ask)
    if spread is None:
        return "UNAVAILABLE"
    return "SAFE" if spread <= max_spread_pct else "RISK"
