import asyncio
from mcp.server import Server
from mcp.server.sse import SseServerTransport

async def test():
    mcp = Server('test')
    transport = SseServerTransport('/messages')
    
    async def receive():
        await asyncio.sleep(1)
        return {'type': 'http.disconnect'}
        
    async def _send(msg):
        print('SEND:', msg['type'])
        
    async with transport.connect_sse({'type': 'http'}, receive, _send) as streams:
        print('Streams connected!')
        await mcp.run(streams[0], streams[1], mcp.create_initialization_options())
        print('Server run returned!')

asyncio.run(test())
