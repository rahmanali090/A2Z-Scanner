import requests
from .config import BINANCE_BASE_URL

def get_price(symbol):
    r = requests.get(f"{BINANCE_BASE_URL}/fapi/v1/ticker/price", params={"symbol": symbol}, timeout=10)
    r.raise_for_status()
    return float(r.json()["price"])

def get_24h_ticker(symbol):
    r = requests.get(f"{BINANCE_BASE_URL}/fapi/v1/ticker/24hr", params={"symbol": symbol}, timeout=10)
    r.raise_for_status()
    return r.json()
