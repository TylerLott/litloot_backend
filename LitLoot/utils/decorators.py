import functools
import time
import logging
from typing import Any, Callable, TypeVar, cast

F = TypeVar('F', bound=Callable[..., Any])

def with_retry(attempts: int = 3, delay: float = 2.0) -> Callable[[F], F]:
    def wrapper(func: F) -> F:
        @functools.wraps(func)
        def retry_fn(*args: Any, **kwargs: Any) -> Any:
            for i in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"Retry {i+1}/{attempts} for {func.__name__}: {e}")
                    time.sleep(delay * (i + 1))
            raise RuntimeError(f"{func.__name__} failed after {attempts} attempts.")
        return cast(F, retry_fn)
    return wrapper
