import os
from typing import List
from config.settings import get_settings
from core.logger import get_logger

logger = get_logger(__name__)

class SecretsManager:
    """
    Abstracts encryption key retrieval. 
    In a true enterprise scenario, this class interfaces with AWS KMS, HashiCorp Vault, 
    or GCP Secret Manager to dynamically pull and rotate encryption keys.
    """

    @classmethod
    def get_active_key(cls) -> str:
        """
        Retrieves the primary active encryption key.
        """
        # Simulated KMS fetch
        settings = get_settings()
        key = settings.ENCRYPTION_KEY
        if not key:
            raise ValueError("No active encryption key found in Secrets Manager")
        return key

    @classmethod
    def get_retired_keys(cls) -> List[str]:
        """
        Retrieves previously active keys to allow decrypting legacy ciphertext 
        during a graceful rotation period.
        """
        # Simulated KMS fetch
        settings = get_settings()
        keys_str = settings.OLD_ENCRYPTION_KEYS
        return [k.strip() for k in keys_str.split(',') if k.strip()]
