import asyncio
import html
import logging
from typing import Iterable, List, Tuple

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, MessageEntity

logging.basicConfig(level=logging.INFO)


def utf16_offset_to_index(text: str, offset: int) -> int:
    if offset <= 0:
        return 0
    count = 0
    for i, ch in enumerate(text):
        count += 2 if ord(ch) > 0xFFFF else 1
        if count >= offset:
            return i + 1
    return len(text)


def entity_span(text: str, entity: MessageEntity) -> Tuple[int, int]:
    start = utf16_offset_to_index(text, entity.offset)
    end = utf16_offset_to_index(text, entity.offset + entity.length)
    return start, end


def build_tag(entity: MessageEntity, text: str, start: int, end: int) -> Tuple[str, str]:
    t = entity.type
    if t == "bold":
        return "<b>", "</b>"
    if t == "italic":
        return "<i>", "</i>"
    if t == "underline":
        return "<u>", "</u>"
    if t == "strikethrough":
        return "<s>", "</s>"
    if t == "spoiler":
        return "<tg-spoiler>", "</tg-spoiler>"
    if t == "code":
        return "<code>", "</code>"
    if t == "pre":
        if entity.language:
            lang = html.escape(entity.language, quote=True)
            return f"<pre><code class=\"language-{lang}\">", "</code></pre>"
        return "<pre>", "</pre>"
    if t == "text_link":
        url = html.escape(entity.url or "", quote=True)
        return f"<a href=\"{url}\">", "</a>"
    if t == "text_mention" and entity.user:
        return f"<a href=\"tg://user?id={entity.user.id}\">", "</a>"
    if t == "url":
        url = html.escape(text[start:end], quote=True)
        return f"<a href=\"{url}\">", "</a>"
    if t == "email":
        addr = html.escape(text[start:end], quote=True)
        return f"<a href=\"mailto:{addr}\">", "</a>"
    if t == "phone_number":
        phone = html.escape(text[start:end], quote=True)
        return f"<a href=\"tel:{phone}\">", "</a>"
    if t == "mention":
        username = text[start:end].lstrip("@")
        username = html.escape(username, quote=True)
        return f"<a href=\"https://t.me/{username}\">", "</a>"
    if t == "hashtag":
        tag = html.escape(text[start:end], quote=True)
        return f"<a href=\"tg://search?query={tag}\">", "</a>"
    if t == "cashtag":
        tag = html.escape(text[start:end], quote=True)
        return f"<a href=\"tg://search?query={tag}\">", "</a>"
    if t == "bot_command":
        return "<code>", "</code>"
    if t == "custom_emoji":
        return f"<tg-emoji emoji-id=\"{entity.custom_emoji_id}\">", "</tg-emoji>"
    if t == "blockquote":
        return "<blockquote>", "</blockquote>"
    return "", ""


def unparse_html(text: str, entities: Iterable[MessageEntity]) -> str:
    entity_spans: List[Tuple[MessageEntity, int, int]] = []
    for e in entities:
        start, end = entity_span(text, e)
        if start >= end:
            continue
        open_tag, close_tag = build_tag(e, text, start, end)
        if (open_tag, close_tag) == ("", ""):
            continue
        entity_spans.append((e, start, end))

    if not entity_spans:
        return text

    opens: List[List[Tuple[int, str, str]]] = [[] for _ in range(len(text) + 1)]
    closes: List[List[Tuple[int, str]]] = [[] for _ in range(len(text) + 1)]

    for e, start, end in entity_spans:
        open_tag, close_tag = build_tag(e, text, start, end)
        opens[start].append((end, open_tag, close_tag))
        closes[end].append((start, close_tag))

    out: List[str] = []
    for i in range(len(text) + 1):
        if i < len(closes):
            for start, close_tag in sorted(closes[i], key=lambda x: x[0], reverse=True):
                out.append(close_tag)
        if i < len(opens):
            for end, open_tag, _ in sorted(opens[i], key=lambda x: x[0], reverse=True):
                out.append(open_tag)
        if i < len(text):
            out.append(html.escape(text[i]))

    return "".join(out)


def get_text_and_entities(message: Message) -> Tuple[str, List[MessageEntity]]:
    if message.text:
        return message.text, list(message.entities or [])
    if message.caption:
        return message.caption, list(message.caption_entities or [])
    return "", []


def is_only_custom_emoji(text: str, entities: List[MessageEntity]) -> bool:
    if not text or not entities:
        return False
    if any(e.type != "custom_emoji" for e in entities):
        return False

    covered = [False] * len(text)
    for e in entities:
        start, end = entity_span(text, e)
        for i in range(start, min(end, len(text))):
            covered[i] = True

    for i, ch in enumerate(text):
        if not covered[i] and not ch.isspace():
            return False
    return True


async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет!\n"
        "Отправь текст с премиум-эмоджи или с форматированием, и я верну "
        "HTML-заготовку с <tg-emoji>.\n"
        "Если пришлёшь один стикер или только премиум-эмоджи — верну их id."
    )


async def handle_message(message: Message) -> None:
    if message.sticker:
        custom_id = message.sticker.custom_emoji_id
        if custom_id:
            await message.answer(custom_id)
        else:
            await message.answer("У этого стикера нет custom_emoji_id.")
        return

    text, entities = get_text_and_entities(message)
    if not text:
        await message.answer("Отправь текст или стикер с премиум-эмоджи.")
        return

    if is_only_custom_emoji(text, entities):
        ids = [e.custom_emoji_id for e in entities if e.custom_emoji_id]
        if ids:
            await message.answer("\n".join(ids))
        else:
            await message.answer("Custom emoji id не найден.")
        return

    html_text = unparse_html(text, entities)
    await message.answer(html_text)


BOT_TOKEN = "8785691457:AAFkdjQDe2mQHIlrjxNp7V-PYRYGLmIU6wY"


async def main() -> None:
    token = BOT_TOKEN

    bot = Bot(token=token)
    dp = Dispatcher()

    dp.message.register(cmd_start, F.text == "/start")
    dp.message.register(handle_message)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
