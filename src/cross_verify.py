def compare_prices(binance_price, bybit_price, threshold=0.005):
    if binance_price is None or bybit_price is None:
        return "UNAVAILABLE"

    if binance_price <= 0 or bybit_price <= 0:
        return "NO"

    diff = abs(binance_price - bybit_price) / binance_price

    if diff <= threshold:
        return "YES"

    return "PARTIAL"
