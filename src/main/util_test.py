from typing import Any
from typing import Callable

import pytest

from main.db import Raw
from main.util import safe
from main.util import select_max_size_photo
from main.util import to_values


def validate_wraps(func1: Callable, func2: Callable) -> None:
    assert func1.__name__ == func2.__name__
    assert func1.__doc__ == func2.__doc__


@pytest.mark.asyncio
async def test_safe_normal() -> None:
    async def handler(*args: Any, **kwargs: Any) -> tuple[tuple, dict]:
        """some doc"""
        return args, kwargs

    safe_handler = safe(handler)

    validate_wraps(handler, safe_handler)

    args = (1, 2, 3)
    kwargs = {"a": 4, "b": 5}

    result_original = await handler(*args, **kwargs)
    result_safe = await safe_handler(*args, **kwargs)

    assert result_original == result_safe


@pytest.mark.asyncio
async def test_safe_exc(capsys: Any) -> None:
    async def handler() -> float:
        """some doc"""
        return 1 / 0

    safe_handler = safe(handler)

    validate_wraps(handler, safe_handler)

    with pytest.raises(ZeroDivisionError):
        await handler()

    result_safe = await safe_handler()
    assert result_safe is None

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_select_max_size_photo() -> None:
    ph1 = select_max_size_photo([])
    assert ph1.file_id == ""
    assert ph1.file_size is None
    assert ph1.height == 0
    assert ph1.width == 0

    ph1 = ph1.copy(update={"file_size": 1})
    ph2 = ph1.copy(update={"file_size": 2})
    assert select_max_size_photo([ph1, ph2]) == ph2

    ph1 = ph1.copy(update={"width": 1})
    ph2 = ph1.copy(update={"width": 2})
    assert select_max_size_photo([ph1, ph2]) == ph2

    ph1 = ph1.copy(update={"height": 1})
    ph2 = ph1.copy(update={"height": 2})
    assert select_max_size_photo([ph1, ph2]) == ph2


def test_to_values() -> None:
    map_fields = {
        Raw.user_id: 1,
        Raw.book_id: 2,
    }

    map_field_names = {
        "user_id": 1,
        "book_id": 2,
    }

    assert to_values(map_fields) == map_field_names
    assert to_values(map_field_names) == map_field_names
