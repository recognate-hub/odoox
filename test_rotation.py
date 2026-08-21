import os

from cryptography.fernet import Fernet

from core.encryption import decrypt


def test_rotation():
    # 1. Encrypt with old key
    old_key = Fernet.generate_key().decode()
    cipher = Fernet(old_key)
    ciphertext = cipher.encrypt(b"secret_password").decode()

    # 2. Setup environment for rotation
    os.environ["OLD_ENCRYPTION_KEYS"] = old_key

    # 3. Decrypt
    decrypted = decrypt(ciphertext)
    assert decrypted == "secret_password"
    print("Rotation test passed!")


if __name__ == "__main__":
    test_rotation()
