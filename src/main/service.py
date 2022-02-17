from consigliere import telegram
from consigliere.bot import Bot
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.middleware import Middleware
from starlette.responses import HTMLResponse

from framework.config import settings
from framework.dirs import DIR_STATIC
from framework.logging import logger
from main import business
from main import db
from main import dispatcher
from main.util import safe

app = FastAPI(
    middleware=[
        Middleware(SentryAsgiMiddleware),
    ],
)
app.mount("/static", StaticFiles(directory=DIR_STATIC), name="static")

bot = Bot(settings.TELEGRAM_BOT_TOKEN)

API_V1 = "/api/v1"
WEBHOOK_URL = f"wh{settings.WEBHOOK_SECRET}"


@app.get("/", response_class=HTMLResponse)
async def handle_index() -> str:
    logger.trace("handling /")

    index = DIR_STATIC / "index.html"
    logger.trace("index.html to read: {}", index.as_posix())

    assert index.is_file(), f"{index.as_posix()} is not a file"
    logger.trace("index.html is ok")

    with index.open("r") as src:
        data = src.read()
        logger.trace("index.html is {} bytes", len(data))
        return data


@app.get("/e")
async def handle_sentry_test() -> None:
    logger.trace("sentry test, will raise an exception")
    raise RuntimeError("sentry test")


@app.get(f"{API_V1}/get_webhook_info")
async def handle_webhook_info() -> telegram.WebhookInfo:
    info = await bot.getWebhookInfo()
    return info


@app.put(f"{API_V1}/setup_webhook")
async def handle_webhook_setup() -> bool:
    url = f"{settings.HOST}/{WEBHOOK_URL}"
    ok: bool = await bot.setWebhook(url=url)
    return ok


@app.post(f"/{WEBHOOK_URL}")
@safe
async def handle_webhook_update(
    update: telegram.Update,
    session: db.Session = db.SessionDependency,
) -> None:
    message, edited = (
        (update.message, False)
        if update.message
        else (update.edited_message, True)
    )

    user = await business.install_user(session, user=message.from_)

    ctx = dispatcher.Context(
        bot=bot,
        edited=edited,
        message=message,
        session=session,
        user=user,
    )

    action = await dispatcher.dispatch(ctx)
    if action:
        await action
