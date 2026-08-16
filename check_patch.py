from unittest.mock import MagicMock, patch

from mcp_app.tools import contacts

with patch('mcp_app.server._get_tenant_service') as mock_get:
    mock_get.return_value = (MagicMock(), MagicMock())
    print('Inside patch:', contacts.server._get_tenant_service)
    
print('Outside patch:', contacts.server._get_tenant_service)
