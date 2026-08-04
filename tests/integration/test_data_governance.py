import pytest
import os
import json
from unittest.mock import patch, MagicMock

from services.data_governance import DataGovernanceService

class TestDataGovernanceService:

    @pytest.fixture
    def mock_supabase(self):
        with patch("services.data_governance.get_supabase") as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def service(self, mock_supabase):
        return DataGovernanceService("fake_token")

    @pytest.fixture
    def temp_log_file(self, tmp_path):
        log_file = tmp_path / "app.log"
        # Write some fake log lines
        log_file.write_text(
            '{"event": "Tool Invoked", "user_id": "test_user_123"}\n'
            '{"event": "System startup", "user_id": "system"}\n'
            '{"event": "Tool Failed", "user_id": "test_user_123"}\n'
        )
        return str(log_file)

    def test_export_tenant_data(self, service, mock_supabase):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "odoo_url": "https://test.odoo.com"}]
        mock_supabase.table().select().eq().execute.return_value = mock_response

        # Execute
        result = service.export_tenant_data("test_user_123")

        # Verify
        assert result["tenant_id"] == "test_user_123"
        assert "export_timestamp" in result
        assert result["middleware_data"]["workspaces"] == mock_response.data
        
        # Verify supabase called correctly
        mock_supabase.table.assert_called_with("user_workspaces")
        mock_supabase.table().select.assert_called_with("*")
        mock_supabase.table().select().eq.assert_called_with("user_id", "test_user_123")
        mock_supabase.table().select().eq().execute.assert_called_once()

    def test_log_scrubbing_and_verification(self, service, temp_log_file):
        user_id = "test_user_123"
        
        # Verify initial state
        assert not service._verify_log_scrubbing(temp_log_file, user_id)
        
        # Scrub logs
        scrubbed_count = service._scrub_log_file(temp_log_file, user_id)
        
        assert scrubbed_count == 2
        
        # Verify final state
        assert service._verify_log_scrubbing(temp_log_file, user_id)
        
        # Verify file contents manually
        with open(temp_log_file, "r") as f:
            content = f.read()
            assert "test_user_123" not in content
            assert "[REDACTED_USER]" in content

    def test_delete_tenant_data_workflow(self, service, mock_supabase, temp_log_file, monkeypatch):
        user_id = "test_user_123"
        
        original_scrub = service._scrub_log_file
        def mock_scrub(path, uid):
            return original_scrub(temp_log_file, uid)
            
        original_verify = service._verify_log_scrubbing
        def mock_verify(path, uid):
            return original_verify(temp_log_file, uid)
            
        monkeypatch.setattr(service, "_scrub_log_file", mock_scrub)
        monkeypatch.setattr(service, "_verify_log_scrubbing", mock_verify)
        
        # Execute deletion
        result = service.delete_tenant_data(user_id)
        
        # Verify database deletion called
        mock_supabase.table.assert_called_with("user_workspaces")
        mock_supabase.table().delete.assert_called_once()
        mock_supabase.table().delete().eq.assert_called_with("user_id", user_id)
        mock_supabase.table().delete().eq.return_value.execute.assert_called_once()
        
        # Verify result
        assert result["status"] == "success"
        assert result["deleted_user_id"] == user_id
        assert result["log_lines_scrubbed"] == 2
        assert result["verification_passed"] is True
