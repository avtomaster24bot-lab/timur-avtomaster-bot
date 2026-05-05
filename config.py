import os

# Ссылка на бот (используется в постах и видео)
BOT_LINK = "@AvtoMaster_24_bot"

# --- Telegram ---
BOT_TOKEN = os.getenv("BOT_TOKEN")            # токен вашего бота
CHANNEL_ID = os.getenv("CHANNEL_ID")          # например, "@avtomaster_channel"

# --- Google Gemini API ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # ключ для генерации картинок
