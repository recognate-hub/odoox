import os
import sys
import json

sys.path.append(os.path.abspath("."))
from services.alerts import AlertService

def test_alerts():
    print("Testing Proactive Webhook Alerts...")
    
    tenant_db = "recognate_demo"
    service = AlertService(tenant_db=tenant_db)
    
    print("1. Simulating incoming webhook from Odoo...")
    alert_id = service.push_alert(
        event_type="machine_breakdown",
        severity="critical",
        message="Assembly Line 1 reported a critical failure.",
        payload={"workcenter_id": 1, "downtime_expected_minutes": 120}
    )
    print(f" -> Alert successfully pushed to queue. ID: {alert_id}")
    
    print("\n2. Simulating AI Agent fetching recent alerts...")
    alerts = service.get_recent_alerts(limit=5, unread_only=True)
    print(" -> Alerts found:")
    print(json.dumps(alerts, indent=2))
    
    print("\n3. Simulating AI Agent acknowledging the alert...")
    ack_res = service.acknowledge_alerts([alert_id])
    print(f" -> {ack_res}")
    
    print("\n4. Verifying queue is now empty (for unread)...")
    alerts_after = service.get_recent_alerts(unread_only=True)
    if not alerts_after:
        print(" -> SUCCESS: Unread queue is empty.")
    else:
        print(" -> FAIL: Unread queue still has alerts.")

if __name__ == "__main__":
    test_alerts()
