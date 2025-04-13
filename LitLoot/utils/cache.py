from typing import Any, Callable, Dict, TypeVar, cast
from services.vector_store import search

T = TypeVar('T')
_cache: Dict[str, Any] = {}

def get_or_set(key: str, callback: Callable[[], T]) -> T:
    if key in _cache:
        return cast(T, _cache[key])
    value: T = callback()
    _cache[key] = value
    return value