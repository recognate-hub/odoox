import fileinput
import os
from typing import Any

from core.logger import get_logger
from core.supabase import get_supabase

logger = get_logger(__name__)

class DataGovernanceService:
    """
    Handles SOC 2 and GDPR/CCPA Compliance workflows for data export 
    (Right to Access) and deletion (Right to be Forgotten).
    """

    def __init__(self, token: str):
        self.token = token
        self.supabase = get_supabase(token)

    def export_tenant_data(self, user_id: str) -> dict[str, Any]:
        """
        Exports all middleware data associated with a tenant.
        Odoo data is NOT exported here, as Odoo is the authoritative CRM system of record.
        """
        logger.info("Exporting tenant data", target_user_id=user_id)
        
        # 1. Fetch user workspaces
        workspace_response = self.supabase.table("user_workspaces").select("*").eq("user_id", user_id).execute()
        
        return {
            "tenant_id": user_id,
            "export_timestamp": __import__('datetime').datetime.now().isoformat(),
            "middleware_data": {
                "workspaces": workspace_response.data
            }
        }

    def _scrub_log_file(self, file_path: str, user_id: str) -> int:
        """
        Physically scrubs the user_id from the log file by replacing it with [REDACTED_USER].
        Returns the number of lines modified.
        """
        if not os.path.exists(file_path):
            return 0
            
        modified_count = 0
        try:
            with fileinput.FileInput(file_path, inplace=True, backup='.bak') as file:
                for line in file:
                    if user_id in line:
                        modified_count += 1
                        print(line.replace(user_id, "[REDACTED_USER]"), end='')
                    else:
                        print(line, end='')
            return modified_count
        except Exception as e:
            logger.error("Failed to scrub log file", error=str(e), file_path=file_path)
            raise

    def _verify_log_scrubbing(self, file_path: str, user_id: str) -> bool:
        """
        Verifies that the user_id no longer exists in the log file.
        """
        if not os.path.exists(file_path):
            return True
            
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if user_id in line:
                    return False
        return True

    def delete_tenant_data(self, user_id: str) -> dict[str, Any]:
        """
        Completely deletes a tenant from the middleware.
        1. Deletes all user_workspaces records.
        2. Scrubs the tenant's user_id from physical log files.
        (Note: Does not delete the Auth user if using row-level RLS, but in a real app, 
        we would call supabase.auth.admin.delete_user(user_id) using a service role key).
        """
        logger.info("Initiating tenant deletion workflow", target_user_id=user_id)
        
        # 1. Delete from database
        self.supabase.table("user_workspaces").delete().eq("user_id", user_id).execute()
        
        # 2. Scrub logs (Right to be Forgotten in audit logs)
        log_path = "logs/app.log"
        scrubbed_lines = self._scrub_log_file(log_path, user_id)
        
        # 3. Verify logs are clean
        verification_passed = self._verify_log_scrubbing(log_path, user_id)
        
        if not verification_passed:
            logger.error("Log scrubbing verification failed!", target_user_id=user_id)
            raise RuntimeError("Data deletion verification failed. user_id still found in logs.")
            
        logger.info("Tenant deletion workflow completed", target_user_id=user_id, scrubbed_lines=scrubbed_lines)
        
        return {
            "status": "success",
            "deleted_user_id": user_id,
            "log_lines_scrubbed": scrubbed_lines,
            "verification_passed": verification_passed
        }
