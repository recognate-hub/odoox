
import pytest

from core.exceptions import FinOpsBudgetExceededException
from services.finops import FinOpsService


class TestFinOpsService:

    @pytest.fixture(autouse=True)
    def reset_store(self):
        FinOpsService.reset_store()
        
    def test_record_invocation_increments_usage(self):
        service = FinOpsService(daily_budget_limit=10)
        tenant_id = "tenant_1"
        
        service.record_invocation(tenant_id, "test_tool")
        
        status = service.get_budget_status(tenant_id)
        assert status["usage"] == 1
        assert status["limit"] == 10
        assert status["remaining"] == 9
        assert status["status"] == "healthy"

    def test_record_invocation_blocks_on_limit_exceeded(self):
        service = FinOpsService(daily_budget_limit=2)
        tenant_id = "tenant_2"
        
        service.record_invocation(tenant_id, "test_tool")
        service.record_invocation(tenant_id, "test_tool")
        
        status = service.get_budget_status(tenant_id)
        assert status["usage"] == 2
        assert status["remaining"] == 0
        assert status["status"] == "exceeded"
        
        with pytest.raises(FinOpsBudgetExceededException) as excinfo:
            service.record_invocation(tenant_id, "test_tool")
            
        assert "exceeded their daily API budget" in str(excinfo.value)
