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
    "ADAUSDT",
    "ARBUSDT",
    "APTUSDT",
    "HYPEUSDT",
    "DOTUSDT",
 "ATOMUSDT",
 "APEUSDT",
 "IOTAUSDT",
 "RUNEUSDT",
 "SNXUSDT",
 "KAVAUSDT",
 "AVAXUSDT",
 "JUPUSDT",
 "SEIUSDT",
}


def run_once():
    init_db()
    symbols = [s for s in get_usdt_futures_symbols() if s in PRIORITY_SYMBOLS]
    alpha_tokens = get_token_list()
    hammer_alerts = run_inverted_hammer_alerts(get_usdt_futures_symbols())
    general_signals = []
    from src.coin_analysis import analyze_coin
    from src.signal_engine import process_signal
    for symbol in symbols:
        x = analyze_coin(symbol)
        if x["direction"] != "FLAT":
            general_signals.append(process_signal(symbol, x["direction"], x["change_percent"]))
    news_signal_candidates = []
    from src.binance_news import get_macro_news_signal_candidates
    for news_signal in get_macro_news_signal_candidates(20):
        news_signal_candidates.append(process_signal(news_signal["symbol"], news_signal["direction"], news_signal["change_percent"]))
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
                if process_inverted_hammer_alert(symbol, pattern):
                    alerts_sent += 1
    return alerts_sent
if __name__ == "__main__":
    main()
