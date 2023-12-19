import threading
from functools import wraps
from typing import Callable, Any, Optional, List


class TimeoutError(Exception):
    """Exception to be raised when a function call times out."""


def timeout(seconds: int) -> Callable:
    """Decorator to timeout a function after a certain number of seconds."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = [None]
            exception: List[Optional[Exception]] = [None]

            def target() -> None:
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=target)
            thread.start()
            # automatically kills thread if it's goes too long
            thread.join(seconds)

            if exception[0]:
                raise exception[0]

            return result[0]

        return wrapper

    return decorator
