from core.context import WorkspaceContext
from core.encryption import encrypt

try:
    workspace = WorkspaceContext(
        odoo_url="a", odoo_db="b", odoo_username="c", odoo_password="d", user_id="e"
    )
    payload = workspace.model_dump_json()
    print("Payload length:", len(payload))
    encrypted = encrypt(payload)
    print("Encrypted successfully. Length:", len(encrypted))
except Exception:
    import traceback

    traceback.print_exc()
