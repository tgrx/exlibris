import asyncio
from contextlib import closing
from typing import AsyncGenerator
from typing import Generator

import pytest

from main import db


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    with closing(asyncio.new_event_loop()) as loop:
        yield loop


@pytest.fixture(scope="function")
async def session2() -> AsyncGenerator[db.Session, None]:
    async with db.Session() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.rollback()
