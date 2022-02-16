import traceback
from functools import wraps
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import TypeVar

from consigliere.telegram.entities import PhotoSize


def safe(handler: Callable) -> Callable:
    @wraps(handler)
    async def safe_handler(*args: Any, **kwargs: Any) -> Any:
        try:
            return await handler(*args, **kwargs)
        except Exception:
            traceback.print_exc()

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


def to_values(field_to_value_map: Dict[Any, T1]) -> Dict[str, T1]:
    return {
        (field.key if not isinstance(field, str) else field): value
        for field, value in field_to_value_map.items()
    }
