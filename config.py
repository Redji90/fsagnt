"""Конфигурация приложения"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в .env файле")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не установлен в .env файле")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# PDF Settings
MAX_PDF_SIZE_MB = int(os.getenv("MAX_PDF_SIZE_MB", "10"))
MAX_PDF_SIZE_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024

# Пути
UPLOAD_DIR = "uploads"
ANALYSIS_DIR = "analysis"

# Создаем директории если их нет
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)




