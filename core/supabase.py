from supabase import Client, create_client

from config.settings import get_settings

_supabase_client = None

def get_supabase(token: str = None) -> Client:
    """
    Returns a Supabase client.
    If a token is provided, returns a client authenticated as that user (for RLS).
    Otherwise, returns the global anonymous/service client.
    """
    settings = get_settings()
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")
        
    if token:
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        client.postgrest.auth(token)
        return client
        
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _supabase_client
