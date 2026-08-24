import os
import sys
import base64
import json

sys.path.append(os.path.abspath("."))
from services.visualization import generate_pareto_chart, generate_spc_chart

def test_visuals():
    print("Testing Visualization Generation...")
    
    # 1. Pareto Chart
    pareto_data = [
        {"loss_reason": "Material Shortage", "duration_minutes": 150},
        {"loss_reason": "Machine Breakdown", "duration_minutes": 80},
        {"loss_reason": "Operator Error", "duration_minutes": 30},
        {"loss_reason": "Setup Time", "duration_minutes": 15},
    ]
    
    print("Generating Pareto Chart...")
    pareto_b64 = generate_pareto_chart(pareto_data, title="OEE Losses Pareto Chart")
    
    if pareto_b64:
        with open("pareto_test.png", "wb") as fh:
            fh.write(base64.b64decode(pareto_b64))
        print(" -> SUCCESS: Saved to pareto_test.png")
    else:
        print(" -> FAIL: Pareto generation failed.")
        
    # 2. SPC Chart
    spc_data = [
        {"date": "Day 1", "measure": 10.1, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5},
        {"date": "Day 2", "measure": 10.2, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5},
        {"date": "Day 3", "measure": 10.4, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5},
        {"date": "Day 4", "measure": 10.6, "norm": 10.0, "tolerance_min": 9.5, "tolerance_max": 10.5}, # Out of bounds
    ]
    
    print("Generating SPC Chart...")
    spc_b64 = generate_spc_chart(spc_data, title="SPC Control Chart: Diameter")
    
    if spc_b64:
        with open("spc_test.png", "wb") as fh:
            fh.write(base64.b64decode(spc_b64))
        print(" -> SUCCESS: Saved to spc_test.png")
    else:
        print(" -> FAIL: SPC generation failed.")

if __name__ == "__main__":
    test_visuals()
