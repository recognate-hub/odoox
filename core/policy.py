import json
import os
from pathlib import Path
from typing import Dict, List
from core.logger import get_logger

logger = get_logger(__name__)

class PolicyEngine:
    """
    Policy-as-Code engine.
    Loads declarative RBAC policies and evaluates access requests.
    """
    _policies: Dict[str, List[str]] = {}
    _loaded: bool = False

    @classmethod
    def load_policies(cls, file_path: str = None):
        """Loads policies from a JSON file into memory."""
        if not file_path:
            # Default to config/rbac_policy.json
            base_dir = Path(__file__).parent.parent
            file_path = base_dir / "config" / "rbac_policy.json"
            
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                cls._policies = data.get("roles", {})
                cls._loaded = True
                logger.info("Successfully loaded RBAC policies", roles=list(cls._policies.keys()))
        except Exception as e:
            logger.error("Failed to load RBAC policies", error=str(e), path=str(file_path))
            raise RuntimeError(f"Could not load RBAC policies from {file_path}") from e

    @classmethod
    def is_allowed(cls, role: str, action: str) -> bool:
        """
        Evaluates whether a role is permitted to perform a given action.
        Supports wildcard '*' actions.
        """
        if not cls._loaded:
            cls.load_policies()
            
        # 1. Unknown roles have zero access.
        if role not in cls._policies:
            logger.warning("Policy evaluation failed: unknown role", role=role, action=action)
            return False
            
        allowed_actions = cls._policies[role]
        
        # 2. Check for wildcard admin access
        if "*" in allowed_actions:
            return True
            
        # 3. Check for exact action match
        if action in allowed_actions:
            return True
            
        logger.warning("Policy evaluation denied", role=role, action=action)
        return False
