import time
import functools
from PiPerW.helpers import Log

def safe_execution_wrapper(max_retries=2, timeout=5, fallback_func=None):
    """
    Middleware SRE: Executes a critical function and implements Exponential Backoff and Circuit Breaking.
    Useful for bringing up unstable hardware or executing network-dependent modules.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    delay = 2 ** retries  # Exponential Backoff
                    Log.error(f"[FailSafe] Error in {func.__name__}: {e}. Retrying {retries}/{max_retries} in {delay}s...")
                    time.sleep(delay)
                    
            Log.critical(f"[FailSafe] Circuit Breaker Activated on {func.__name__}.")
            if fallback_func:
                Log.info(f"Executing Fallback for {func.__name__}...")
                return fallback_func()
            return False # Circuit broken
        return wrapper
    return decorator
