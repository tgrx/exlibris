import httpx
import pytest
from starlette import status

from framework.dirs import DIR_STATIC


@pytest.mark.functional
async def test_index(asgi_client: httpx.AsyncClient) -> None:
    resp: httpx.Response = await asgi_client.get("/")
    assert resp.status_code == status.HTTP_200_OK

    with (DIR_STATIC / "index.html").open("r") as index_html:
        html = index_html.read()
        assert resp.text == html


@pytest.mark.functional
async def test_sentry(asgi_client: httpx.AsyncClient) -> None:
    with pytest.raises(RuntimeError) as exc_info:
        await asgi_client.get("/e")
    assert str(exc_info.value) == "sentry test"
