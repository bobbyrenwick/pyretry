import time

from functools import wraps


def retry(exceptions_to_catch, num_retries=5, timeout=0, hook=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            timeout_is_func = hasattr(timeout, '__call__')

            for i in range(num_retries + 1):
                attempt_number = i + 1

                try:
                    return func(*args, **kwargs)
                except exceptions_to_catch as e:
                    if i == num_retries:
                        raise e

                    t = timeout(attempt_number) if timeout_is_func else timeout

                    if hook is not None:
                        hook(e, attempt_number, t)

                    if timeout:
                        time.sleep(t)

        return wrapper
    return decorator
