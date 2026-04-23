import os
import asyncio
import random
import re
import logging
from datetime import datetime
from pathlib import Path

import requests
from groq import Groq

# ======================== НАСТРОЙКИ ========================
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SITE_URL = "https://avtomaster24bot-lab.github.io/avtomaster_24_BOT/"

if not BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL_ID")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ======================== БАЗА ТЕМ (можно расширять) ========================
TOPICS = [
    "Mitsubishi L200: почему гниёт рама и антикоррозийная обработка своими руками",
    "Toyota Land Cruiser 200: как убрать люфт рулевой рейки без замены",
    "BMW X5 E70: замена свечей накала и диагностика Webasto",
    "Audi A6 C7: почему пропадает тяга на 1.8 TFSI (PCV, маслоотделитель)",
    "Как быстро и дёшево найти эвакуатор ночью – не обзванивая 10 номеров",
    "Как заказать редкую запчасть через тендер в Автомастер24 и сэкономить часы",
    "Зимний лайфхак: заводим дизель в -30 без вебасты",
    "Летний лайфхак: охлаждаем салон до +18 за 2 минуты",
    "Почему скрипит руль на Hyundai Solaris – смазка карданчика за 10 минут",
    "Geely Atlas: глючит мультимедиа – жёсткая перезагрузка кодом 2580",
    "Как проверить компрессию без компрессометра (по пульсации шланга)",
    "Как промыть систему охлаждения лимонной кислотой – пропорции и риски",
    "Как восстановить запотевшие фары пастой GOI",
    "Сброс ошибки Check Engine без сканера – 5 способов",
]

# ======================== РЕЗЕРВНЫЕ ПОСТЫ (все с «от Автомастер24» и без чужих брендов) ========================
FALLBACK_POSTS_DETAILED = [
    """**Mitsubishi L200: антикоррозийная обработка рамы**

Рама L200 начинает ржаветь уже на 3-й год. Замена рамы стоит от 800 000 ₸, но можно замедлить процесс за 15 000 ₸ и выходные.

**Пошаговая инструкция от Автомастер24:**
1. Мойка Karcher (особенно полости). Сушка 2 дня в тёплом гараже.
2. Преобразователь ржавчины «Цинкарь» – кистью, через 4 часа смыть. Повторить 2 раза.
3. Защита внутренних полостей: пневмопушка с гибким шлангом, состав «Dinitrol ML» (3–4 л). Вводить в технологические отверстия лонжеронов и поперечин.
4. Наружная обработка: битумная мастика «Антикор +» (2 слоя). Особо тщательно – арки и места крепления бака.

**Важно:** через 2 года проверять сварные швы.

❓ **Не хотите возиться сами?**  
Отправьте заявку в боте Автомастер24: укажите авто, год, желаемый состав. Через 10 минут получите 3–5 предложений от проверенных СТО с ценами в тенге. Никаких звонков — всё в чате.

👉 [ Отправить заявку на антикор ]({site_url})""",

    """**Toyota Land Cruiser 200: убираем люфт рулевой рейки за 20 минут**

На пробеге 100 000+ км появляется стук и люфт. Замена рейки – от 600 000 ₸, но есть регулировка за 0 ₸.

**Пошаговая инструкция от Автомастер24:**
1. Поддомкратить перед, снять защиту картера.
2. На рейке слева найти регулировочный болт с контргайкой (24 мм).
3. Ослабить контргайку, вкрутить шестигранник на 5 до лёгкого касания.
4. Открутить на 30° (перетяжка = закусывание рейки).
5. Затянуть контргайку моментом 35 Н·м.
6. Покачать колесо – люфт должен уйти. Если остался – нужен ремкомплект втулок (Gates 3490).

**Где взять втулки и не переплатить?**  
Создайте заявку в Автомастер24: укажите авто, запчасть. Магазины сами пришлют цены в тенге, а сервисы – стоимость установки.

👉 [ Сравнить цены на запчасть ]({site_url})""",

    """**BMW X5 E70: не греет Webasto зимой – чиним свечу накала**

Автономка не запускается в мороз? Чаще всего виновата свеча накала (от 15 000 ₸).

**Пошаговая инструкция от Автомастер24:**
1. Снимите защиту картера, найдите свечу на Webasto.
2. Отсоедините разъём, прозвоните мультиметром (сопротивление 0.5–2 Ом). Обрыв = замена.
3. Для демонтажа нужна головка на 12 и проникающая смазка.
4. Если свеча жива – возможно, забита камера сгорания. Снимите, прочистите ёршиком.

**Нет времени или инструмента?**  
Вызовите мобильного механика через Автомастер24. Опишите проблему, пришлите фото. Специалисты предложат цену и время выезда.

👉 [ Вызвать механика ]({site_url})""",

    """**Как вызвать эвакуатор ночью за 2 минуты и не переплатить**

Сломались на трассе? Не обзванивайте 10 диспетчерских, теряя час.

**Алгоритм от Автомастер24:**
1. Откройте бот Автомастер24.
2. Нажмите «Эвакуатор», укажите город, точку А, точку Б, тип авто.
3. Получите предложения от 3–5 перевозчиков с ценой и временем подачи в течение 5 минут.
4. Выберите подходящее – эвакуатор приедет.

💰 Все цены в тенге, без скрытых платежей. А если нужен и ремонт – сразу оформите заявку на СТО.

👉 [ Отправить заявку на эвакуатор ]({site_url})"""
]

def get_fallback_post() -> str:
    template = random.choice(FALLBACK_POSTS_DETAILED)
    return template.format(site_url=SITE_URL)

# ======================== ПРОМПТ ДЛЯ GROQ (ТОЛЬКО АВТОМАСТЕР24, ДЕТАЛЬНО) ========================
SYSTEM_PROMPT = """Ты — ведущий эксперт автомобильного сервиса «Автомастер24» с 30-летним опытом. Твой стиль: живой, дерзкий, с долей юмора, но исключительно полезный. Ты даёшь конкретные, проверенные советы с цифрами, артикулами и пошаговыми инструкциями. Пиши от первого лица, как механик-практик.

**Структура каждого поста:**
1. Заголовок, интригующий и с практической ценностью.
2. Проблема: что, когда, на каком пробеге случается.
3. Диагностика (как понять без подъёмника, на слух, по запаху).
4. **Пошаговая инструкция от Автомастер24** (обязательно выдели этот заголовок) с деталями:
   - Моменты затяжки (Н·м), зазоры (мм), давления (атм), артикулы деталей.
   - Названия фирменных жидкостей, смазок, инструментов.
   - Типичные ошибки и как их избежать.
5. Скрытый лайфхак или особенность.
6. Что делать, если своими силами не получилось – даёшь ссылку на сервис.

**Обязательная воронка в конце или внутри:**
- Подчеркни, что в боте Автомастер24 можно отправить заявку (эвакуатор, запчасть, ремонт) и получить предложения от нескольких проверенных исполнителей с ценами в тенге.
- Пример: «Ищете деталь? Не обзванивайте полгорода. Укажите в боте марку авто и артикул – магазины сами пришлют цены. Экономия времени – часы».
- Все цены – только в тенге (₸) или без цифр.

**Фото (опционально):** Если нужно, добавь строку `[PHOTO_REQUIRED: краткое описание кадра]`.

Никаких упоминаний других журналов, изданий или шоу. Только «Автомастер24». Длина: 400–700 слов. Разбивай на абзацы, используй эмодзи маркеры. Формат – обычный текст (можно **жирный** для заголовков).

Учти текущую дату: {current_date}.

Пример завершения:
«…Если после регулировки люфт остался – нужен ремкомплект втулок. Не бегайте по магазинам. Отправьте заявку в Автомастер24: какой авто, нужная деталь. Через 15 минут вам придёт 3–5 цен от разных поставщиков в тенге. 👉 {site_url}»
"""

# ======================== ФУНКЦИЯ ГЕНЕРАЦИИ ЧЕРЕЗ GROQ ========================
async def generate_post_groq(topic: str) -> str:
    if not groq_client:
        return None
    current_date = datetime.now().strftime("%d.%m.%Y")
    user_prompt = f"Тема поста: {topic}. Напиши максимально полезный, детальный пост от лица автомеханика Автомастер24. Обязательно включи пошаговую инструкцию от Автомастер24 и в конце призыв отправить заявку через бот."
    try:
        for attempt in range(2):
            try:
                response = groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT.replace("{current_date}", current_date)},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.85,
                    max_tokens=1500
                )
                post = response.choices[0].message.content.strip()
                if post:
                    if SITE_URL not in post:
                        post += f"\n\n👉 Отправить заявку и сравнить цены: {SITE_URL}"
                    return post
            except Exception as e:
                logger.warning(f"Groq попытка {attempt+1} не удалась: {e}")
                await asyncio.sleep(3)
        return None
    except Exception as e:
        logger.error(f"Groq ошибка: {e}")
        return None

# ======================== РАБОТА С ФОТО ========================
PHOTO_DIR = Path("images")

def get_photo_for_post(post_text: str):
    match = re.search(r'\[PHOTO_REQUIRED:\s*(.*?)\]', post_text)
    if not match:
        return None, post_text
    keywords = match.group(1).lower()
    clean_text = re.sub(r'\[PHOTO_REQUIRED:.*?\]', '', post_text, flags=re.DOTALL)
    if PHOTO_DIR.exists():
        for img in PHOTO_DIR.iterdir():
            if img.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp'):
                if keywords in img.stem.lower():
                    return str(img), clean_text
    default_img = PHOTO_DIR / "no_image.jpg"
    if default_img.exists():
        return str(default_img), clean_text + "\n\n(Фото временно отсутствует)"
    return None, clean_text

def send_photo_to_telegram(photo_path: str, caption: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        with open(photo_path, 'rb') as f:
            files = {'photo': f}
            data = {'chat_id': CHANNEL_ID, 'caption': caption, 'parse_mode': 'HTML'}
            resp = requests.post(url, files=files, data=data, timeout=30)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка отправки фото: {e}")
        return False

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
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка отправки текста: {e}")
        return False

# ======================== ОСНОВНАЯ ФУНКЦИЯ ========================
async def main():
    logger.info("=== АВТОМАСТЕР24 – ГЕНЕРАЦИЯ ЭКСПЕРТНОГО ПОСТА ===")
    topic = random.choice(TOPICS)
    logger.info(f"Тема: {topic}")

    post_text = None
    for attempt in range(3):
        post_text = await generate_post_groq(topic)
        if post_text:
            break
        await asyncio.sleep(5)

    if not post_text:
        logger.warning("Groq недоступен, берём резервный пост")
        post_text = get_fallback_post()
    else:
        post_text = re.sub(r'(https?://)?t\.me/\S+', '', post_text)
        if SITE_URL not in post_text:
            post_text += f"\n\n👉 Отправить заявку и сравнить цены: {SITE_URL}"

    photo_path, clean_post = get_photo_for_post(post_text)
    if photo_path:
        ok = send_photo_to_telegram(photo_path, clean_post)
        if not ok:
            send_to_telegram(clean_post)
        else:
            logger.info("✅ Пост с фото опубликован")
    else:
        ok = send_to_telegram(clean_post)
        logger.info("✅ Пост без фото опубликован" if ok else "❌ Ошибка отправки")

    logger.info("=== ГОТОВО ===")

if __name__ == "__main__":
    asyncio.run(main())
