import os
import asyncio
import random
import re
import logging
from datetime import datetime

import requests
from groq import Groq

# ======================== НАСТРОЙКИ ========================
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SITE_URL = "https://avtomaster24bot-lab.github.io/avtomaster_24_BOT/"
BOT_LINK = "https://t.me/AvtoMaster_24_bot"          # прямая рабочая ссылка

if not BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL_ID")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ======================== ТЕХНИЧЕСКИЕ ТЕМЫ (для Groq) ========================
TECHNICAL_TOPICS = [
    "Mitsubishi L200: почему гниёт рама и антикоррозийная обработка своими руками",
    "Toyota Land Cruiser 200: как убрать люфт рулевой рейки без замены",
    "BMW X5 E70: замена свечей накала и диагностика Webasto",
    "Audi A6 C7: почему пропадает тяга на 1.8 TFSI (PCV, маслоотделитель)",
    "Зимний лайфхак: заводим дизель в -30 без вебасты",
    "Летний лайфхак: охлаждаем салон до +18 за 2 минуты",
    "Почему скрипит руль на Hyundai Solaris – смазка карданчика за 10 минут",
    "Geely Atlas: глючит мультимедиа – жёсткая перезагрузка кодом 2580",
    "Как проверить компрессию без компрессометра (по пульсации шланга)",
    "Как промыть систему охлаждения лимонной кислотой – пропорции и риски",
    "Как восстановить запотевшие фары пастой GOI",
    "Сброс ошибки Check Engine без сканера – 5 способов",
]

# ======================== ИНСТРУКЦИИ ПО ПОЛЬЗОВАНИЮ СЕРВИСОМ (редкие посты) ========================
HOWTO_POSTS = [
    """**Как вызвать эвакуатор ночью за 2 минуты и не переплатить**

Сломались на трассе? Не обзванивайте 10 диспетчерских, теряя час.

**Алгоритм от Автомастер24:**
1. Откройте бот Автомастер24: {bot_link}
2. Нажмите «Эвакуатор», укажите город, точку А, точку Б, тип авто.
3. Получите предложения от 3–5 перевозчиков с ценой и временем подачи в течение 5 минут.
4. Выберите подходящее – эвакуатор приедет.

💰 Все цены в тенге, без скрытых платежей. А если нужен и ремонт – сразу оформите заявку на СТО.""",

    """**Как заказать редкую запчасть через тендер и не переплатить**

Ищете деталь, которой нигде нет? Не обзванивайте десятки магазинов.

**Схема работы от Автомастер24:**
1. Создайте заявку в боте: {bot_link} → укажите марку, модель, артикул детали.
2. Система разошлёт запрос всем подключённым магазинам.
3. В течение 15 минут вы получите 3–5 предложений с ценами в тенге.
4. Выберите лучшее – магазин свяжется с вами.

Экономите часы поиска и находите лучшую цену.""",

    """**Как вызвать мобильного механика – пошаговая инструкция**

Не хотите ехать в сервис? Опишите поломку в боте Автомастер24:

1. Откройте бот: {bot_link}
2. Нажмите «Механик на выезд».
3. Опишите проблему, приложите фото (если нужно).
4. Через 5–10 минут получите предложения от свободных мастеров с ценой и временем приезда.
5. Выберите мастера – он приедет к вам.

Без посредников, честные цены в тенге, гарантия.""",
]

# ======================== ПОСТЫ, ГЕНЕРИРУЕМЫЕ GROQ ========================
SYSTEM_PROMPT = """Ты — ведущий эксперт автомобильного сервиса «Автомастер24» с 30-летним опытом. Твой стиль: живой, дерзкий, с долей юмора, но исключительно полезный. Давай конкретные советы с цифрами, артикулами и пошаговыми инструкциями.

**Структура поста:**
1. Заголовок.
2. Проблема (когда, на каком пробеге).
3. Диагностика без подъёмника (на слух, по запаху).
4. **Пошаговая инструкция от Автомастер24** с деталями:
   - Моменты затяжки (Н·м), зазоры (мм), артикулы.
   - Названия жидкостей, инструментов.
   - Типичные ошибки.
5. Лайфхак или скрытая особенность.
6. Что делать, если не получается.

Обязательно в конце добавь фразу: «👉 Перейти в бот: {bot_link}» и «👉 Подробнее на сайте: {site_url}». Цены только в тенге (₸). Не упоминай другие журналы – только Автомастер24.

Длина 400–700 слов. Тема поста: {topic}
"""

async def generate_technical_post(topic: str) -> str:
    if not groq_client:
        return None
    prompt = SYSTEM_PROMPT.format(bot_link=BOT_LINK, site_url=SITE_URL, topic=topic)
    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=1500
        )
        post = response.choices[0].message.content.strip()
        if post:
            # Удаляем чужие ссылки, добавляем наши, если нет
            post = re.sub(r'(https?://)?t\.me/\S+', '', post)
            if BOT_LINK not in post:
                post += f"\n\n👉 Перейти в бот: {BOT_LINK}"
            if SITE_URL not in post:
                post += f"\n\n👉 Подробнее на сайте: {SITE_URL}"
            return post
    except Exception as e:
        logger.warning(f"Groq ошибка: {e}")
    return None

def prepare_howto_post(raw_post: str) -> str:
    """Вставляет ссылку на бот в инструкцию."""
    raw_post = raw_post.format(bot_link=BOT_LINK)
    raw_post = re.sub(r'(https?://)?t\.me/\S+', '', raw_post)
    if BOT_LINK not in raw_post:
        raw_post += f"\n\n👉 Перейти в бот: {BOT_LINK}"
    if SITE_URL not in raw_post:
        raw_post += f"\n\n👉 Подробнее на сайте: {SITE_URL}"
    return raw_post

# ======================== ОТПРАВКА В TELEGRAM ========================
def send_to_telegram(text: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text.strip(),
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 200:
            logger.info("Пост успешно отправлен")
        else:
            logger.error(f"Ошибка {resp.status_code}: {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Исключение при отправке: {e}")
        return False

# ======================== ОСНОВНАЯ ЛОГИКА ========================
async def main():
    logger.info("=== АВТОМАСТЕР24 – ГЕНЕРАЦИЯ ПОСТА ===")

    # Редко (примерно 1 раз в 7-10 дней) публикуем инструкцию
    # 0.12 = 12% дней ≈ раз в 8 дней
    if random.random() < 0.12:
        logger.info("Сегодня пост-инструкция о сервисе")
        raw_post = random.choice(HOWTO_POSTS)
        post_text = prepare_howto_post(raw_post)
    else:
        topic = random.choice(TECHNICAL_TOPICS)
        logger.info(f"Техническая тема: {topic}")
        post_text = await generate_technical_post(topic)
        if not post_text:
            # Если Groq не ответил, берём запасную инструкцию (чтобы пост был)
            logger.warning("Groq не ответил, публикуем инструкцию как резерв")
            raw_post = random.choice(HOWTO_POSTS)
            post_text = prepare_howto_post(raw_post)

    # Финальная отправка
    if post_text and len(post_text) > 0:
        success = send_to_telegram(post_text)
        logger.info("✅ Пост опубликован" if success else "❌ Ошибка отправки")
    else:
        logger.error("Не удалось сформировать пост")

    logger.info("=== ГОТОВО ===")

if __name__ == "__main__":
    asyncio.run(main())
