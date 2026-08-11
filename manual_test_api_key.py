from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_api_key_gen():
    with patch('routers.admin.get_workspace_credentials') as mock_creds:
        mock_ws = MagicMock()
        mock_ws.model_dump_json.return_value = '{"test":"data"}'
        mock_creds.return_value = mock_ws
        
        # Override get_user_token
        from routers.admin import get_user_token
        app.dependency_overrides[get_user_token] = lambda: 'test-token'
        
        response = client.get('/api/workspace/api-key')
        print('Status:', response.status_code)
        print('Data:', response.json())
            
test_api_key_gen()
