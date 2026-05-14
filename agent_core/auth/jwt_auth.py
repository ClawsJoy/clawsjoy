"""JWT 认证模块"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from pathlib import Path
import json

SECRET_KEY = "clawsjoy-secret-key-2026-change-in-production"
TOKEN_EXPIRE_HOURS = 24

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_token(user_id: str, tenant_id: str, role: str) -> str:
    payload = {
        'user_id': user_id,
        'tenant_id': tenant_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}

def refresh_token(token: str) -> str:
    payload = verify_token(token)
    if payload.get('error'):
        return None
    return generate_token(payload['user_id'], payload['tenant_id'], payload['role'])
