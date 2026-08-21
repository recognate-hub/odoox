import io
import xmlrpc.client


class MyTransport(xmlrpc.client.Transport):
    def request(self, host, handler, request_body, verbose=False):
        xml_resp = b"<?xml version='1.0'?><methodResponse><params><param><value><string>ok</string></value></param></params></methodResponse>"
        return self.parse_response(io.BytesIO(xml_resp))


proxy = xmlrpc.client.ServerProxy("http://localhost", transport=MyTransport())
print(proxy.test())
