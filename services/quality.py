from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)


class QualityService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def create_quality_alert(
        self,
        name: str,
        product_id: int,
        team_id: int | None = None,
        priority: str = "0",
    ) -> dict[str, Any]:
        alert_id = self.odoo.create_quality_alert(name, product_id, team_id, priority)
        return {"status": "success", "quality_alert_id": alert_id}

    def get_quality_checks(
        self, product_id: int | None = None, limit: int = 20, offset: int = 0, date_from: str | None = None, date_to: str | None = None
    ) -> list[dict[str, Any]]:
        return self.odoo.get_quality_checks(product_id, limit, offset, date_from, date_to)

    def get_quality_alerts(
        self, product_id: int | None = None, limit: int = 50, offset: int = 0, date_from: str | None = None, date_to: str | None = None
    ) -> list[dict[str, Any]]:
        return self.odoo.get_quality_alerts(product_id, limit, offset, date_from, date_to)

    def update_quality_alert(
        self, alert_id: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        success = self.odoo.update_quality_alert(alert_id, data)
        return (
            {"status": "success"}
            if success
            else {"status": "error", "message": "Update failed"}
        )

    def get_quality_points(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.odoo.get_quality_points(limit)

    def get_product_stage_metrics(self, product_id: int) -> dict[str, Any]:
        """
        Fetches quality checks for a product and groups the measurements
        (e.g., diameter, radius) by their manufacturing stage (work order).
        """
        try:
            checks = self.odoo.get_quality_checks(product_id=product_id, limit=500)
        except Exception as e:
            return {"status": "error", "message": f"Could not fetch quality checks: {e}", "product_id": product_id, "stages": []}
            
        if not checks:
            return {"status": "success", "product_id": product_id, "stages": [], "message": "No quality checks logged for this product."}

        # Group by workorder_id
        stages = {}
        for check in checks:
            wo_data = check.get("workorder_id")
            if not wo_data:
                wo_name = "General Quality Inspection"
                wo_id = 0
            else:
                wo_id, wo_name = wo_data[0], wo_data[1] if isinstance(wo_data, list) else (wo_data, f"Work Order {wo_data}")
                
            stage_key = f"{wo_name} (ID: {wo_id})"
            
            if stage_key not in stages:
                stages[stage_key] = {"workorder_id": wo_id, "workorder_name": wo_name, "metrics": []}
                
            # Extract metric label (from point_id or name)
            point_data = check.get("point_id")
            label = point_data[1] if isinstance(point_data, list) and len(point_data) > 1 else check.get("name", "Quality Inspection")
            
            # Extract value safely across Odoo versions
            test_type = check.get("test_type", "passfail")
            norm_val = check.get("norm", 0.0)
            if test_type == "measure":
                m_val = check.get("measure", check.get("norm", 0.0))
                value = f"{m_val} (Norm: {norm_val})"
            elif test_type == "passfail":
                value = check.get("quality_state", "none")
            else:
                value = check.get("note") or check.get("quality_state", "none")
                
            stages[stage_key]["metrics"].append({
                "check_id": check.get("id"),
                "label": label,
                "value": value,
                "date": check.get("control_date") or check.get("create_date")
            })
            
        return {
            "status": "success",
            "product_id": product_id,
            "stages": list(stages.values())
        }

    def analyze_quality_trends(self, product_id: int, metric_label: str) -> dict[str, Any]:
        """
        Analyze statistical trends for a specific metric across recent quality checks.
        """
        try:
            checks = self.odoo.get_quality_checks(product_id=product_id, limit=200)
        except Exception as e:
            return {"status": "error", "message": f"Could not fetch quality checks: {e}"}

        values = []
        for check in checks:
            point_data = check.get("point_id")
            label = point_data[1] if isinstance(point_data, list) and len(point_data) > 1 else check.get("name", "")
            
            if label.lower() == metric_label.lower() or metric_label.lower() in label.lower():
                measure = check.get("measure") or check.get("norm")
                if measure is not None:
                    try:
                        m_float = float(measure)
                        values.append({
                            "date": check.get("control_date") or check.get("create_date"),
                            "measure": m_float,
                            "norm": float(check.get("norm") or 0.0),
                            "tolerance_min": float(check.get("tolerance_min") or 0.0),
                            "tolerance_max": float(check.get("tolerance_max") or 0.0)
                        })
                    except (ValueError, TypeError):
                        pass
                    
        if not values:
            return {"status": "error", "message": f"No numerical data found for metric '{metric_label}' on product {product_id}."}
            
        measures = [v["measure"] for v in values]
        mean = sum(measures) / len(measures)
        variance = sum((x - mean) ** 2 for x in measures) / len(measures)
        std_dev = variance ** 0.5
        
        # Simple trend check (last 5 vs previous)
        trend = "stable"
        if len(measures) >= 10:
            recent_mean = sum(measures[:5]) / 5
            older_mean = sum(measures[5:10]) / 5
            if recent_mean > older_mean + (std_dev * 0.5):
                trend = "drifting upward"
            elif recent_mean < older_mean - (std_dev * 0.5):
                trend = "drifting downward"

        stats = {
            "mean": round(mean, 4),
            "std_dev": round(std_dev, 4),
            "trend": trend,
        }

        from services.visualization import generate_spc_chart
        chart_b64 = generate_spc_chart(values, title=f"SPC Control Chart: {metric_label} (Product {product_id})")

        return {
            "product_id": product_id,
            "metric_label": metric_label,
            "data_points_analyzed": len(values),
            "statistics": stats,
            "latest_values": values[:10],
            "spc_chart_base64": chart_b64
        }

    from core.cache import cache_response
    
    @cache_response(ttl_seconds=300)
    def analyze_defect_root_causes(self) -> dict[str, Any]:
        """
        Aggregate failed quality checks to pinpoint problematic workcenters/stages.
        """
        # Fetch a larger batch of quality checks (not filtered by product)
        checks = self.odoo.search_read_records(
            "quality.check", 
            domain=[("quality_state", "=", "fail")], 
            fields=["workorder_id", "product_id", "test_type"], 
            limit=500
        )
        
        bottlenecks = {}
        for check in checks:
            wo_data = check.get("workorder_id")
            if not wo_data:
                continue
                
            wo_name = wo_data[1] if isinstance(wo_data, list) else f"Work Order {wo_data}"
            if wo_name not in bottlenecks:
                bottlenecks[wo_name] = {"failures": 0, "products_affected": set()}
                
            bottlenecks[wo_name]["failures"] += 1
            prod_data = check.get("product_id")
            if prod_data and isinstance(prod_data, list):
                bottlenecks[wo_name]["products_affected"].add(prod_data[1])
                
        # Format the output and sort by failure count descending
        sorted_bottlenecks = sorted(
            [{"workcenter_stage": k, "failure_count": v["failures"], "products": list(v["products_affected"])} for k, v in bottlenecks.items()],
            key=lambda x: x["failure_count"], 
            reverse=True
        )
        
        return {
            "status": "success",
            "total_failures_analyzed": len(checks),
            "root_causes": sorted_bottlenecks
        }
        
    def log_quality_result(
        self, check_id: int, measure: float | None = None, quality_state: str | None = None
    ) -> dict[str, Any]:
        """
        Record the measurement or pass/fail state for a quality check.
        """
        success = self.odoo.update_quality_check_result(check_id, measure, quality_state)
        return (
            {"status": "success", "message": f"Quality check {check_id} updated."}
            if success
            else {"status": "error", "message": "Failed to log quality result."}
        )

