def evaluate_market_shock(change_percent, volume_ratio=1.0, shock_percent=5.0, volume_threshold=2.0):
    change = abs(float(change_percent or 0))
    volume_ratio = float(volume_ratio or 0)
    triggered = change >= shock_percent or volume_ratio >= volume_threshold
    return {
        "status": "ALERT" if triggered else "NORMAL",
        "price_shock": change >= shock_percent,
        "volume_shock": volume_ratio >= volume_threshold,
        "change_percent": change,
        "volume_ratio": volume_ratio,
    }
