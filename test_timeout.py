import asyncio
from config.settings import get_settings
from odoo.xmlrpc import XmlRpcOdooConnector
from repositories.odoo import OdooRepository

def test_apps():
    settings = get_settings()
    connector = XmlRpcOdooConnector(settings)
    repo = OdooRepository(connector)

    try:
        print("Testing get_installed_apps...")
        apps = repo.get_installed_apps()
        print(f"Success! Found {len(apps)} apps.")
    except Exception as e:
        print(f"Error: {e}")

    try:
        print("Testing get_work_center_capacity...")
        from services.production import ProductionService
        service = ProductionService(repo)
        wcs = service.get_workcenters()
        print(f"Success! Found {len(wcs)} workcenters.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_apps()
