import httpx
import pytest
from pytest_mock import MockerFixture
from starlette import status

from framework.config import settings
from main.service import WEBHOOK_URL


@pytest.mark.functional
async def test_get_webhook_info(
    asgi_client: httpx.AsyncClient,
    mocker: MockerFixture,
) -> None:
    bot = mocker.patch("main.service.bot", autospec=True)
    bot.getWebhookInfo.return_value = {"a": 1}

    resp: httpx.Response = await asgi_client.get("/api/v1/get_webhook_info")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == bot.getWebhookInfo.return_value


@pytest.mark.functional
async def test_webhook_setup(
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
