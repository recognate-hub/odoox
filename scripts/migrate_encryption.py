import argparse
import os
import sys

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptography.fernet import InvalidToken

from core.encryption import _get_active_fernet, encrypt
from core.supabase import get_supabase


def migrate_credentials(token: str):
    print("Starting Envelope Encryption Migration...")
    
    supabase = get_supabase(token)
    
    # Fetch all workspaces (requires admin token/service role key for a real migration script)
    # Since this is a user-specific token for now, it will only migrate their own data
    response = supabase.table("user_workspaces").select("*").execute()
    
    if not response.data:
        print("No workspaces found.")
        return
        
    migrated_count = 0
    skipped_count = 0
    
    legacy_cipher = _get_active_fernet()
    
    for row in response.data:
        password = row.get("odoo_password", "")
        
        if password.startswith("ENVELOPE_V1:"):
            print(f"Skipping {row['id']} - already migrated.")
            skipped_count += 1
            continue
            
        try:
            # Decrypt old password
            plaintext_bytes = legacy_cipher.decrypt(password.encode('utf-8'))
            plaintext = plaintext_bytes.decode('utf-8')
            
            # Re-encrypt with envelope
            new_ciphertext = encrypt(plaintext)
            
            # Update database
            supabase.table("user_workspaces").update({
                "odoo_password": new_ciphertext
            }).eq("id", row["id"]).execute()
            
            migrated_count += 1
            print(f"Migrated {row['id']}")
            
        except InvalidToken:
            print(f"Failed to decrypt {row['id']} - Invalid Token")
            skipped_count += 1
        except Exception as e:
            print(f"Error migrating {row['id']}: {e}")
            skipped_count += 1
            
    print(f"\nMigration complete. Migrated: {migrated_count}, Skipped: {skipped_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate old Fernet passwords to KMS Envelope Encryption")
    parser.add_argument("--token", required=True, help="Supabase JWT or Service Role Key")
    args = parser.parse_args()
    
    migrate_credentials(args.token)
