import urllib.request
import urllib.parse
import json

base_url = 'http://127.0.0.1:8000'
try:
    print('Fetching metadata...')
    res = urllib.request.urlopen(f'{base_url}/.well-known/oauth-authorization-server')
    metadata = json.loads(res.read().decode())
    print(json.dumps(metadata, indent=2))

    print('\nRegistering client...')
    reg_url = metadata['registration_endpoint']
    req_data = json.dumps({
        'client_name': 'Claude Desktop',
        'redirect_uris': ['http://127.0.0.1:54321/oauth/callback']
    }).encode()

    req = urllib.request.Request(reg_url, data=req_data, headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    client_data = json.loads(res.read().decode())
    print('Registration successful:')
    print(json.dumps(client_data, indent=2))
except Exception as e:
    print('Failed:', e)
    if hasattr(e, 'read'):
        print(e.read().decode())
