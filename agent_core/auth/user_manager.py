"""用户管理模块"""

import json
from pathlib import Path
from datetime import datetime
from .jwt_auth import hash_password, verify_password

class UserManager:
    def __init__(self):
        self.users_dir = Path("data/users")
        self.users_dir.mkdir(parents=True, exist_ok=True)
    
    def register(self, tenant_id: str, username: str, password: str, email: str = "") -> dict:
        user_file = self.users_dir / f"{tenant_id}_{username}.json"
        if user_file.exists():
            return {'success': False, 'error': 'User already exists'}
        
        user_data = {
            'username': username,
            'password_hash': hash_password(password),
            'email': email,
            'tenant_id': tenant_id,
            'role': 'user',
            'created_at': datetime.now().isoformat(),
            'balance': 0,
            'skills': []
        }
        
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        return {'success': True, 'username': username}
    
    def login(self, tenant_id: str, username: str, password: str) -> dict:
        user_file = self.users_dir / f"{tenant_id}_{username}.json"
        if not user_file.exists():
            return {'success': False, 'error': 'User not found'}
        
        with open(user_file, 'r') as f:
            user = json.load(f)
        
        if not verify_password(password, user['password_hash']):
            return {'success': False, 'error': 'Invalid password'}
        
        from .jwt_auth import generate_token
        token = generate_token(username, tenant_id, user['role'])
        
        return {
            'success': True,
            'token': token,
            'user': {
                'username': user['username'],
                'role': user['role'],
                'balance': user.get('balance', 0)
            }
        }
    
    def get_user(self, tenant_id: str, username: str) -> dict:
        user_file = self.users_dir / f"{tenant_id}_{username}.json"
        if not user_file.exists():
            return None
        with open(user_file, 'r') as f:
            return json.load(f)
    
    def add_balance(self, tenant_id: str, username: str, amount: float) -> dict:
        user = self.get_user(tenant_id, username)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        user['balance'] = user.get('balance', 0) + amount
        user_file = self.users_dir / f"{tenant_id}_{username}.json"
        with open(user_file, 'w') as f:
            json.dump(user, f, indent=2)
        
        return {'success': True, 'balance': user['balance']}

user_manager = UserManager()
