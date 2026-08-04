from cryptography.fernet import Fernet, InvalidToken
from core.secrets import SecretsManager

def _get_active_fernet() -> Fernet:
    key = SecretsManager.get_active_key()
    if len(key) < 32:
        # Pad with '=' if someone provided a raw string instead of base64
        import base64
        key = base64.urlsafe_b64encode(key.encode('utf-8').ljust(32, b' '))
    return Fernet(key)

def _get_retired_fernets() -> list[Fernet]:
    fernets = []
    for key in SecretsManager.get_retired_keys():
        try:
            fernets.append(Fernet(key))
        except Exception:
            continue
    return fernets

def encrypt(secret: str) -> str:
    """Encrypt a string and return the ciphertext as a string."""
    if not secret:
        return secret
    cipher = _get_active_fernet()
    return cipher.encrypt(secret.encode('utf-8')).decode('utf-8')

def decrypt(token: str) -> str:
    """Decrypt a ciphertext token and return the original string."""
    if not token:
        return token
    # If it doesn't look like a Fernet token, skip decryption (for backwards compatibility)
    if not token.startswith('gAAAAAB'):
        return token
    
    keys = [_get_active_fernet()] + _get_retired_fernets()
        
    for cipher in keys:
        try:
            return cipher.decrypt(token.encode('utf-8')).decode('utf-8')
        except (InvalidToken, Exception):
            continue
            
    # Fallback if decryption fails (e.g. wrong key, corrupted data)
    return token
