import asyncio
from mcp.server.sse import SseServerTransport

async def test():
    transport = SseServerTransport('/messages')
    
    async def receive():
        await asyncio.sleep(1)
        return {'type': 'http.disconnect'}
        
    class RequestMock:
        scope = {'type': 'http'}
        receive = receive
        async def _send(self, msg):
            print('SEND HTTP:', msg)
    
    req = RequestMock()
    
    async with transport.connect_sse(req.scope, req.receive, req._send) as streams:
        print('Streams connected!')

asyncio.run(test())
