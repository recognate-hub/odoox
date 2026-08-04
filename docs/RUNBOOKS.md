# ODOOX Incident Response Runbooks

## Scenario A: Supabase Auth / DB Outage
**Symptom:** Middleware returns `503 Service Unavailable` or `500 Internal Server Error` due to timeout when calling Supabase.
**Impact:** Agents cannot authenticate, and tenants cannot retrieve their Odoo credentials.
**Resolution Steps:**
1. **Verify Status:** Check `status.supabase.com`.
2. **Failover:** If the primary region (`us-east-1`) is degraded but `us-west-2` is green, trigger the DNS failover script (`scripts/failover_dns.sh`) to route to the Standby region.
3. **Communication:** Update the internal status page: "Investigating identity provider latency."
4. **Recovery:** Once Supabase resolves the issue, run the DR Drill verification (`scripts/dr_drill.py`) in read-only mode to ensure data integrity before failing back to primary.

## Scenario B: Odoo Rate Limit Exceeded (429 Too Many Requests)
**Symptom:** `OdooRateLimitException` is thrown rapidly across multiple tenants.
**Impact:** AI agents receive degraded service and cannot fetch CRM records.
**Resolution Steps:**
1. **Identify Source:** Check the FinOps Grafana dashboard to see if a single noisy-neighbor agent is exhausting the IP-based rate limit of the upstream Odoo instance.
2. **Throttle:** If a specific tenant is misbehaving, manually reduce their `FinOpsService` budget via the admin panel.
3. **Circuit Breaker:** Ensure the `CircuitBreaker` in `core/xmlrpc.py` is successfully opening and returning cached/fallback responses.

## Scenario C: Break-Glass Secret Compromise
**Symptom:** A developer accidentally leaks the `AES_KEY_256` or `SUPABASE_KEY`.
**Impact:** Critical. Total compromise of tenant Odoo credentials.
**Resolution Steps:**
1. **Execute Rotation:** Immediately execute `poetry run python test_rotation.py`. This script fetches the new key, re-encrypts all stored Odoo credentials in Supabase, and updates the environment.
2. **Revoke Old Keys:** Roll the Supabase API keys in the dashboard.
3. **Audit:** Review `logs/app.log` for unauthorized data export calls (`services/data_governance.py`).
4. **Notify:** Notify affected tenants within 24 hours per SOC 2 / GDPR requirements.
