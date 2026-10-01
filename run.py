from src.database import init_db
from src.binance_data import get_usdt_futures_symbols, scan_rapid_price_moves
from src.binance_alpha import get_token_list
from src.binance_news import refresh_alpha_catalysts
from src.btc_context import build_btc_context as get_btc_context

PRIORITY_SYMBOLS = {
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "XMRUSDT",
    "KSMUSDT",
    "ETCUSDT",
    "LINKUSDT",
    "ENAUSDT",
    "SUIUSDT",
    "NEARUSDT",
    "BANKUSDT",
    "UNIUSDT",
    "ICPUSDT",
    "INJUSDT",
    "DORUSDT",
    "ADAUSDT",
    "ARBUSDT",
    "APTUSDT",
    "HYPEUSDT",
    "DOTUSDT",
}


def run_once():
    init_db()
    symbols = [s for s in get_usdt_futures_symbols() if s in PRIORITY_SYMBOLS]
    alpha_tokens = get_token_list()
    hammer_alerts = run_inverted_hammer_alerts(symbols)
    rapid_result = scan_rapid_price_moves()
    news_result = refresh_alpha_catalysts()
    btc_context = get_btc_context()
    return {
        "symbol_count": len(symbols),
        "alpha_token_count": len(alpha_tokens),
        "hammer_alerts": hammer_alerts,
        "rapid_result": rapid_result,
        "news_result": news_result,
        "btc_context": btc_context,
        "status": "READY",
        "mode": "SIGNAL/ALERT",
    }



def main():
    result = run_once()
    print(f"A2Z Scanner: {result['mode']} | Status: {result['status']} | Signals sent: {result['hammer_alerts']} | Symbols: {result['symbol_count']} | Alpha: {result['alpha_token_count']} | News: {result['news_result']}")




def run_inverted_hammer_alerts(symbols):
    from src.binance_data import scan_inverted_hammer, process_inverted_hammer_alert
    alerts_sent = 0
    for symbol in symbols:
        results = scan_inverted_hammer(symbol)
        for pattern in results.values():
            if pattern:
                from src.signal_engine import process_signal
                process_signal(symbol, "BULLISH", pattern.get("change_percent", 0), pattern.get("timeframe"), pattern.get("candle"), pattern)
                if process_inverted_hammer_alert(symbol, pattern):
                    alerts_sent += 1
    return alerts_sent
if __name__ == "__main__":
    main()
