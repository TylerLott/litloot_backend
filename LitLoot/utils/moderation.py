import functools
from typing import Any, Callable, Dict, List, Tuple, TypeVar, cast
from flask import request, jsonify, Response
from .openai_client import get_client

F = TypeVar('F', bound=Callable[..., Any])

def moderate_prompt(prompt_key: str = "query") -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Skip moderation for all routes
            return func(*args, **kwargs)
        return cast(F, wrapper)
    return decorator

def check_moderation(text: str) -> Tuple[bool, Dict[str, float]]:
    try:
        client = get_client()
        result = client.moderations.create(input=text)
        output = result.results[0]
        
        # Only consider categories with very high confidence (> 0.9)
        flagged_categories = {
            k: v for k, v in output.category_scores.items() 
            if v > 0.9 and k in ["hate", "hate/threatening", "self-harm", "violence", "violence/graphic"]
        }
        
        # Only flag if there are actual concerning categories
        return bool(flagged_categories), flagged_categories
    except Exception as e:
        print(f"Moderation API error: {str(e)}")
        return False, {}  # Allow the request if moderation fails
