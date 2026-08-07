import os
from dotenv import load_dotenv
load_dotenv('.env')

from supabase import create_client
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
try:
    res = supabase.table('user_workspaces').select('*').eq('id', '1').execute()
    print('SUCCESS:', len(res.data))
except Exception as e:
    print('ERROR:', e)
