import sys
import os
import json

sys.path.append(os.path.abspath("."))
from config.settings import get_settings
from odoo.xmlrpc import XmlRpcOdooConnector
from repositories.odoo import OdooRepository
from services.inventory import InventoryService
from services.invoicing import InvoicingService
import core.context
from core.context import current_token

def test_phase4():
    print("Testing Phase 4: Financial & Inventory Deep Analytics...")
    
    # We must use the live token for this test to fetch real data
    # We'll use the token provided by the user in the conversation
    test_token = "odx_ENVELOPE_V1:gAAAAABqhgo6BfV4g4JEp0VbRHx7vWDi_edIQbsqj_yLE0ET5xuhotljBj-Bhn1Ygar7ypG4An7570GdIpCSCzGeCcUso_Hie4ygMHiaIDE_oFkbfzMoMj3ErMt-p4SbgGo08-z9E1AD:gAAAAABqhgo6CkLN_1TyPWx5ZM3xqfmEVB4nulwTxn-ywoQuttM6IyHZQtnvs7WihzmS3JciCY-0qcZi_IYUEAzovbluwG97U_7xqrQvTKPHjmFpEV-8d032Fs6yQPniJh73eWfJ-ffl0lh4Verov6dmPENGcThBbho5QIvhRz1DFs5AuvvD7DIhpnuEiwccrAqWhbPHhhHPfuLP5Y5GnXNViOoB3UsBTQWiy5Q5Zvd24_9-FKygrCUqhDkWo_pPLf3ZBkyFYoj28f-1f53EIeUQXG21uTQTgr_TtqOqOOZZlNaikWW-XEHM5lbZjRkBoYksTKgEFX-JdSpQryY75f9y4isF6TtVh1z4L19OQNU3qe_tmINvueZ0anR96HZ_nUjK4L-Np4bch4nEnuHybJ_0kgqokMk89KrmDL-4-HF8_YflxRMLwu20HDFbwJsMat2KFM5LaYDYPB4akI0wBKJUi8g6HtKQxd04kyIsRA9T_-KgogWvzsV5DXUf3zsMbJxV1I3Wn_-V4cCyFK-sATVKAPK9-EPT0j986s74YdQfmGUp2JCQe7zHM5hScvU6SPdjELswrEkbyNCS_FAUedku75HabZKs1h8cnlJvEiqv9K3XZ6247b9xMAswdFkMy8jgoOfRlTxeiWqVgNsrmwHBa3ZszeDlJQ=="
    current_token.set(test_token)
    
    settings = get_settings()
    connector = XmlRpcOdooConnector(settings)
    repo = OdooRepository(connector)
    
    try:
        inv_service = InventoryService(repo)
        print("\n--- 1. Testing Inventory Health Analysis (Dead Stock) ---")
        inv_health = inv_service.analyze_inventory_health()
        print(json.dumps(inv_health, indent=2))
        
        invoicing_service = InvoicingService(repo)
        print("\n--- 2. Testing Cashflow Shortage Prediction (AR vs AP) ---")
        cashflow = invoicing_service.predict_cashflow_shortages()
        print(json.dumps(cashflow, indent=2))
        
    except Exception as e:
        print(f"Error testing Phase 4: {e}")

if __name__ == "__main__":
    test_phase4()
