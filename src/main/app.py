import uvicorn

from framework.config import settings
from framework.logging import logger
from main.service import app

SERVER_RUNNING_BANNER = """
+----------------------------------------+
|             SERVER WORKS!              |
+----------------------------------------+

Visit {proto}{host}:{port}

..........................................
"""


def run() -> None:
    banner = SERVER_RUNNING_BANNER.format(
        host=settings.HOST,
        port=settings.PORT,
        proto=("http://" if "https" not in settings.HOST else "https://"),
    )
    logger.info(banner)

    try:
        uvicorn.run(
            app,
            host="0.0.0.0",  # noqa: B104,S104
            port=8000,
            reload=False,
        )
    except KeyboardInterrupt:
        logger.trace("stopping server")
    finally:
        logger.trace("server has been shut down")


if __name__ == "__main__":
    run()
