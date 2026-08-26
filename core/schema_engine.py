from typing import Any, Dict, List, Optional
from core.logger import get_logger
from core.exceptions import OdooSchemaMismatchError

logger = get_logger(__name__)

class SchemaEngine:
    def __init__(self, connector: Any):
        self.connector = connector
        
    def get_model_fields_cached(self, model: str) -> Dict[str, Any]:
        """Fetch and cache fields_get for a given model."""
        return self.connector.get_model_fields(model)
        
    def has_model(self, model: str) -> bool:
        """Check if a model exists by attempting to fetch its fields."""
        try:
            fields = self.connector.get_model_fields(model)
            return bool(fields)
        except Exception:
            return False

    def has_field(self, model: str, field: str) -> bool:
        """Check if a field exists on a model."""
        try:
            fields = self.get_model_fields_cached(model)
            return field in fields
        except Exception:
            return False

    def filter_and_alias_fields(self, model: str, requested_fields: List[str], aliases: Dict[str, List[str]] = None) -> List[str]:
        """
        Filter requested fields to only those that exist on the model.
        Resolve aliases if the primary field is missing.
        """
        try:
            valid_fields = self.get_model_fields_cached(model)
            if not valid_fields:
                return requested_fields # Fallback if fields_get fails
        except Exception as e:
            logger.warning(f"Failed to fetch fields for {model}: {e}")
            return requested_fields # Fallback to original
            
        final_fields = []
        aliases = aliases or {}
        
        for field in requested_fields:
            if field in valid_fields:
                final_fields.append(field)
            elif field in aliases:
                # Try fallbacks
                for alias in aliases[field]:
                    if alias in valid_fields:
                        final_fields.append(alias)
                        break
                else:
                    logger.debug(f"Field '{field}' and aliases {aliases[field]} missing on {model}")
            else:
                logger.debug(f"Field '{field}' missing on {model}")
                
        return final_fields

    def validate_domain(self, model: str, domain: List[Any]) -> None:
        """Validate domain conditions referencing non-existent fields."""
        if not domain:
            return
            
        try:
            valid_fields = self.get_model_fields_cached(model)
            if not valid_fields:
                return
        except Exception:
            return
            
        for condition in domain:
            if isinstance(condition, (list, tuple)) and len(condition) == 3:
                field_name = condition[0]
                # Handle relationship dot notation e.g., 'partner_id.name'
                base_field = str(field_name).split('.')[0]
                
                if base_field not in valid_fields:
                    raise OdooSchemaMismatchError(
                        f"Field '{base_field}' used in search domain does not exist on model '{model}'. "
                        f"Try checking the schema using get_model_fields."
                    )

    def validate_write_data(self, model: str, data: Dict[str, Any]) -> None:
        """Validate that all fields in the write payload exist on the target model."""
        if not data:
            return
            
        try:
            valid_fields = self.get_model_fields_cached(model)
            if not valid_fields:
                return
        except Exception:
            return
            
        invalid_fields = set(data.keys()) - set(valid_fields.keys())
        if invalid_fields:
            raise OdooSchemaMismatchError(
                f"Cannot write to model '{model}'. Fields {invalid_fields} do not exist. "
                f"Try checking the schema using get_model_fields to find the correct field names."
            )
