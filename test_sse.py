import urllib.request
import sys

def connect_sse():
    req = urllib.request.Request('http://127.0.0.1:8000/sse?token=dummy', headers={'Accept': 'text/event-stream'})
    try:
        with urllib.request.urlopen(req) as res:
            print('SSE Connected!')
            for i in range(5):
                line = res.readline().decode()
                if line:
                    print('SSE:', line.strip())
    except Exception as e:
        print('SSE Error:', e)
        if hasattr(e, 'read'):
            print(e.read().decode())

connect_sse()
