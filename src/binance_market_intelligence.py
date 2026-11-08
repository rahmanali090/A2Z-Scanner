from src.binance_data import (
    get_price,
    get_24h_ticker,
    get_open_interest,
    get_funding_rate,
    get_order_book,
    get_market_klines,
)

def get_market_intelligence(symbol):
    ticker = get_24h_ticker(symbol)
    order_book = get_order_book(symbol, limit=20)
    return {
        "symbol": symbol,
        "price": get_price(symbol),
        "ticker": ticker,
        "open_interest": get_open_interest(symbol),
        "funding_rate": get_funding_rate(symbol),
        "order_book": order_book,
        "market_klines": get_market_klines(symbol),
    }
