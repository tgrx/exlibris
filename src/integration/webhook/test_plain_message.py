from typing import cast
from unittest.mock import MagicMock

import httpx
import orjson
import pytest
from consigliere import telegram
from pytest_mock import MockerFixture
from starlette import status

from main import business
from main import db
from main.service import WEBHOOK_URL

USER = telegram.User(
    first_name="user",
    id=4,
    is_bot=True,
)

CHAT = telegram.Chat(id=3)

MESSAGE = telegram.Message(
    chat=CHAT,
    date="2000-01-01T00:00:00Z",
    message_id=2,
    text="test text",
    **{"from": USER},
)

UPDATE = telegram.Update(
    message=MESSAGE,
    update_id=1,
)


@pytest.mark.functional
async def test(
    asgi_client: httpx.AsyncClient,
    test_session: db.Session,
    mocker: MockerFixture,
) -> None:
    mock_bot = mocker.patch("main.service.bot", autospec=True)

    session = cast(db.Session, test_session)
    mock_session = build_mock_session(
        mocker, session, "main.service.db.Session"
    )

    users = await business.get_users(session)
    assert not users

    resp: httpx.Response = await asgi_client.post(
        WEBHOOK_URL,
        data=cast(dict, orjson.dumps(UPDATE.dict(by_alias=True))),
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() is None

    mock_session.begin.assert_called()

    users = await business.get_users(session)
    assert len(users) == 1
    user = users[0]

    raws = await business.get_unbound_raws(test_session, user=user)
    assert len(raws) == 1
    raw = raws[0]

    mock_bot.sendMessage.assert_called_once_with(
        chat_id=CHAT.id,
        text=(
            f"получил текст: {MESSAGE.text},"
            f" сохранил как raw text {raw.id}"
        ),
    )


def build_mock_session(
    mocker: MockerFixture, session: db.Session, where: str
) -> db.Session:
    mock_session_ctx = MagicMock()
    mock_session_ctx.__aenter__.return_value = session
    mock_session = mocker.patch(where, autospec=True)
    mock_session.begin.return_value = mock_session_ctx
    return mock_session
