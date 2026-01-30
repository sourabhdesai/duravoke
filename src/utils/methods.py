from inspect import signature
from typing import Any, Callable, List

def positional_arguments(func: Callable[..., Any]) -> List[str]:
    """
    Get the positional arguments of a function in the order of their positioning.
    """
    return list(signature(func).parameters.keys())
