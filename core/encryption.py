from cryptography.fernet import Fernet
from config.settings import get_settings

def get_cipher() -> Fernet:
    """Initialize the Fernet cipher using the Master Encryption Key."""
    settings = get_settings()
    if not settings.ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY must be set in the environment.")
    return Fernet(settings.ENCRYPTION_KEY)

def encrypt(secret: str) -> str:
    """Encrypt a string and return the ciphertext as a string."""
    if not secret:
        return secret
    cipher = get_cipher()
    return cipher.encrypt(secret.encode('utf-8')).decode('utf-8')

def decrypt(token: str) -> str:
    """Decrypt a ciphertext token and return the original string."""
    if not token:
        return token
    # If it doesn't look like a Fernet token, skip decryption (for backwards compatibility)
    if not token.startswith('gAAAAAB'):
        return token
    
    cipher = get_cipher()
    try:
        return cipher.decrypt(token.encode('utf-8')).decode('utf-8')
    except Exception:
        # Fallback if decryption fails (e.g. wrong key, corrupted data)
        return token
