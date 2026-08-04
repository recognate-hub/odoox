# Break-Glass Incident Response: Encryption Key Compromise

If the primary ODOOX `ENCRYPTION_KEY` is leaked, exposed, or compromised in any way, immediately execute this runbook to revoke the key and safely re-encrypt the Supabase datastore.

## 1. Verify and Declare Incident
- Confirm the compromise.
- Escalate to the incident response team and temporarily pause ODOOX ingress traffic (disable the FastMCP bridge endpoint) to prevent new writes during the rotation window.

## 2. Generate New Key Material
- Generate a new cryptographically secure 32-byte key:
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
- Store this new key securely in the Vault/KMS.

## 3. Configure Rotation State
- Log into the Secrets Manager (e.g. AWS KMS or HashiCorp Vault).
- Demote the compromised key to the `OLD_ENCRYPTION_KEYS` list.
- Promote the newly generated key to be the primary `ODOO_ENCRYPTION_KEY`.
- Wait for the SecretsManager cache to flush or actively restart the ODOOX worker processes so they fetch the new key configuration.

## 4. Run the Re-Encryption Script
- Execute the bulk re-encryption script against the Supabase datastore. 
- The script will iterate through all stored tenant contexts, decrypt the `odoo_password` using the old key (which is now in `OLD_ENCRYPTION_KEYS`), and immediately re-encrypt it using the new primary key.
- *Note: Do this swiftly to minimize the time the compromised key is loaded in memory.*

## 5. Revoke the Compromised Key
- Once the re-encryption script finishes successfully, log back into the Secrets Manager.
- **Delete/Revoke** the compromised key entirely from `OLD_ENCRYPTION_KEYS`.
- The compromised key is now useless, as all ciphertexts have been rolled to the new key.

## 6. Audit & Resume
- Review access logs in Supabase and the Odoo backend to ensure no malicious activity occurred using the compromised key.
- Restore ODOOX ingress traffic.
