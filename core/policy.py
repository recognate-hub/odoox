import json
from pathlib import Path

from core.logger import get_logger

logger = get_logger(__name__)


class PolicyEngine:
    """
    Policy-as-Code engine.
    Loads declarative RBAC policies and evaluates access requests.
    """

    _policies: dict[str, list[str]] = {}
    _allowed_models: dict[str, list[str]] = {}
    _loaded: bool = False

    @classmethod
    def load_policies(cls, file_path: str | None = None):
        """Loads policies from a JSON file into memory."""
        if not file_path:
            # Default to config/rbac_policy.json
            base_dir = Path(__file__).parent.parent
            file_path = base_dir / "config" / "rbac_policy.json"

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                cls._policies = data.get("roles", {})
                cls._allowed_models = data.get("allowed_models", {})
                cls._loaded = True
                logger.info(
                    "Successfully loaded RBAC policies",
                    roles=list(cls._policies.keys()),
                )
        except Exception as e:
            logger.error(
                "Failed to load RBAC policies", error=str(e), path=str(file_path)
            )
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
            logger.warning(
                "Policy evaluation failed: unknown role", role=role, action=action
            )
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

    @classmethod
    def is_model_allowed(cls, role: str, action: str, model: str) -> bool:
        """
        Evaluates whether a role is permitted to access a specific model
        using generic tools (e.g. search_read_records).
        """
        if not cls._loaded:
            cls.load_policies()

        if role not in cls._allowed_models:
            logger.warning(
                "Model policy evaluation failed: unknown role in allowed_models",
                role=role,
                model=model,
            )
            return False

        allowed_models_list = cls._allowed_models[role]

        if "*" in allowed_models_list:
            return True

        if model in allowed_models_list:
            return True

        logger.warning(
            "Model policy evaluation denied", role=role, action=action, model=model
        )
        return False
