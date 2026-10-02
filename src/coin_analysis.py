from src.binance_market_intelligence import get_market_intelligence

def analyze_coin(symbol):
    market = get_market_intelligence(symbol)
    ticker = market.get("ticker") or {}
    change = float(ticker.get("priceChangePercent", 0) or 0)
    if change > 0:
        direction = "BULLISH"
    elif change < 0:
        direction = "BEARISH"
    else:
        direction = "FLAT"
    return {
        "symbol": symbol,
        "price": market.get("price"),
        "direction": direction,
        "change_percent": change,
        "open_interest": market.get("open_interest"),
        "funding_rate": market.get("funding_rate"),
        "order_book": market.get("order_book"),
        "market_klines": market.get("market_klines"),
    }
