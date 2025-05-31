from __future__ import annotations

import re
from typing import TypeVar


_T = TypeVar("_T")


type MaybeContainer[_T] = _T | dict[str, MaybeContainer[_T]] | list[MaybeContainer[_T]]


def _camel_to_snake(name: str) -> str:
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub("([A-Z])([A-Z][a-z])", r"\1_\2", name)
    return name.lower()


def camel_to_snake_key_recursive(obj: MaybeContainer[_T]) -> MaybeContainer[_T]:
    if isinstance(obj, dict):
        return {
            _camel_to_snake(key): camel_to_snake_key_recursive(value)
            for key, value in obj.items()
        }
    elif isinstance(obj, list):
        return [camel_to_snake_key_recursive(item) for item in obj]
    return obj
