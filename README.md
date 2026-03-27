# Create-text

Бот-конвертер для премиум-эмоджи Telegram.

## Запуск

1. Установи зависимости:

```bash
pip install -r requirements.txt
```

2. Укажи токен бота:

```bash
export BOT_TOKEN="123456:ABCDEF..."
```

3. Запусти:

```bash
python main.py
```

## Что делает бот

- Принимает сообщения с форматированием и custom emoji.
- Отдаёт HTML-заготовку с `<tg-emoji emoji-id="...">`.
- Если отправить стикер (custom emoji sticker) или только премиум-эмоджи — вернёт их `id`.
