import sys
import os
import traceback

sys.path.append(os.path.abspath("."))
from config.settings import get_settings
from odoo.xmlrpc import XmlRpcOdooConnector
import core.context
from core.context import current_token
from core.exceptions import OdooReadOnlyError

def test_isolation():
    global core
    print("Testing Phase 1 Isolation Layer...")
    settings = get_settings()
    
    # We don't even need a valid token to test the isolation layer, because the check 
    # happens before authentication in `_execute`! Oh wait, `_authenticate` is called after
    # the check! Excellent. Let's provide a dummy token anyway just in case.
    current_token.set("dummy")
    connector = XmlRpcOdooConnector(settings)
    
    try:
        # Attempt to create a record, this should be blocked immediately
        print("Attempting to execute 'create' method...")
        connector._execute("res.partner", "create", {"name": "Hacker Partner"})
        print("FAIL: The isolation layer did not block the write request!")
    except OdooReadOnlyError as e:
        print(f"SUCCESS: The isolation layer blocked the request.")
        print(f"Error Message: {e}")
    except Exception as e:
        print("FAIL: An unexpected error occurred.")
        traceback.print_exc()

if __name__ == "__main__":
    test_isolation()
