import requests
from .config import BINANCE_ALPHA_BASE_URL

def get_token_list():
    url = f"{BINANCE_ALPHA_BASE_URL}/bapi/defi/v1/public/wallet-direct/buw/wallet/cex/alpha/all/token/list"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def get_exchange_info():
    url = f"{BINANCE_ALPHA_BASE_URL}/bapi/defi/v1/public/alpha-trade/get-exchange-info"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def get_ticker(symbol):
    url = f"{BINANCE_ALPHA_BASE_URL}/bapi/defi/v1/public/alpha-trade/ticker"
    r = requests.get(url, params={"symbol": symbol}, timeout=10)
    r.raise_for_status()
    return r.json()

def get_klines(symbol, interval="4h", limit=100):
    url = f"{BINANCE_ALPHA_BASE_URL}/bapi/defi/v1/public/alpha-trade/klines"
    r = requests.get(
        url,
        params={"symbol": symbol, "interval": interval, "limit": limit},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()

def get_agg_trades(symbol, limit=100):
    url = f"{BINANCE_ALPHA_BASE_URL}/bapi/defi/v1/public/alpha-trade/agg-trades"
    r = requests.get(
        url,
        params={"symbol": symbol, "limit": limit},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()
