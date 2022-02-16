import httpx
import pytest
from starlette import status

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.functional,
]

TCP_PORTS_RANGE = range(1000, 65535)


async def test_asgi_app(asgi_client: httpx.AsyncClient) -> None:
    resp: httpx.Response = await asgi_client.get("/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.text.startswith("<!DOCTYPE html>")


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
