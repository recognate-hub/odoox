import json
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from supabase import Client, create_client

# Load environment variables
load_dotenv()

# We need a service_role key to bypass RLS for backup/restore
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in environment.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE_NAME = "user_workspaces"


def run_drill():
    print("INITIATING AUTOMATED DISASTER RECOVERY DRILL")
    print(f"Target Table: {TABLE_NAME}")
    print("-" * 50)

    # STEP 1: BACKUP
    print("STEP 1: Taking snapshot backup...")
    try:
        response = supabase.table(TABLE_NAME).select("*").execute()
        original_data = response.data
        record_count = len(original_data)

        file_name = f"dr_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

        # Write to temporary local file
        with open(file_name, "w") as f:
            json.dump(original_data, f, indent=2)

        # Upload to Supabase Storage (Cloud)
        try:
            # Ensure bucket exists or ignore if it does
            try:
                supabase.storage.create_bucket("backups")
            except Exception:
                pass  # Bucket might already exist

            with open(file_name, "rb") as f:
                supabase.storage.from_("backups").upload(file_name, f.read())
            print(
                f"Backup successfully uploaded to Supabase Storage bucket 'backups': {file_name}"
            )
        except Exception as upload_err:
            if "Bucket not found" in str(upload_err):
                print("ERROR: Supabase Storage bucket 'backups' not found.")
                print(
                    "Please create a bucket named 'backups' in your Supabase dashboard."
                )
                print("The drill cannot proceed without a valid cloud storage bucket.")
                return
            else:
                raise
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    except Exception as e:
        print(f"Backup failed: {e}")
        return

    if record_count == 0:
        print(
            "Warning: Table is empty. The drill will proceed, but there is no data to wipe/restore."
        )

    # STEP 2: SIMULATE DISASTER (WIPE)
    print("\nSTEP 2: Simulating catastrophic database failure (WIPING TABLE)...")
    try:
        if record_count > 0:
            for record in original_data:
                supabase.table(TABLE_NAME).delete().eq(
                    "user_id", record["user_id"]
                ).execute()

        # Verify wipe
        verify_response = supabase.table(TABLE_NAME).select("*").execute()
        if len(verify_response.data) > 0:
            print("Wipe failed: Records still exist in the database.")
            return

        print("Wipe successful! Table is completely empty.")
    except Exception as e:
        print(f"Wipe failed: {e}")
        return

    # STEP 3: RESTORE
    print("\nSTEP 3: Restoring data from cloud backup snapshot...")
    try:
        if record_count > 0:
            # Download backup from Supabase Storage (Cloud)
            downloaded_bytes = supabase.storage.from_("backups").download(file_name)
            restored_data = json.loads(downloaded_bytes)

            (
                supabase.table(TABLE_NAME).insert(restored_data).execute()
            )

        print("Restore operation completed.")
    except Exception as e:
        print(f"Restore failed: {e}")
        return

    # STEP 4: VERIFICATION
    print("\nSTEP 4: Verifying data integrity post-restore...")
    try:
        final_response = supabase.table(TABLE_NAME).select("*").execute()
        final_count = len(final_response.data)

        if final_count == record_count:
            print(
                f"VERIFICATION PASSED: Original count ({record_count}) matches restored count ({final_count})."
            )
            print("DR DRILL COMPLETED SUCCESSFULLY.")
        else:
            print(
                f"VERIFICATION FAILED: Expected {record_count} records, but found {final_count}."
            )
    except Exception as e:
        print(f"Verification failed: {e}")


if __name__ == "__main__":
    run_drill()
