from src.coin_analysis import analyze_coin
from src.cross_exchange import get_cross_exchange_context
from src.anti_chase import evaluate_anti_chase
from src.emergency_intelligence import evaluate_market_shock

def build_signal_context(symbol):
    coin = analyze_coin(symbol)
    change = coin.get("change_percent", 0)

    return {
        "symbol": symbol,
        "coin": coin,
        "cross_exchange": get_cross_exchange_context(symbol),
        "anti_chase": evaluate_anti_chase(change),
        "emergency": evaluate_market_shock(change),
    }

def enrich_signal(symbol, direction, change_percent):
    context = build_signal_context(symbol)
    context["signal"] = {
        "direction": direction,
        "change_percent": float(change_percent or 0),
    }
    return context

def process_signal(symbol, direction, change_percent, timeframe=None, candle=None, pattern_data=None):
    signal = enrich_signal(symbol, direction, change_percent)
    if timeframe is not None and candle is not None and pattern_data is not None:
        from src.database import save_inverted_hammer_candidate
        save_inverted_hammer_candidate(symbol, timeframe, candle, pattern_data)
    if timeframe is not None and candle is not None and pattern_data is not None:
        from src.telegram_alerts import send_alert
        from src.market_intelligence import collect_binance_intelligence
        signal["market_intelligence"] = collect_binance_intelligence(symbol)
        send_alert(str(signal))
    return signal
