import asyncio
from mcp.server.sse import SseServerTransport

async def test():
    transport = SseServerTransport('/messages')
    
    async def receive():
        await asyncio.sleep(1)
        return {'type': 'http.disconnect'}
        
    async def _send(msg):
        if msg['type'] == 'http.response.body':
            print('BODY:', repr(msg.get('body', b'')))
        
    async with transport.connect_sse({'type': 'http'}, receive, _send) as streams:
        pass

asyncio.run(test())
