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

from core.kms import KMSClient


def encrypt(secret: str) -> str:
    """Encrypt a string and return the ciphertext as a string using Envelope Encryption."""
    if not secret:
        return secret
        
    plaintext_dek, encrypted_dek = KMSClient.generate_data_key()
    cipher = Fernet(plaintext_dek)
    ciphertext = cipher.encrypt(secret.encode('utf-8')).decode('utf-8')
    
    # Store both the encrypted DEK and ciphertext
    return f"ENVELOPE_V1:{encrypted_dek}:{ciphertext}"

def decrypt(token: str) -> str:
    """Decrypt a ciphertext token and return the original string."""
    if not token:
        return token
        
    if token.startswith('ENVELOPE_V1:'):
        try:
            _, encrypted_dek, ciphertext = token.split(':', 2)
            plaintext_dek = KMSClient.decrypt_data_key(encrypted_dek)
            cipher = Fernet(plaintext_dek)
            return cipher.decrypt(ciphertext.encode('utf-8')).decode('utf-8')
        except Exception as e:
            from core.logger import get_logger
            get_logger(__name__).error(f"Envelope decryption failed: {e}")
            raise ValueError("Decryption failed due to invalid token or key.") from e
            
    # Backwards compatibility for old raw Fernet tokens
    if token.startswith('gAAAAAB'):
        keys = [_get_active_fernet()] + _get_retired_fernets()
        for cipher in keys:
            try:
                return cipher.decrypt(token.encode('utf-8')).decode('utf-8')
            except (InvalidToken, Exception):
                continue
                
    # Fallback if decryption fails
    raise ValueError("Decryption failed: Token is invalid or all active/retired keys failed.")
