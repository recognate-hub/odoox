import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from config.settings import Settings
from main import app
from services.ultron import UltronService
import mcp_app.tools.ultron as ultron_tools

client = TestClient(app)


def test_ultron_service_headers():
    service = UltronService(base_url="http://test.ultron", api_key="test_key_123")
    headers = service.headers
    assert headers["Authorization"] == "Bearer test_key_123"
    assert headers["Content-Type"] == "application/json"

    service_no_key = UltronService(base_url="http://test.ultron", api_key="")
    assert "Authorization" not in service_no_key.headers


def test_ultron_service_build_payload():
    service = UltronService()
    payload = service._build_payload(
        payment_id="pay_123",
        order_id="SO001",
        amount_paise=49900,
        currency="INR",
        reason_code="BANK_DECLINE",
        customer_id="cust_42",
        customer_email="test@example.com",
        customer_phone="+919876543210",
        event_id="evt_custom_001",
    )
    assert payload["event_id"] == "evt_custom_001"
    assert payload["event_type"] == "payment.failed"
    assert payload["payment_id"] == "pay_123"
    assert payload["order_id"] == "SO001"
    assert payload["amount_paise"] == 49900
    assert payload["currency"] == "INR"
    assert payload["reason_code"] == "BANK_DECLINE"
    assert payload["customer_id"] == "cust_42"
    assert payload["customer_email"] == "test@example.com"
    assert payload["customer_phone"] == "+919876543210"


@pytest.mark.asyncio
async def test_ultron_service_ingest_async():
    service = UltronService(base_url="http://localhost:3001", api_key="test_key")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "received", "event_id": "evt_test"}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        res = await service.ingest_failed_payment(
            payment_id="pay_999",
            order_id="SO0099",
            amount_paise=150000,
        )
        assert res["status"] == "received"
        mock_post.assert_called_once()


def test_ultron_service_ingest_sync():
    service = UltronService(base_url="http://localhost:3001", api_key="test_key")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "received", "event_id": "evt_sync"}
    mock_response.raise_for_status = MagicMock()

    with patch("requests.post") as mock_post:
        mock_post.return_value = mock_response
        res = service.ingest_failed_payment_sync(
            payment_id="pay_sync_1",
            order_id="SO00Sync",
            amount_paise=50000,
        )
        assert res["status"] == "received"
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_ultron_service_opportunities_and_records():
    service = UltronService(base_url="http://localhost:3001", api_key="test_key")
    
    mock_opp_response = MagicMock()
    mock_opp_response.json.return_value = [{"opportunity_id": "opp_1", "status": "active"}]
    mock_opp_response.raise_for_status = MagicMock()

    mock_rec_response = MagicMock()
    mock_rec_response.json.return_value = [{"execution_id": "exec_1", "payment_link": "https://rzp.io/i/abc"}]
    mock_rec_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_opp_response
        opps = await service.get_recovery_opportunities()
        assert len(opps) == 1
        assert opps[0]["opportunity_id"] == "opp_1"

        mock_get.return_value = mock_rec_response
        recs = await service.get_execution_records()
        assert len(recs) == 1
        assert recs[0]["payment_link"] == "https://rzp.io/i/abc"


def test_router_ingest_failed_payment_endpoint():
    with patch("services.ultron.UltronService.ingest_failed_payment", new_callable=AsyncMock) as mock_ingest:
        mock_ingest.return_value = {"event_id": "evt_endpoint_1", "status": "processed"}
        payload = {
            "payment_id": "pay_tx_100",
            "order_id": "SO00100",
            "amount_paise": 199900,
            "currency": "INR",
            "reason_code": "INSUFFICIENT_FUNDS",
            "customer_id": "partner_55",
            "customer_email": "user@example.com",
            "customer_phone": "+919999988888",
        }
        response = client.post("/api/v1/ultron/events/failed-payment", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["data"]["event_id"] == "evt_endpoint_1"


def test_router_opportunities_and_execution_records():
    with patch("services.ultron.UltronService.get_recovery_opportunities", new_callable=AsyncMock) as mock_opps, \
         patch("services.ultron.UltronService.get_execution_records", new_callable=AsyncMock) as mock_recs:
        mock_opps.return_value = [{"id": "opp_123"}]
        mock_recs.return_value = [{"id": "exec_123", "link": "https://rzp.io/i/xyz"}]

        resp1 = client.get("/api/v1/ultron/opportunities")
        assert resp1.status_code == 200
        assert resp1.json()["data"] == [{"id": "opp_123"}]

        resp2 = client.get("/api/v1/ultron/execution-records")
        assert resp2.status_code == 200
        assert resp2.json()["data"] == [{"id": "exec_123", "link": "https://rzp.io/i/xyz"}]


def test_mcp_ultron_tools():
    with patch("services.ultron.UltronService.ingest_failed_payment_sync") as mock_ingest, \
         patch("services.ultron.UltronService.get_recovery_opportunities_sync") as mock_opps, \
         patch("services.ultron.UltronService.get_execution_records_sync") as mock_recs, \
         patch("mcp_app.security.get_current_user_context") as mock_user_ctx:
        
        mock_user_ctx.return_value = MagicMock(role="Admin", user_id="admin_1")
        mock_ingest.return_value = {"event_id": "evt_mcp", "status": "queued"}
        mock_opps.return_value = [{"opp_id": "1"}]
        mock_recs.return_value = [{"exec_id": "2"}]

        res_ingest = ultron_tools.notify_ultron_payment_failed(
            payment_id="pay_mcp_1",
            order_id="SO00MCP",
            amount_paise=75000,
        )
        assert res_ingest["status"] == "success"

        res_opps = ultron_tools.get_ultron_recovery_opportunities()
        assert res_opps["status"] == "success"

        res_recs = ultron_tools.get_ultron_recovery_links()
        assert res_recs["status"] == "success"
