import httpx
import pytest
from pytest_mock import MockerFixture
from starlette import status

from framework.config import settings
from framework.dirs import DIR_STATIC
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
