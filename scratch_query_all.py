import sys
import os
import json

sys.path.append(os.path.abspath("."))
from config.settings import get_settings
from odoo.xmlrpc import XmlRpcOdooConnector
from repositories.odoo import OdooRepository
import core.context
from core.context import current_token

def query_database():
    print("Connecting to live Odoo database to query CRM, Production, and Quality data...")
    
    # Use the live token
    test_token = "odx_ENVELOPE_V1:gAAAAABqhgo6BfV4g4JEp0VbRHx7vWDi_edIQbsqj_yLE0ET5xuhotljBj-Bhn1Ygar7ypG4An7570GdIpCSCzGeCcUso_Hie4ygMHiaIDE_oFkbfzMoMj3ErMt-p4SbgGo08-z9E1AD:gAAAAABqhgo6CkLN_1TyPWx5ZM3xqfmEVB4nulwTxn-ywoQuttM6IyHZQtnvs7WihzmS3JciCY-0qcZi_IYUEAzovbluwG97U_7xqrQvTKPHjmFpEV-8d032Fs6yQPniJh73eWfJ-ffl0lh4Verov6dmPENGcThBbho5QIvhRz1DFs5AuvvD7DIhpnuEiwccrAqWhbPHhhHPfuLP5Y5GnXNViOoB3UsBTQWiy5Q5Zvd24_9-FKygrCUqhDkWo_pPLf3ZBkyFYoj28f-1f53EIeUQXG21uTQTgr_TtqOqOOZZlNaikWW-XEHM5lbZjRkBoYksTKgEFX-JdSpQryY75f9y4isF6TtVh1z4L19OQNU3qe_tmINvueZ0anR96HZ_nUjK4L-Np4bch4nEnuHybJ_0kgqokMk89KrmDL-4-HF8_YflxRMLwu20HDFbwJsMat2KFM5LaYDYPB4akI0wBKJUi8g6HtKQxd04kyIsRA9T_-KgogWvzsV5DXUf3zsMbJxV1I3Wn_-V4cCyFK-sATVKAPK9-EPT0j986s74YdQfmGUp2JCQe7zHM5hScvU6SPdjELswrEkbyNCS_FAUedku75HabZKs1h8cnlJvEiqv9K3XZ6247b9xMAswdFkMy8jgoOfRlTxeiWqVgNsrmwHBa3ZszeDlJQ=="
    current_token.set(test_token)
    
    settings = get_settings()
    connector = XmlRpcOdooConnector(settings)
    repo = OdooRepository(connector)
    
    results = {}
    
    try:
        # 1. CRM
        print("Querying CRM Leads...")
        leads = repo.search_read_records("crm.lead", limit=5, fields=["name", "stage_id", "expected_revenue"])
        results["CRM Leads"] = leads
        
        # 2. Production
        print("Querying Production Orders...")
        mos = repo.search_read_records("mrp.production", limit=5, fields=["name", "product_id", "product_qty", "state"])
        results["Production Orders"] = mos
        
        # 3. Quality
        print("Querying Quality Checks...")
        checks = repo.search_read_records("quality.check", limit=5, fields=["name", "product_id", "quality_state"])
        results["Quality Checks"] = checks
        
        # Write to file
        with open("scratch/db_query_results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        print("SUCCESS! Data saved to scratch/db_query_results.json")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    os.makedirs("scratch", exist_ok=True)
    query_database()
