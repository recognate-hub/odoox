from datetime import date
from typing import Any

from core.exceptions import FinOpsBudgetExceededException
from core.logger import get_logger

logger = get_logger(__name__)

class FinOpsService:
    """
    Tracks tenant API usage and enforces daily budgets to prevent runaway costs.
    """
    
    # Simple in-memory store for tracking budgets during testing/execution
    # In production, this would be backed by Redis or Supabase.
    _usage_store: dict[str, dict[str, int]] = {}
    
    def __init__(self, daily_budget_limit: int = 1000):
        """
        Initialize the FinOps service with a default daily budget.
        """
        self.daily_budget_limit = daily_budget_limit
        self.today = date.today().isoformat()

    def _get_tenant_usage(self, tenant_id: str) -> int:
        if tenant_id not in self._usage_store:
            self._usage_store[tenant_id] = {self.today: 0}
            
        # Handle day rollover
        if self.today not in self._usage_store[tenant_id]:
            self._usage_store[tenant_id] = {self.today: 0}
            
        return self._usage_store[tenant_id][self.today]

    def record_invocation(self, tenant_id: str, tool_name: str) -> None:
        """
        Records a single tool invocation for the tenant and checks budget limits.
        Raises FinOpsBudgetExceededException if the limit is breached.
        """
        current_usage = self._get_tenant_usage(tenant_id)
        
        if current_usage >= self.daily_budget_limit:
            logger.error("FinOps budget exceeded!", tenant_id=tenant_id, limit=self.daily_budget_limit)
            raise FinOpsBudgetExceededException(f"Tenant {tenant_id} has exceeded their daily API budget of {self.daily_budget_limit} requests.")
            
        # Increment usage
        self._usage_store[tenant_id][self.today] += 1
        
        logger.debug(
            "FinOps: Operation recorded", 
            tenant_id=tenant_id, 
            tool=tool_name, 
            usage=self._usage_store[tenant_id][self.today],
            budget=self.daily_budget_limit
        )

    def get_budget_status(self, tenant_id: str) -> dict[str, Any]:
        """
        Returns the current budget status for a tenant.
        """
        usage = self._get_tenant_usage(tenant_id)
        return {
            "tenant_id": tenant_id,
            "date": self.today,
            "usage": usage,
            "limit": self.daily_budget_limit,
            "remaining": max(0, self.daily_budget_limit - usage),
            "status": "healthy" if usage < self.daily_budget_limit else "exceeded"
        }
        
    @classmethod
    def reset_store(cls):
        """For testing purposes."""
        cls._usage_store = {}
