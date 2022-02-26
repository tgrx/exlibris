import asyncio
from contextlib import closing
from typing import Any
from typing import AsyncGenerator
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from framework.config import settings
from main import db
from main.db import Model
from main.db import get_db_url


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    with closing(asyncio.new_event_loop()) as loop:
        yield loop


@pytest.fixture(scope="session")
def test_database_url() -> Generator[str, None, None]:
    db_settings = settings.db_components_from_database_url()
    db_settings.DB_NAME = f"{db_settings.DB_NAME}_test"
    database_url = db_settings.database_url_from_db_components()
    yield get_db_url(database_url)


@pytest.fixture(scope="session")
def test_database_engine(
    test_database_url: str,
) -> Generator[AsyncEngine, None, None]:
    engine = create_async_engine(
        test_database_url.replace("://", "+asyncpg://"),
        echo=settings.MODE_DEBUG_SQL,
    )
    yield engine


@pytest.fixture(scope="session")
def test_database_session_cls(
    test_database_engine: AsyncEngine,
) -> Generator[AsyncSession, None, None]:
    session_cls = sessionmaker(
        test_database_engine,
        autocommit=False,
        class_=AsyncSession,
        expire_on_commit=False,
        future=True,
    )
    yield session_cls


@pytest.fixture(scope="session", autouse=True)
def reset_db(test_database_url: str) -> Any:
    engine = create_engine(
        test_database_url,
        echo=settings.MODE_DEBUG_SQL,
    )

    Model.metadata.create_all(engine)

    yield

    Model.metadata.drop_all(engine)


@pytest.fixture(scope="function")
async def test_session(
    test_database_session_cls: AsyncSession,
) -> AsyncGenerator[db.Session, None]:
    async with test_database_session_cls.begin() as session:
        try:
            yield session
        finally:
            await session.rollback()
