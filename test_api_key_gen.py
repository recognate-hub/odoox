from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_gen():
    print('Testing /api/workspace/api-key ...')
    # Mock get_workspace_credentials so it doesn't need DB
    with patch('core.context.get_workspace_credentials') as mock_creds:
        from core.context import WorkspaceContext
        mock_creds.return_value = WorkspaceContext(odoo_url='url', odoo_db='db', odoo_username='user', odoo_password='pwd', user_id='test-user')
        
        # Override dependency
        from routers.admin import get_user_token
        app.dependency_overrides[get_user_token] = lambda: 'test-token'
        
        response = client.get('/api/workspace/api-key')
        print(f'Response status: {response.status_code}')
        print(f'Response text: {response.text}')

test_gen()
