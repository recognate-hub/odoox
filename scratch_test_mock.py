import json

def test_component_shortages():
    print("\n--- Testing Production: Component Shortages (MOCKED) ---")
    
    # Mock data returned from Odoo
    mock_moves = [
        {"product_id": [101, "Wood Panel"], "product_uom_qty": 50, "quantity": 10, "raw_material_production_id": [1, "MO/001"]},
        {"product_id": [102, "Screws"], "product_uom_qty": 500, "quantity": 0, "raw_material_production_id": [1, "MO/001"]},
        {"product_id": [101, "Wood Panel"], "product_uom_qty": 20, "quantity": 20, "raw_material_production_id": [2, "MO/002"]}
    ]
    
    mock_stock = [
        {"id": 101, "name": "Wood Panel", "qty_available": 30, "virtual_available": 30},
        {"id": 102, "name": "Screws", "qty_available": 1000, "virtual_available": -100}
    ]
    
    class MockOdoo:
        def get_mo_raw_materials(self, limit):
            return mock_moves
        def search_read_records(self, model, domain, fields, limit):
            return mock_stock
            
    from services.production import ProductionService
    service = ProductionService(MockOdoo())
    
    result = service.analyze_component_shortages()
    print(json.dumps(result, indent=2))

def test_production_delays():
    print("\n--- Testing Production: Predictive Delays (MOCKED) ---")
    
    mock_wos = [
        {"id": 1, "name": "Assembly", "production_id": [1, "MO/001"], "workcenter_id": [1, "Assembly Line 1"], "duration": 150, "duration_expected": 100},
        {"id": 2, "name": "Painting", "production_id": [2, "MO/002"], "workcenter_id": [2, "Paint Booth"], "duration": 40, "duration_expected": 50}
    ]
    
    class MockOdoo:
        def get_active_work_orders_duration(self, limit):
            return mock_wos
            
    from services.production import ProductionService
    service = ProductionService(MockOdoo())
    
    result = service.predict_production_delays()
    print(json.dumps(result, indent=2))

def test_quality_trends():
    print("\n--- Testing Quality: SPC Trends (MOCKED) ---")
    
    mock_checks = [
        {"id": 1, "point_id": [1, "Diameter"], "test_type": "measure", "measure": 10.1, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5, "control_date": "2026-08-01"},
        {"id": 2, "point_id": [1, "Diameter"], "test_type": "measure", "measure": 10.2, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5, "control_date": "2026-08-02"},
        {"id": 3, "point_id": [1, "Diameter"], "test_type": "measure", "measure": 10.15, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5, "control_date": "2026-08-03"},
        {"id": 4, "point_id": [1, "Diameter"], "test_type": "measure", "measure": 10.3, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5, "control_date": "2026-08-04"},
        {"id": 5, "point_id": [1, "Diameter"], "test_type": "measure", "measure": 10.35, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5, "control_date": "2026-08-05"},
        # Older checks
        {"id": 6, "point_id": [1, "Diameter"], "test_type": "measure", "measure": 10.0, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5, "control_date": "2026-07-01"},
        {"id": 7, "point_id": [1, "Diameter"], "test_type": "measure", "measure": 10.05, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5, "control_date": "2026-07-02"},
        {"id": 8, "point_id": [1, "Diameter"], "test_type": "measure", "measure": 9.95, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5, "control_date": "2026-07-03"},
        {"id": 9, "point_id": [1, "Diameter"], "test_type": "measure", "measure": 10.0, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5, "control_date": "2026-07-04"},
        {"id": 10, "point_id": [1, "Diameter"], "test_type": "measure", "measure": 9.9, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5, "control_date": "2026-07-05"},
    ]
    
    class MockOdoo:
        def get_quality_checks(self, product_id, limit):
            return mock_checks
            
    from services.quality import QualityService
    service = QualityService(MockOdoo())
    
    result = service.analyze_quality_trends(product_id=1, metric_label="Diameter")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    test_component_shortages()
    test_production_delays()
    test_quality_trends()
