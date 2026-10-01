MARKET_INTELLIGENCE_FIELDS = ("price", "change_24h", "volume_24h", "high_24h", "low_24h", "klines", "order_book", "open_interest", "funding_rate", "candle_stats", "candle_metrics", "data_timestamp", "exchange_info", "timeframe_stats", "timeframe_metrics", "market_status")

def build_market_intelligence(**data):
    return {field: data.get(field) for field in MARKET_INTELLIGENCE_FIELDS}

def collect_binance_intelligence(symbol):
    from src.binance_data import get_price, get_24h_ticker, get_klines, get_order_book, get_open_interest, get_funding_rate, candle_stats, candle_metrics, data_timestamp, get_exchange_info, parse_klines
    ticker = get_24h_ticker(symbol) or {}
    return build_market_intelligence(
        price=get_price(symbol),
        change_24h=ticker.get("priceChangePercent"),
        volume_24h=ticker.get("volume"),
        high_24h=ticker.get("highPrice"),
        low_24h=ticker.get("lowPrice"),
        klines={tf: get_klines(symbol, tf, 100) for tf in ("15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M")},
        order_book=get_order_book(symbol, 20),
        open_interest=get_open_interest(symbol),
        funding_rate=get_funding_rate(symbol),
candle_stats=candle_stats(parse_klines(get_klines(symbol, "1h", 100))),
candle_metrics=candle_metrics(parse_klines(get_klines(symbol, "1h", 100))),
data_timestamp=data_timestamp(),
exchange_info=get_exchange_info(),
    timeframe_stats={tf: candle_stats(parse_klines(get_klines(symbol, tf, 100))) for tf in ["15m","30m","1h","2h","4h","6h","1d"]},
    timeframe_metrics={tf: candle_metrics(parse_klines(get_klines(symbol, tf, 100))) for tf in ["15m","30m","1h","2h","4h","6h","1d"]},
        market_status="AVAILABLE",
    )
