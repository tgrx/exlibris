from functools import cache
from typing import Optional
from uuid import uuid4

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from framework.config import settings


@cache
def get_db_url(db_url: Optional[str] = settings.DATABASE_URL) -> str:
    assert db_url
    if "postgresql" not in db_url:
        db_url = db_url.replace("postgres", "postgresql")
    if "?" in db_url:
        query = db_url.index("?")
        db_url = db_url[:query]
    return db_url


engine = create_async_engine(
    get_db_url().replace("://", "+asyncpg://"),
    echo=settings.MODE_DEBUG_SQL,
)

engine_sync = create_engine(
    get_db_url(),
    echo=settings.MODE_DEBUG_SQL,
)

Session = sessionmaker(
    engine,
    autocommit=False,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True,
)

Base = declarative_base()  # todo: create a decorated class, for typing


class Model(Base):  # type: ignore
    __abstract__ = True
    __mapper_args__ = {
        "eager_defaults": True,
    }

    id = Column(  # noqa: A003,VNE003
        UUID(as_uuid=True),
        default=uuid4,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )


class User(Model):
    __tablename__ = "users"

    tg_id = Column(
        BigInteger,
        nullable=False,
        # unique! see constraints
    )

    first_name = Column(
        Text,
        nullable=False,
    )

    last_name = Column(
        Text,
        nullable=True,
    )

    username = Column(
        Text,
        nullable=True,
    )

    is_bot = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    __table_args__ = (
        # order matters here!
        UniqueConstraint(
            tg_id,
            name="xxx_user_unique_tg_id",
        ),
    )


class Book(Model):
    __tablename__ = "books"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            User.id,
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        index=True,
        nullable=False,
    )


class Raw(Model):
    __tablename__ = "raw"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            User.id,
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        index=True,
        nullable=False,
    )

    book_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            Book.id,
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        index=True,
        nullable=True,
    )

    message_id = Column(
        BigInteger,
        index=True,
        nullable=False,
    )

    photo_file_id = Column(
        Text,
        nullable=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        # order matters here!
        UniqueConstraint(
            user_id,
            message_id,
            name="xxx_raw_unique_uid_mid",
        ),
    )
