import xmlrpc.client

class TimeoutTransport(xmlrpc.client.Transport):
    def __init__(self, timeout=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn

class TimeoutSafeTransport(xmlrpc.client.SafeTransport):
    def __init__(self, timeout=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn

def get_transport(url: str, timeout: int = 10):
    if url.startswith("https:"):
        return TimeoutSafeTransport(timeout=timeout)
    return TimeoutTransport(timeout=timeout)

try:
    proxy = xmlrpc.client.ServerProxy("https://recognate.odoo.com/xmlrpc/2/common", transport=get_transport("https://recognate.odoo.com/xmlrpc/2/common", timeout=2))
    print(proxy.version())
    print("HTTPS TimeoutSafeTransport OK!")
except Exception as e:
    print("Error:", e)
