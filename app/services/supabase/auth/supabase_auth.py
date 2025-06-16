import os
import uuid

import jwt
from typing import Dict, Any, Optional
from fastapi import Request
from pydantic import BaseModel
from app.utils.logger import get_logger
import time

logger = get_logger(__name__)

class SupabaseUser(BaseModel):
    """用户信息模型"""
    id: str
    email: str
    role: Optional[str] = None
    app_metadata: Optional[Dict[str, Any]] = None
    user_metadata: Optional[Dict[str, Any]] = None


_token_user_cache = {}  # token -> (user, timestamp)
_cache_ttl = 3600  # 缓存 1 小时

class SupabaseAuth:
    """Supabase认证工具类"""
    def __init__(self, supabase_client):
        self.supabase_jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        self.supabase_public_key = os.getenv("SUPABASE_PUBLIC_KEY")
        if not self.supabase_jwt_secret and not self.supabase_public_key:
            raise ValueError("缺少认证密钥：SUPABASE_JWT_SECRET 或 SUPABASE_PUBLIC_KEY 必须设置")
        self.jwt_signing_key = self.supabase_public_key or self.supabase_jwt_secret
        self.supabase_client = supabase_client

    def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(
                token,
                self.jwt_signing_key,
                algorithms=["HS256", "RS256"],
                audience="authenticated",
                options={"verify_signature": True}
            )
            logger.debug(f"令牌验证成功，用户ID: {payload.get('sub')}")
            return payload
        except Exception:
            logger.exception("令牌验证失败")
            return None

    def get_user_from_token(self, token: str) -> Optional[SupabaseUser]:
        """从令牌中获取用户信息"""
        if not token:
            logger.warning("未提供令牌")
            return None

        payload = self._verify_token(token)
        if not payload:
            logger.warning("无效令牌")
            return None

        user_id = payload.get("sub")
        if not user_id:
            logger.warning("令牌中缺少用户ID")
            return None

        try:
            logger.debug(f"正在从Supabase获取用户信息: {user_id}")
            response = self.supabase_client.auth.admin.get_user_by_id(user_id)
            user = response.model_dump().get('user')

            if not user:
                logger.warning(f"未找到用户: {user_id}")
                return None

            return SupabaseUser(
                id=user.get("id"),
                email=user.get("email"),
                role=user.get("role"),
                app_metadata=user.get("app_metadata"),
                user_metadata=user.get("user_metadata")
            )
        except Exception:
            logger.exception("获取用户信息失败")
            return None

    async def get_current_user_from_request(self, request: Request) -> Optional[SupabaseUser]:
        """从请求中提取当前用户"""
        logger.debug(f"请求路径: {request.url.path}")
        logger.debug(f"请求头字段: {list(request.headers.keys())}")
        try:
            auth_header = request.headers.get("authorization", "")
            if not auth_header:
                logger.warning("请求缺少Authorization头")
                return None
            logger.debug(f"Authorization头(前20字符): {auth_header[:20]}...")
            scheme, token = auth_header.split(None, 1)
            if scheme.lower() != "bearer":
                logger.warning(f"不支持的认证方案: {scheme}")
                return None
            if not token :
                logger.warning(f"传入的token为空")
                return None
            #添加缓存层
            now = time.time()
            cached = _token_user_cache.get(token)
            if cached:
                user, ts = cached
                if now - ts < _cache_ttl:
                    logger.debug(f"cache user hit")
                    return user
            user = self.get_user_from_token(token)
            if user:
                # ✅ 写入缓存
                _token_user_cache[token] = (user, now)
            return user
        except ValueError:
            logger.exception("Authorization头格式错误")
            return None
        except Exception:
            logger.exception("解析Authorization头时出错")
            return None

    async def get_user(self,request: Request) -> Optional[SupabaseUser]:
        """FastAPI依赖项，用于获取当前用户"""
        return await self.get_current_user_from_request(request)

def get_mock_user():
    return str("fixed_user_id")