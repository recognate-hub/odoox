from datetime import UTC, datetime
from typing import Any, ClassVar

from core.exceptions import FinOpsBudgetExceededException
from core.logger import get_logger
import os

logger = get_logger(__name__)

# Default global budget from env var, defaulting to 1000
try:
    GLOBAL_DAILY_BUDGET = int(os.environ.get("GLOBAL_DAILY_BUDGET", "1000"))
except ValueError:
    GLOBAL_DAILY_BUDGET = 1000

class FinOpsService:
    """
    Tracks tenant API usage and enforces daily budgets to prevent runaway costs.
    Uses Redis when available for multi-worker persistence, falls back to in-memory.
    """
    
    # In-memory fallback
    _usage_store: ClassVar[dict[str, dict[str, int]]] = {}
    
    def __init__(self, daily_budget_limit: int = GLOBAL_DAILY_BUDGET):
        """
        Initialize the FinOps service with the global daily budget.
        """
        self.daily_budget_limit = daily_budget_limit

    @property
    def today(self) -> str:
        return datetime.now(UTC).date().isoformat()

    def _get_tenant_usage(self, tenant_id: str) -> int:
        from core.cache import redis_client
        if redis_client:
            try:
                redis_key = f"finops:{tenant_id}:{self.today}"
                val = redis_client.get(redis_key)
                return int(val) if val else 0
            except Exception as e:
                logger.warning(f"Redis get failed for FinOps, falling back to in-memory: {e}")
        
        # In-memory fallback
        if tenant_id not in self._usage_store or self.today not in self._usage_store[tenant_id]:
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
            
        from core.cache import redis_client
        if redis_client:
            try:
                redis_key = f"finops:{tenant_id}:{self.today}"
                new_usage = redis_client.incr(redis_key)
                if new_usage == 1:
                    redis_client.expire(redis_key, 172800) # 48 hours TTL
                usage_to_log = new_usage
            except Exception as e:
                logger.warning(f"Redis incr failed for FinOps, falling back to in-memory: {e}")
                self._record_in_memory(tenant_id)
                usage_to_log = self._usage_store[tenant_id][self.today]
        else:
            self._record_in_memory(tenant_id)
            usage_to_log = self._usage_store[tenant_id][self.today]
        
        logger.debug(
            "FinOps: Operation recorded", 
            tenant_id=tenant_id, 
            tool=tool_name, 
            usage=usage_to_log,
            budget=self.daily_budget_limit
        )

    def _record_in_memory(self, tenant_id: str):
        if tenant_id not in self._usage_store or self.today not in self._usage_store[tenant_id]:
            self._usage_store[tenant_id] = {self.today: 0}
        self._usage_store[tenant_id][self.today] += 1

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
