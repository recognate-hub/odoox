import inspect
import mcp.server
try:
    from mcp.server.sse import TransportSecuritySettings
    print("TransportSecuritySettings found!")
except Exception as e:
    print(e)

try:
    import mcp.shared.security
    print(inspect.getsource(mcp.shared.security))
except Exception as e:
    print("mcp.shared.security:", e)
