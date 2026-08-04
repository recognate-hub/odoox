# Service Level Objectives (SLOs) & Error Budgets

## Target Metrics

### 1. Availability SLO: 99.9%
- **Definition:** The percentage of MCP JSON-RPC requests that result in a successful response (or an expected client error, e.g., 400 Bad Request) out of total valid requests.
- **Measurement:** Prometheus metrics scraped from the FastAPI middleware, specifically `http_requests_total` grouped by status code.
- **Error Budget:** 43 minutes and 49 seconds of downtime permitted per month.

### 2. Latency SLO: 95th Percentile < 800ms
- **Definition:** 95% of all valid read/write requests to Odoo must complete in under 800 milliseconds roundtrip (from middleware ingress to egress).
- **Measurement:** Datadog APM tracing measuring the span duration of `OdooClient.call`.
- **Error Budget:** If the p95 latency exceeds 800ms for more than 5% of the trailing 30-day window, feature development is halted to prioritize performance tuning.

### 3. FinOps Integrity SLO: 99.99%
- **Definition:** The percentage of MCP operations that correctly decrement the tenant's API budget.
- **Measurement:** Reconciliation between the sum of `FinOpsService` counters and actual Supabase API logs.

## Error Budget Policies

When an Error Budget is exhausted:
1. **P0 Incident Triggered:** Engineering on-call is paged.
2. **Feature Freeze:** No new non-critical features may be deployed until the service operates within budget for 7 consecutive days.
3. **Blameless Post-Mortem:** A document is created detailing the root cause and remediation items.
