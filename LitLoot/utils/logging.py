import functools
import logging
from typing import Any, Callable, Dict, TypeVar, cast
from flask import request
from config import DEBUG

# Configure file handler
file_handler = logging.FileHandler('litloot_debug.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add file handler to root logger
logging.getLogger().addHandler(file_handler)

# Get our custom logger
logger = logging.getLogger('litloot')

# Type variable for the decorated function
F = TypeVar('F', bound=Callable[..., Any])

def log_response(func: F) -> F:
    """
    Decorator that logs function responses when in debug mode.
    Logs the function name, arguments, return value, and request details.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Always allow the request to proceed
        try:
            # Log the function call and request details
            func_name: str = func.__name__
            
            # Log request details
            request_info: Dict[str, Any] = {
                "method": request.method,
                "path": request.path,
                "headers": dict(request.headers),
                "args": dict(request.args),
                "json": request.get_json(silent=True) or {},
                "form": dict(request.form)
            }
            
            # Use print for debugging to ensure we see the output
            print(f"\n=== DEBUG LOG: {func_name} ===")
            print(f"Request details: {request_info}")
            print(f"Function args: {args}, kwargs: {kwargs}")
            
            # Also use logging
            logger.debug(f"Function {func_name} called with args: {args}, kwargs: {kwargs}")
            logger.debug(f"Request details: {request_info}")
            
            # Call the original function
            result = func(*args, **kwargs)
            
            # Log the result
            print(f"Function result: {result}")
            logger.debug(f"Function {func_name} returned: {result}")
            
            return result
        except Exception as e:
            # Log the error but allow the request to proceed
            print(f"Error in {func.__name__}: {str(e)}")
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return func(*args, **kwargs)
    return cast(F, wrapper) 