from core.supabase import get_supabase

try:
    supabase = get_supabase()
    resp = supabase.table("user_workspaces").select("*").limit(1).execute()
    print("SUCCESS: ", resp.data)
except Exception as e:
    print("ERROR: ", e)
