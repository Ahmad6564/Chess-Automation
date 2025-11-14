"""
Helper utility functions.
"""

import time
from typing import Callable, Any
from functools import wraps


def timer(func: Callable) -> Callable:
    """
    Decorator to time function execution.
    
    Args:
        func: Function to time
    
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f}s")
        return result
    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator to retry a function on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            last_exception = None
            
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    last_exception = e
                    
                    if attempts < max_attempts:
                        print(f"Attempt {attempts} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        print(f"All {max_attempts} attempts failed.")
            
            raise last_exception
        
        return wrapper
    return decorator


def ensure_bounds(value: int, min_val: int, max_val: int) -> int:
    """
    Ensure a value is within bounds.
    
    Args:
        value: Value to check
        min_val: Minimum value
        max_val: Maximum value
    
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def parse_uci_move(move_uci: str) -> tuple:
    """
    Parse UCI move string into components.
    
    Args:
        move_uci: Move in UCI format (e.g., 'e2e4', 'e7e8q')
    
    Returns:
        Tuple of (from_square, to_square, promotion)
    """
    if len(move_uci) < 4:
        raise ValueError(f"Invalid UCI move: {move_uci}")
    
    from_square = move_uci[:2]
    to_square = move_uci[2:4]
    promotion = move_uci[4:] if len(move_uci) > 4 else None
    
    return from_square, to_square, promotion


def format_time(seconds: float) -> str:
    """
    Format seconds into a readable string.
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if division by zero.
    
    Args:
        a: Numerator
        b: Denominator
        default: Default value if b is zero
    
    Returns:
        Result of division or default
    """
    return a / b if b != 0 else default


if __name__ == "__main__":
    # Test helpers
    print("Testing helper functions...")
    
    # Test timer
    @timer
    def slow_function():
        time.sleep(0.5)
        return "Done"
    
    result = slow_function()
    print(f"Result: {result}")
    
    # Test retry
    @retry(max_attempts=3, delay=0.5)
    def failing_function():
        print("Attempting...")
        raise ValueError("Test error")
    
    # try:
    #     failing_function()
    # except ValueError:
    #     print("Function failed as expected")
    
    # Test parse UCI
    from_sq, to_sq, promo = parse_uci_move("e7e8q")
    print(f"Parsed: {from_sq} -> {to_sq}, promotion: {promo}")
    
    # Test format time
    print(f"Time formatted: {format_time(125.5)}")
