import xmlrpc.client

url = "https://recognate.odoo.com/"
username = "recognate.hub@gmail.com"
password = "0d0126c1a54cca3a2ff109576bd06e1bcf1a97f1"

for db in ["recognate", "recognate.odoo.com", "recognate-hub"]:
    common = xmlrpc.client.ServerProxy(f"{url.rstrip('/')}/xmlrpc/2/common")
    try:
        uid = common.authenticate(db, username, password, {})
        if uid:
            print(f"SUCCESS with db={db}! UID: {uid}")
            break
        else:
            print(f"Failed with db={db}")
    except Exception as e:
        print(f"Exception with db={db}: {e}")
