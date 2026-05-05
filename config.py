import os

# Ссылка на бот (используется в постах и видео)
BOT_LINK = "@AvtoMaster_24_bot"

# --- Telegram ---
BOT_TOKEN = os.getenv("@AvtoMaster_24_bot")            # токен вашего бота
CHANNEL_ID = os.getenv("CHANNEL_ID")          # например, "@avtomaster_channel"

# --- Google Gemini API ---
GEMINI_API_KEY = os.getenv("AIzaSyDZUrxGKMfOJBe-SM7XvbLzh4yYpPK_xgA")  # ключ для генерации картинок
