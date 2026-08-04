# ODOOX Disaster Recovery & Resilience Plan

## Recovery Objectives

### RPO (Recovery Point Objective): 1 Hour
- **Definition:** The maximum acceptable amount of data loss measured in time.
- **Implementation:** Supabase Point-in-Time Recovery (PITR) is enabled for the `user_workspaces` table and auth schema, ensuring backups are streamed continuously. The maximum data loss window is 1 hour.

### RTO (Recovery Time Objective): 4 Hours
- **Definition:** The maximum acceptable time to restore the middleware service after a catastrophic failure.
- **Implementation:** Automated Infrastructure-as-Code (Terraform/Pulumi) allows redeployment of the Python FastAPI application in < 15 minutes. Database restoration via Supabase PITR can take up to 2 hours depending on dataset size, comfortably meeting the 4-hour target.

## Multi-Region Failover Strategy

To ensure high availability against regional cloud outages, ODOOX utilizes an Active-Passive failover architecture:

1. **Primary Region:** AWS `us-east-1` (Application & Supabase Primary).
2. **Standby Region:** AWS `us-west-2` (Application Standby & Supabase Read Replica).
3. **Failover Execution:**
   - In the event of a total regional failure in `us-east-1`, Cloudflare DNS automatically routes traffic to the `us-west-2` standby cluster.
   - The Supabase Read Replica in `us-west-2` is manually promoted to Primary via the Supabase dashboard (or automated via API trigger).
   - Application configuration (`settings.py`) dynamically switches connection strings based on region availability.

## Automated DR Drills
As part of our SOC 2 compliance, we execute automated backup, wipe, and restore drills against staging/production tables using the `scripts/dr_drill.py` playbook.

*This document is reviewed and updated annually by the platform engineering team.*
