import asyncio
import functools
from typing import Callable, Any


def async_retry(max_retries: int = 3, base_delay: float = 1.0):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (2 ** (attempt - 1))
                        await asyncio.sleep(delay)
                        log = kwargs.get("log")
                        if log:
                            log.warning(
                                "Попытка {}/{} не удалась: {}. Повтор через {:.1f}с",
                                attempt, max_retries, str(e), delay,
                            )
            raise last_exception
        return wrapper
    return decorator
