import sys
import os
import json
import sys
import os

sys.path.append(os.path.abspath("."))
from config.settings import get_settings
from odoo.xmlrpc import XmlRpcOdooConnector
from repositories.odoo import OdooRepository
from services.quality import QualityService
from services.production import ProductionService
import core.context
from core.context import current_token

def test():
    global core
    print("Connecting to LIVE Odoo...")
    settings = get_settings()
    
    # Use the live token provided by the user
    real_token = "odx_ENVELOPE_V1:gAAAAABqhgo6BfV4g4JEp0VbRHx7vWDi_edIQbsqj_yLE0ET5xuhotljBj-Bhn1Ygar7ypG4An7570GdIpCSCzGeCcUso_Hie4ygMHiaIDE_oFkbfzMoMj3ErMt-p4SbgGo08-z9E1AD:gAAAAABqhgo6CkLN_1TyPWx5ZM3xqfmEVB4nulwTxn-ywoQuttM6IyHZQtnvs7WihzmS3JciCY-0qcZi_IYUEAzovbluwG97U_7xqrQvTKPHjmFpEV-8d032Fs6yQPniJh73eWfJ-ffl0lh4Verov6dmPENGcThBbho5QIvhRz1DFs5AuvvD7DIhpnuEiwccrAqWhbPHhhHPfuLP5Y5GnXNViOoB3UsBTQWiy5Q5Zvd24_9-FKygrCUqhDkWo_pPLf3ZBkyFYoj28f-1f53EIeUQXG21uTQTgr_TtqOqOOZZlNaikWW-XEHM5lbZjRkBoYksTKgEFX-JdSpQryY75f9y4isF6TtVh1z4L19OQNU3qe_tmINvueZ0anR96HZ_nUjK4L-Np4bch4nEnuHybJ_0kgqokMk89KrmDL-4-HF8_YflxRMLwu20HDFbwJsMat2KFM5LaYDYPB4akI0wBKJUi8g6HtKQxd04kyIsRA9T_-KgogWvzsV5DXUf3zsMbJxV1I3Wn_-V4cCyFK-sATVKAPK9-EPT0j986s74YdQfmGUp2JCQe7zHM5hScvU6SPdjELswrEkbyNCS_FAUedku75HabZKs1h8cnlJvEiqv9K3XZ6247b9xMAswdFkMy8jgoOfRlTxeiWqVgNsrmwHBa3ZszeDlJQ=="
    current_token.set(real_token)
    
    connector = XmlRpcOdooConnector(settings)
    repo = OdooRepository(connector)
    quality_service = QualityService(repo)
    production_service = ProductionService(repo)
    
    print("\n--- Testing Production: Component Shortages ---")
    try:
        shortages = production_service.analyze_component_shortages()
        print(json.dumps(shortages, indent=2))
    except Exception as e:
        print("Error:", e)
        
    print("\n--- Testing Production: Predictive Delays ---")
    try:
        delays = production_service.predict_production_delays()
        print(json.dumps(delays, indent=2))
    except Exception as e:
        print("Error:", e)

    print("\n--- Testing Production: OEE Losses ---")
    try:
        oee = production_service.analyze_oee_losses(limit=100)
        print(json.dumps(oee, indent=2))
    except Exception as e:
        print("Error:", e)
        
    print("\n--- Testing Quality: Defect Root Causes ---")
    try:
        defects = quality_service.analyze_defect_root_causes()
        print(json.dumps(defects, indent=2))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test()
