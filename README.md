# ✨ Telegram Premium Emoji ID Bot (`tg-premium-emoji-bot`)

Telegram-бот для извлечения `custom_emoji_id` из премиум-эмодзи и автоматической конвертации форматированного текста в HTML-разметку `<tg-emoji emoji-id="...">` для использования в ботах (`aiogram` / `Bot API`).

---

## ✨ Возможности

- **Конвертация текста**: принимает сообщение с любым форматированием и кастомными эмодзи и возвращает готовый HTML-код с тегами `<tg-emoji emoji-id="...">`.
- **Извлечение ID**: при отправке стикера или набора премиум-эмодзи возвращает список их `custom_emoji_id`.

---

## 🚀 Быстрый старт

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN="123456:ABCDEF..."
python3 main.py
```
