import requests
from .config import BYBIT_BASE_URL

def get_price(symbol):
    r = requests.get(f"{BYBIT_BASE_URL}/v5/market/tickers", params={"category": "linear", "symbol": symbol}, timeout=10)
    r.raise_for_status()
    data = r.json()
    return float(data["result"]["list"][0]["lastPrice"])
