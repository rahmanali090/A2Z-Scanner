import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "A2Z Scanner"
PAPER_MODE = os.getenv("PAPER_MODE", "false").lower() == "true"
BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://fapi.binance.com")
BYBIT_BASE_URL = os.getenv("BYBIT_BASE_URL", "https://api.bybit.com")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

BINANCE_ALPHA_BASE_URL = os.getenv("BINANCE_ALPHA_BASE_URL", "https://www.binance.com")
