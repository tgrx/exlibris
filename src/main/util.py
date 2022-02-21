from functools import wraps
from typing import Any
from typing import Callable
from typing import Iterable
from typing import TypeVar

from consigliere.telegram.entities import PhotoSize
from loguru import logger


def safe(handler: Callable) -> Callable:
    @wraps(handler)
    async def safe_handler(*args: Any, **kwargs: Any) -> Any:
        try:
            return await handler(*args, **kwargs)
        except Exception as err:
            logger.exception(err)

    return safe_handler


def select_max_size_photo(photos: Iterable[PhotoSize]) -> PhotoSize:
    if not photos:
        return PhotoSize(
            file_id="",
            file_size=None,
            file_unique_id="",
            height=0,
            width=0,
        )

    photo = max(
        photos,
        key=lambda _photo: (
            _photo.file_size,
            _photo.width,
            _photo.height,
        ),
    )

    return photo


T1 = TypeVar("T1")


def to_values(field_to_value_map: dict[Any, T1]) -> dict[str, T1]:
    """
    Converts a map { attr/str: Any } => {str: Any}.
    Useful for model field mappings.

    :param field_to_value_map: {model.attribute | "attribute name": value}
    :return: {"field name": value}
    """

    return {
        (field.key if not isinstance(field, str) else field): value
        for field, value in field_to_value_map.items()
    }
