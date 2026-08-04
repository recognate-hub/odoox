import functools
from pydantic import BaseModel, ValidationError as PydanticValidationError
from core.logger import get_logger
from core.exceptions import ValidationError

logger = get_logger(__name__)

def validate_write_input(schema_cls: type[BaseModel]):
    """
    Decorator that strictly validates kwargs against a Pydantic schema before execution.
    Logs any rejection explicitly and raises a clean ValidationError.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Validate inputs
                validated_data = schema_cls(**kwargs)
            except PydanticValidationError as e:
                # Explicit rejection logging
                logger.warning("Write Validation Rejected", tool=func.__name__, errors=e.errors())
                raise ValidationError(f"Input validation failed for {func.__name__}: {str(e)}")
            
            # Since fastmcp relies on the original signature for Claude, we can't easily 
            # inject the validated pydantic model back into kwargs if it expects primitives.
            # But we can replace kwargs with the validated dumped dict if we want, or just proceed.
            # We'll just proceed with the original kwargs if validation passes, 
            # or pass the validated dict if the signature expects it.
            # In our case, server.py tools accept primitive args. We will pass the validated data back to kwargs.
            return func(*args, **validated_data.model_dump())
        return wrapper
    return decorator
