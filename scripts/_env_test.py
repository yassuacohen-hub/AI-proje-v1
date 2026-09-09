import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

token = os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

print(f"Token found: {bool(token)}")
print(f"Token value: {token[:15]}..." if token else "Token: None")
print(f"Chat ID found: {bool(chat_id)}")
print(f"Chat ID: {chat_id}")