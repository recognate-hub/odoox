import json
import time
from typing import Any
from core.cache import redis_client
from core.logger import get_logger

logger = get_logger(__name__)

class AlertService:
    """
    Manages proactive alerts sent from Odoo (via webhooks).
    Alerts are stored per-tenant so the AI can fetch and acknowledge them.
    """
    def __init__(self, tenant_db: str):
        self.tenant_db = tenant_db
        self.queue_key = f"odoo_alerts:{tenant_db}"
        # Fallback in-memory list if redis is unavailable
        self._memory_queue = []

    def push_alert(self, event_type: str, severity: str, message: str, payload: dict[str, Any] = None) -> str:
        """Push a new alert from Odoo into the queue."""
        alert = {
            "id": f"alert_{int(time.time() * 1000)}",
            "timestamp": time.time(),
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "payload": payload or {},
            "status": "unread"
        }
        
        logger.info(f"New alert received for tenant {self.tenant_db}: {event_type} - {message}")
        
        if redis_client:
            redis_client.lpush(self.queue_key, json.dumps(alert))
            # Keep only the last 100 alerts
            redis_client.ltrim(self.queue_key, 0, 99)
        else:
            self._memory_queue.insert(0, alert)
            if len(self._memory_queue) > 100:
                self._memory_queue.pop()
                
        return alert["id"]

    def get_recent_alerts(self, limit: int = 10, unread_only: bool = True) -> list[dict[str, Any]]:
        """Fetch recent alerts for the AI to process."""
        alerts = []
        if redis_client:
            raw_alerts = redis_client.lrange(self.queue_key, 0, limit - 1)
            alerts = [json.loads(a) for a in raw_alerts]
        else:
            alerts = self._memory_queue[:limit]
            
        if unread_only:
            alerts = [a for a in alerts if a.get("status") == "unread"]
            
        return alerts

    def acknowledge_alerts(self, alert_ids: list[str]) -> dict[str, Any]:
        """Mark specific alerts as read/acknowledged by the AI."""
        if not alert_ids:
            return {"status": "success", "acknowledged": 0}
            
        count = 0
        if redis_client:
            # Redis list doesn't support easy in-place updates, so we read all, update, and rewrite
            raw_alerts = redis_client.lrange(self.queue_key, 0, -1)
            updated = []
            for raw in raw_alerts:
                alert = json.loads(raw)
                if alert["id"] in alert_ids and alert["status"] == "unread":
                    alert["status"] = "read"
                    count += 1
                updated.append(json.dumps(alert))
            
            if count > 0:
                redis_client.delete(self.queue_key)
                if updated:
                    redis_client.rpush(self.queue_key, *updated)
        else:
            for alert in self._memory_queue:
                if alert["id"] in alert_ids and alert["status"] == "unread":
                    alert["status"] = "read"
                    count += 1
                    
        return {"status": "success", "acknowledged_count": count}
