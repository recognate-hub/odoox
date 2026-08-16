
from cryptography.fernet import Fernet

from core.logger import get_logger
from core.secrets import SecretsManager

logger = get_logger(__name__)

class KMSClient:
    """
    Mock KMS Client for Enterprise Envelope Encryption.
    In a real environment, this would call AWS KMS / GCP KMS.
    """
    
    @staticmethod
    def _get_kek() -> bytes:
        # Fallback to local ENCRYPTION_KEY if no external KMS is configured
        key = SecretsManager.get_active_key()
        try:
            import base64
            # Test if it's valid urlsafe base64 and decodes to exactly 32 bytes
            decoded = base64.urlsafe_b64decode(key.encode('utf-8'))
            if len(decoded) != 32:
                raise ValueError
            return key.encode('utf-8')
        except Exception:
            import base64
            import hashlib
            # Hash any invalid key into a perfect 32-byte base64 string
            key_hash = hashlib.sha256(key.encode('utf-8')).digest()
            return base64.urlsafe_b64encode(key_hash)

    @classmethod
    def generate_data_key(cls) -> tuple[bytes, str]:
        """
        Generates a new Data Encryption Key (DEK).
        Returns: (plaintext_dek, encrypted_dek)
        """
        plaintext_dek = Fernet.generate_key()
        
        # In AWS KMS, this would be kms.generate_data_key(KeyId='...')
        # For mock KMS, we encrypt the DEK with our KEK (Master Key)
        kek_cipher = Fernet(cls._get_kek())
        encrypted_dek = kek_cipher.encrypt(plaintext_dek).decode('utf-8')
        
        return plaintext_dek, encrypted_dek

    @classmethod
    def decrypt_data_key(cls, encrypted_dek: str) -> bytes:
        """
        Decrypts an encrypted DEK using the KMS KEK.
        """
        # In AWS KMS, this would be kms.decrypt(CiphertextBlob=...)
        kek_cipher = Fernet(cls._get_kek())
        return kek_cipher.decrypt(encrypted_dek.encode('utf-8'))
