import httpx
import pytest
from starlette import status


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
