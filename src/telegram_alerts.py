from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import requests
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
    return r.ok

def send_inverted_hammer_alert(pattern, levels):
    if not pattern or not levels:
        return False
    candle_time = datetime.fromtimestamp(
        float(pattern["candle_close_time"]) / 1000,
        tz=ZoneInfo("Asia/Karachi")
    ).strftime("%I:%M:%S %p")
    def fmt(value):
        return f"{float(value):.8f}".rstrip("0").rstrip(".")
    message = (
        "INVERTED HAMMER ALERT\n"
        f"Coin: {pattern['symbol']}\n"
        f"Timeframe: {pattern.get('timeframes_text', pattern['timeframe'])}\n"
        f"Candle Time: {candle_time}\n"
        f"Entry: {fmt(levels['entry'])}\n"
        f"SL 🧨: {fmt(levels['stop_loss'])}\n"
f"TP1 {chr(0x1F3AF)}: {fmt(levels[chr(116)+chr(112)+chr(49)])}\n"
f"TP2 {chr(0x1F459)}: {fmt(levels[chr(116)+chr(112)+chr(50)])}\n"
f"TP3 {chr(0x1F680)}: {fmt(levels[chr(116)+chr(112)+chr(51)])}\n"
        "! Reason: Completed Inverted Hammer\n"
        "Manual verification required."
    )
    return send_alert(message)
