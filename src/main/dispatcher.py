from typing import Any
from typing import Callable
from typing import Coroutine
from typing import NamedTuple

from consigliere import telegram
from consigliere.bot import Bot

from main import business
from main import db
from main.consts import BOT_COMMANDS
from main.util import select_max_size_photo


class Context(NamedTuple):
    bot: Bot
    edited: bool
    message: telegram.Message
    session: db.Session
    user: db.User


ActionT = Coroutine[Any, Any, Any]


async def dispatch(context: Context) -> ActionT:
    handler: Callable = handle_default

    if context.edited:
        handler = handle_edited_message
    elif context.message.text:
        if context.message.text == "/add":
            handler = handle_add
        elif context.message.text == "/clear":
            handler = handle_clear
        elif context.message.text == "/find":  # todo: startswith
            handler = handle_find
    elif context.message.photo:
        handler = handle_photo

    action: Coroutine = await handler(context)

    return action


async def handle_edited_message(context: Context) -> ActionT:
    _err = f"unexpected original message {context.message}"
    assert context.edited, _err

    if context.message.text in BOT_COMMANDS:
        text = "никаких обновлений: команды не обновляются"

    else:
        photo = select_max_size_photo(context.message.photo)

        raws = await business.install_raw(
            context.session,
            description=context.message.text or context.message.caption,
            message_id=context.message.message_id,
            photo_file_id=photo.file_id or None,
            user=context.user,
        )

        if raws:
            text = f"обновленная инфа: {raws}"
        else:
            text = "никаких обновлений: всё уже сохранено"

    action: ActionT = context.bot.sendMessage(
        chat_id=context.message.chat.id,
        text=text,
    )

    return action


async def handle_add(context: Context) -> Coroutine:
    _err = f"unexpected text in message {context.message}"
    assert context.message.text == "/add", _err
    _err = f"unexpected photo in message {context.message}"
    assert not context.message.photo, _err

    raws = await business.get_unbound_raws(context.session, user=context.user)
    if raws:
        book = await business.create_book(context.session, user=context.user)
        text = f"создал книгу {book.id} из {raws}"
    else:
        text = "так а не из чего создавать"

    action: ActionT = context.bot.sendMessage(
        chat_id=context.message.chat.id,
        text=text,
    )

    return action


async def handle_clear(context: Context) -> Coroutine:
    _err = f"unexpected text in message {context.message}"
    assert context.message.text == "/clear", _err
    _err = f"unexpected photo in message {context.message}"
    assert not context.message.photo

    raws_nr = await business.remove_unbound_raws(
        context.session,
        user=context.user,
    )
    if raws_nr:
        text = f"все {raws_nr!r} raw-ки очищены"
    else:
        text = "все и так хорошо, нечего очищать"

    action: ActionT = context.bot.sendMessage(
        chat_id=context.message.chat.id,
        text=text,
    )

    return action


async def handle_find(context: Context) -> Coroutine:
    _err = f"no text in message {context.message}"
    assert context.message.text, _err
    _err = f"invalid command text in message {context.message}"
    assert context.message.text.startswith("/find"), _err
    _err = f"unexpected photo in message {context.message}"
    assert not context.message.photo, _err

    text = (
        f"поиск завершён: ты искал {context.message.text!r},"
        f" а мы нашли ХУЙ ТЕБЕ )))0"
    )

    action: ActionT = context.bot.sendMessage(
        chat_id=context.message.chat.id,
        text=text,
    )

    return action


async def handle_default(context: Context) -> Coroutine:
    _err = f"no text in message {context.message}"
    assert context.message.text, _err

    _err = f"unexpected photo in message {context.message}"
    assert not context.message.photo, _err

    raw_text = await business.install_raw(
        context.session,
        description=context.message.text,
        message_id=context.message.message_id,
        user=context.user,
    )

    text = (
        f"получил текст: {context.message.text},"
        f" сохранил как raw text {raw_text.id}"
    )

    action: ActionT = context.bot.sendMessage(
        chat_id=context.message.chat.id,
        text=text,
    )

    return action


async def handle_photo(context: Context) -> ActionT:
    _err = f"no photo in message {context.message}"
    assert context.message.photo, _err

    photo = select_max_size_photo(context.message.photo)

    raw_photo = await business.install_raw(
        context.session,
        description=context.message.caption,
        message_id=context.message.message_id,
        photo_file_id=photo.file_id,
        user=context.user,
    )

    text = (
        f"получил фотку {context.message.caption!r}\n\n"
        f"{photo.json()}\n\n"
        f"сохранил как raw photo {raw_photo.id}"
    )

    action: ActionT = context.bot.sendMessage(
        chat_id=context.message.chat.id,
        text=text,
    )

    return action


async def _make_default_action(*_args: Any, **_kwargs: Any) -> None:
    pass
