import pytest
from unittest.mock import MagicMock
from core.schema_engine import SchemaEngine
from core.exceptions import OdooSchemaMismatchError

class MockConnector:
    def __init__(self, schemas):
        self.schemas = schemas
        
    def get_model_fields(self, model):
        if model in self.schemas:
            return self.schemas[model]
        raise Exception(f"Model {model} not found")

@pytest.fixture
def schema_engine():
    schemas = {
        "res.partner": {
            "name": {"type": "char"},
            "email": {"type": "char"},
            "parent_id": {"type": "many2one"}
        },
        "crm.lead": {
            "name": {"type": "char"},
            "expected_revenue": {"type": "float"},
        }
    }
    connector = MockConnector(schemas)
    return SchemaEngine(connector)

def test_has_model(schema_engine):
    assert schema_engine.has_model("res.partner") is True
    assert schema_engine.has_model("missing.model") is False

def test_has_field(schema_engine):
    assert schema_engine.has_field("res.partner", "email") is True
    assert schema_engine.has_field("res.partner", "missing_field") is False

def test_filter_and_alias_fields(schema_engine):
    requested = ["name", "email", "missing_field", "manager_id"]
    aliases = {"manager_id": ["parent_id", "coach_id"]}
    
    fields = schema_engine.filter_and_alias_fields("res.partner", requested, aliases)
    assert fields == ["name", "email", "parent_id"]

def test_validate_domain_valid(schema_engine):
    domain = [["name", "ilike", "test"], ["parent_id.name", "=", "Corp"]]
    # Should not raise exception
    schema_engine.validate_domain("res.partner", domain)

def test_validate_domain_invalid(schema_engine):
    domain = [["name", "ilike", "test"], ["missing_field", "=", "value"]]
    with pytest.raises(OdooSchemaMismatchError) as exc:
        schema_engine.validate_domain("res.partner", domain)
    assert "missing_field" in str(exc.value)

def test_validate_write_data_valid(schema_engine):
    data = {"name": "Test", "expected_revenue": 100.0}
    schema_engine.validate_write_data("crm.lead", data)

def test_validate_write_data_invalid(schema_engine):
    data = {"name": "Test", "x_custom_field": "value"}
    with pytest.raises(OdooSchemaMismatchError) as exc:
        schema_engine.validate_write_data("crm.lead", data)
    assert "x_custom_field" in str(exc.value)
