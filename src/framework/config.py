from multiprocessing import cpu_count
from typing import NoReturn
from typing import Optional
from urllib.parse import urlsplit

from pydantic import BaseSettings
from pydantic import Field
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper

from framework.dirs import DIR_CONFIG_SECRETS


class _Settings(BaseSettings):
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        secrets_dir = DIR_CONFIG_SECRETS.as_posix()


class DatabaseSettings(_Settings):
    DATABASE_URL: Optional[str] = Field(make_secret=True)
    DB_DRIVER: Optional[str] = Field(exclude=True)
    DB_HOST: Optional[str] = Field(exclude=True)
    DB_NAME: Optional[str] = Field(
        env=[
            "DB_NAME",
            "POSTGRES_DB",
        ],
        exclude=True,
    )
    DB_PASSWORD: Optional[str] = Field(
        env=[
            "DB_PASSWORD",
            "POSTGRES_PASSWORD",
        ],
        exclude=True,
    )
    DB_PORT: Optional[int] = Field(exclude=True)
    DB_USER: Optional[str] = Field(
        env=[
            "DB_USER",
            "POSTGRES_USER",
        ],
        exclude=True,
    )

    def database_url_from_db_components(self) -> str:
        def fail_validation(error_message: str) -> NoReturn:
            raise ValidationError(
                errors=[
                    ErrorWrapper(
                        exc=ValueError(error_message),
                        loc="schema",
                    )
                ],
                model=DatabaseSettings,
            )

        if not self.DB_DRIVER:
            fail_validation("db driver MUST be set")

        if not self.DB_HOST and self.DB_PORT:
            fail_validation("db host MUST be set when port is set")

        if not self.DB_USER and self.DB_PASSWORD:
            fail_validation("db user MUST be set when password is set")

        netloc = ":".join(map(str, filter(bool, (self.DB_HOST, self.DB_PORT))))
        userinfo = ":".join(filter(bool, (self.DB_USER, self.DB_PASSWORD)))  # type: ignore  # noqa: E501

        if not netloc and userinfo:
            fail_validation("netloc MUST be set when userinfo is set")

        authority = "@".join(filter(bool, (userinfo, netloc)))

        url = f"{self.DB_DRIVER}://{authority}"

        if self.DB_NAME:
            url = f"{url}/{self.DB_NAME}"

        return url


class Settings(DatabaseSettings):
    __name__ = "Settings"  # noqa: VNE003

    HEROKU_API_TOKEN: Optional[str] = Field(default=None, make_secret=True)
    HEROKU_APP_NAME: Optional[str] = Field(default=None, make_secret=True)
    HOST: str = Field(default="localhost", make_secret=True)
    MODE_DEBUG: bool = Field(default=False, make_secret=True)
    MODE_DEBUG_SQL: bool = Field(default=False, make_secret=True)
    PORT: int = Field(default=8000, make_secret=True)
    REQUEST_TIMEOUT: int = Field(default=30, make_secret=True)
    SENTRY_DSN: Optional[str] = Field(default=None, make_secret=True)
    TELEGRAM_BOT_TOKEN: str = Field(..., make_secret=True)
    TEST_SERVICE_URL: str = Field(
        default="http://localhost:8000", make_secret=True
    )
    WEB_CONCURRENCY: int = Field(default=cpu_count() * 2 + 1, make_secret=True)
    WEBHOOK_SECRET: str = Field(..., make_secret=True)

    def db_components_from_database_url(self) -> DatabaseSettings:
        if not self.DATABASE_URL:
            return DatabaseSettings()

        components = urlsplit(self.DATABASE_URL)

        return DatabaseSettings(
            DB_DRIVER=components.scheme,
            DB_HOST=components.hostname,
            DB_NAME=components.path[1:],
            DB_PASSWORD=components.password,
            DB_PORT=components.port,
            DB_USER=components.username,
        )


settings: Settings = Settings()
