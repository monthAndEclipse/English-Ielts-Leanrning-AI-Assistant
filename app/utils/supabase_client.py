import os
from supabase import create_client
_supabase = None  # 单例实例缓存

def get_supabase():
    global _supabase
    if _supabase is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not supabase_url or not supabase_key:
            raise RuntimeError("请设置 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY 环境变量")
        _supabase = create_client(supabase_url, supabase_key)
    return _supabase
