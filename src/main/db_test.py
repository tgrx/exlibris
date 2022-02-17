import os
from unittest import mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from main.db import begin_session_txn
from main.db import get_db_url

pytestmark = [
    pytest.mark.unit,
]

envs_default = {
    "TELEGRAM_BOT_TOKEN": "TELEGRAM_BOT_TOKEN",
    "WEBHOOK_SECRET": "WEBHOOK_SECRET",
}


@mock.patch.dict(os.environ, envs_default, clear=True)
@mock.patch("framework.config.Settings.Config.secrets_dir", None)
@pytest.mark.parametrize(
    "env,actual",
    (
        ("postgres://u:p@h:1/d", "postgresql://u:p@h:1/d"),
        ("postgres://u:p@h:1/d?ssl=True", "postgresql://u:p@h:1/d"),
        ("postgresql://u:p@h:1/d", "postgresql://u:p@h:1/d"),
        ("postgresql://u:p@h:1/d?ssl=True", "postgresql://u:p@h:1/d"),
    ),
)
def test_schema_adaptation_1(env: str, actual: str) -> None:
    assert get_db_url(env) == actual


@pytest.mark.asyncio
async def test_begin_session() -> None:
    async with begin_session_txn() as sess:
        assert isinstance(sess, AsyncSession)
