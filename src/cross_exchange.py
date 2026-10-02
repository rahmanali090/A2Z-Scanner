import requests
from src.binance_data import get_price

def get_bybit_ticker(symbol):
    response = requests.get(
        "https://api.bybit.com/v5/market/tickers",
        params={"category": "linear", "symbol": symbol},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    items = data.get("result", {}).get("list", [])
    return items[0] if items else None

def get_cross_exchange_context(symbol):
    bybit = get_bybit_ticker(symbol)
    binance_price = get_price(symbol)
    bybit_price = float(bybit.get("lastPrice")) if bybit and bybit.get("lastPrice") else None
    price_diff = (bybit_price - binance_price) if bybit_price is not None and binance_price is not None else None
    price_diff_percent = (price_diff / binance_price * 100) if price_diff is not None and binance_price else None
    return {
        "symbol": symbol,
        "bybit": bybit,
        "binance_price": binance_price,
        "bybit_price": bybit_price,
        "price_diff": price_diff,
        "price_diff_percent": price_diff_percent,
    }
