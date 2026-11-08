from src.binance_data import get_24h_ticker


def analyze_coin(symbol):
    try:
        ticker = get_24h_ticker(symbol) or {}
    except Exception:
        ticker = {}

    change = float(ticker.get("priceChangePercent", 0) or 0)

    if change > 0:
        direction = "BULLISH"
    elif change < 0:
        direction = "BEARISH"
    else:
        direction = "FLAT"

    return {
        "symbol": symbol,
        "price": ticker.get("lastPrice"),
        "direction": direction,
        "change_percent": change,
        "open_interest": None,
        "funding_rate": None,
        "order_book": None,
        "market_klines": None,
    }
