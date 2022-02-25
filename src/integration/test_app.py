from typing import Optional
from typing import cast
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import httpx
import orjson
import pytest
from consigliere import telegram
from pytest_mock import MockerFixture
from starlette import status

from framework.config import settings
from framework.dirs import DIR_STATIC
from main import db
from main.service import WEBHOOK_URL

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.functional,
]

TCP_PORTS_RANGE = range(1000, 65535)


async def test_service_index(asgi_client: httpx.AsyncClient) -> None:
    resp: httpx.Response = await asgi_client.get("/")
    assert resp.status_code == status.HTTP_200_OK

    with (DIR_STATIC / "index.html").open("r") as index_html:
        html = index_html.read()
        assert resp.text == html


async def test_service_sentry_test(asgi_client: httpx.AsyncClient) -> None:
    with pytest.raises(RuntimeError) as exc_info:
        await asgi_client.get("/e")
    assert str(exc_info.value) == "sentry test"


async def test_service_api_get_webhook_info(
    asgi_client: httpx.AsyncClient,
    mocker: MockerFixture,
) -> None:
    bot = mocker.patch("main.service.bot", autospec=True)
    bot.getWebhookInfo.return_value = {"a": 1}

    resp: httpx.Response = await asgi_client.get("/api/v1/get_webhook_info")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == bot.getWebhookInfo.return_value


async def test_service_api_webhook_setup(
    asgi_client: httpx.AsyncClient,
    mocker: MockerFixture,
) -> None:
    bot = mocker.patch("main.service.bot", autospec=True)
    bot.setWebhook.return_value = True

    resp: httpx.Response = await asgi_client.put("/api/v1/setup_webhook")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == bot.setWebhook.return_value
    bot.setWebhook.assert_called_once_with(
        url=f"{settings.HOST}/{WEBHOOK_URL}",
    )


@pytest.mark.parametrize("action", [None, AsyncMock()])
async def test_service_webhook(
    asgi_client: httpx.AsyncClient,
    session2: db.Session,
    mocker: MockerFixture,
    action: Optional[AsyncMock],
) -> None:
    update = telegram.Update(
        update_id=1,
        message=telegram.Message(
            message_id=2,
            date="2000-01-01T00:00:00Z",
            chat=telegram.Chat(
                id=3,
            ),
            **{
                "from": telegram.User(
                    first_name="user",
                    id=4,
                    is_bot=True,
                )
            },
        ),
    )

    mock_bot = mocker.patch("main.service.bot", autospec=True)

    mock_db = mocker.patch("main.service.db", autospec=True)
    mock_session_ctx = MagicMock()
    mock_session_ctx.__aenter__.return_value = session2
    mock_db.Session.begin.return_value = mock_session_ctx
    dispatcher_dispatch = mocker.patch(
        "main.service.dispatcher.dispatch",
        autospec=True,
    )
    dispatcher_dispatch.return_value = action() if action else None

    resp: httpx.Response = await asgi_client.post(
        WEBHOOK_URL,
        data=cast(dict, orjson.dumps(update.dict(by_alias=True))),
    )

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() is None

    assert mock_db.Session.begin.call_count == 2

    ctx = dispatcher_dispatch.call_args.args[0]
    assert ctx.bot is mock_bot
    assert ctx.edited is False
    assert ctx.message == update.message
    assert ctx.session == session2
    assert ctx.user.tg_id == update.message.from_.id
    assert ctx.user.first_name == update.message.from_.first_name

    if action:
        action.assert_awaited_once()


@pytest.mark.webapp
async def test_web_app(web_client: httpx.AsyncClient) -> None:
    try:
        resp: httpx.Response = await web_client.get("/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.text.startswith("<!DOCTYPE html>")
    except (
        httpx.ConnectError,
        httpx.TimeoutException,
    ) as err:  # pragma: no cover
        raise AssertionError(
            f"unable to connect to server @ {web_client.base_url}"
        ) from err
