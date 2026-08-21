import json
import os
import tempfile

import pytest

from core.policy import PolicyEngine


@pytest.fixture
def policy_file():
    data = {
        "roles": {
            "Admin": ["*"],
            "Sales": ["get_leads", "create_lead"],
            "Support": ["search_contacts"],
        },
        "allowed_models": {
            "Admin": ["*"],
            "Sales": ["res.partner", "crm.lead"],
            "Support": ["res.partner"],
        },
    }
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        json.dump(data, f)
        temp_name = f.name

    yield temp_name
    os.remove(temp_name)


def test_is_allowed_admin(policy_file):
    PolicyEngine.load_policies(policy_file)
    assert PolicyEngine.is_allowed("Admin", "any_action") is True
    assert PolicyEngine.is_allowed("Admin", "destructive_action") is True


def test_is_allowed_sales(policy_file):
    PolicyEngine.load_policies(policy_file)
    assert PolicyEngine.is_allowed("Sales", "get_leads") is True
    assert PolicyEngine.is_allowed("Sales", "create_lead") is True
    assert PolicyEngine.is_allowed("Sales", "search_contacts") is False
    assert PolicyEngine.is_allowed("Sales", "unknown_action") is False


def test_is_allowed_unknown_role(policy_file):
    PolicyEngine.load_policies(policy_file)
    assert PolicyEngine.is_allowed("Hacker", "get_leads") is False


def test_is_model_allowed_admin(policy_file):
    PolicyEngine.load_policies(policy_file)
    assert (
        PolicyEngine.is_model_allowed("Admin", "search_read_records", "any.model")
        is True
    )


def test_is_model_allowed_sales(policy_file):
    PolicyEngine.load_policies(policy_file)
    assert (
        PolicyEngine.is_model_allowed("Sales", "search_read_records", "crm.lead")
        is True
    )
    assert (
        PolicyEngine.is_model_allowed("Sales", "search_read_records", "res.partner")
        is True
    )
    assert (
        PolicyEngine.is_model_allowed("Sales", "search_read_records", "hr.employee")
        is False
    )


def test_is_model_allowed_unknown_role(policy_file):
    PolicyEngine.load_policies(policy_file)
    assert (
        PolicyEngine.is_model_allowed("Hacker", "search_read_records", "crm.lead")
        is False
    )
