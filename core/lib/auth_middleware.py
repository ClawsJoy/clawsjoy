"""API 认证中间件"""

import logging
import os
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import g, jsonify, request

logger = logging.getLogger(__name__)


class AuthManager:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET", "change-me-in-production")
        self.algorithm = "HS256"
        self.token_expire_hours = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

    def generate_jwt(self, user_id: str) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expire_hours),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_jwt(self, token: str):
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            logger.warning("Token 已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效 Token: {e}")
            return None


_auth_manager = AuthManager()


def get_auth_manager():
    return _auth_manager


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = _auth_manager.verify_jwt(token)
            if payload:
                g.user_id = payload.get("user_id")
                return f(*args, **kwargs)
        return (
            jsonify({"error": "Unauthorized", "message": "请提供有效的认证凭证"}),
            401,
        )

    return decorated
