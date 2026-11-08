import os
import requests
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_alert(message, parse_mode=None):
    token = os.getenv("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
    chat_id = os.getenv("TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID)
    if not token or not chat_id:
        print("Telegram Error: BOT_TOKEN or CHAT_ID is missing!", flush=True)
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            if parse_mode:
                payload.pop("parse_mode", None)
                response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                print(f"Telegram API Error {response.status_code}: {response.text}", flush=True)
                return False
        return True
    except Exception as e:
        print(f"Telegram connection exception: {e}", flush=True)
        return False

def send_inverted_hammer_alert(pattern, levels):
    msg = (
        "INVERTED HAMMER ALERT\n"
        f"Symbol: {pattern.get('symbol')}\n"
        f"Timeframe: {pattern.get('timeframe')}\n"
        f"Entry: {levels.get('entry')}\n"
        f"Stop Loss: {levels.get('stop_loss')}\n"
        f"TP1: {levels.get('tp1')} | TP2: {levels.get('tp2')} | TP3: {levels.get('tp3')}"
    )
    return send_alert(msg, parse_mode=None)
