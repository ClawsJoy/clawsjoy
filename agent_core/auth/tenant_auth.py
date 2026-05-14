"""多租户权限隔离系统"""

import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum

class Role(Enum):
    ADMIN = "admin"
    TENANT_ADMIN = "tenant_admin"
    USER = "user"
    GUEST = "guest"

class Permission(Enum):
    # 系统级权限
    MANAGE_TENANTS = "manage_tenants"
    VIEW_ALL_DATA = "view_all_data"
    SYSTEM_CONFIG = "system_config"
    
    # 租户级权限
    MANAGE_TENANT_USERS = "manage_tenant_users"
    VIEW_TENANT_DATA = "view_tenant_data"
    MANAGE_TENANT_SKILLS = "manage_tenant_skills"
    
    # 用户级权限
    VIEW_OWN_DATA = "view_own_data"
    MANAGE_OWN_SKILLS = "manage_own_skills"
    USE_SKILLS = "use_skills"

class TenantAuth:
    """租户认证与权限管理"""
    
    def __init__(self, data_dir: str = "data/tenants"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._init_default_tenant()
    
    def _init_default_tenant(self):
        """初始化默认租户和管理员"""
        # 系统租户
        system_tenant = self.data_dir / "system"
        system_tenant.mkdir(exist_ok=True)
        
        # 默认管理员
        admin_file = system_tenant / "admin.json"
        if not admin_file.exists():
            admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
            with open(admin_file, 'w') as f:
                json.dump({
                    'username': 'admin',
                    'password_hash': admin_hash,
                    'role': Role.ADMIN.value,
                    'created_at': datetime.now().isoformat()
                }, f)
        
        # 默认普通租户
        demo_tenant = self.data_dir / "demo"
        demo_tenant.mkdir(exist_ok=True)
        (demo_tenant / "secrets").mkdir(exist_ok=True)
        (demo_tenant / "users").mkdir(exist_ok=True)
        (demo_tenant / "data").mkdir(exist_ok=True)
        (demo_tenant / "skills").mkdir(exist_ok=True)
    
    def create_tenant(self, tenant_id: str, admin_username: str, admin_password: str) -> Dict:
        """创建新租户"""
        tenant_dir = self.data_dir / tenant_id
        if tenant_dir.exists():
            return {'error': 'Tenant already exists'}
        
        tenant_dir.mkdir(parents=True)
        
        # 创建租户目录结构
        (tenant_dir / "secrets").mkdir()
        (tenant_dir / "users").mkdir()
        (tenant_dir / "data").mkdir()
        (tenant_dir / "skills").mkdir()
        (tenant_dir / "purchases").mkdir()
        
        # 创建租户管理员
        password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
        with open(tenant_dir / "admin.json", 'w') as f:
            json.dump({
                'username': admin_username,
                'password_hash': password_hash,
                'role': Role.TENANT_ADMIN.value,
                'created_at': datetime.now().isoformat()
            }, f)
        
        # 创建租户配置
        with open(tenant_dir / "config.json", 'w') as f:
            json.dump({
                'tenant_id': tenant_id,
                'created_at': datetime.now().isoformat(),
                'status': 'active',
                'max_users': 100,
                'max_storage': '1GB'
            }, f, indent=2)
        
        return {'success': True, 'tenant_id': tenant_id}
    
    def authenticate(self, tenant_id: str, username: str, password: str) -> Optional[Dict]:
        """认证用户"""
        tenant_dir = self.data_dir / tenant_id
        if not tenant_dir.exists():
            return None
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # 检查管理员
        admin_file = tenant_dir / "admin.json"
        if admin_file.exists():
            with open(admin_file, 'r') as f:
                admin = json.load(f)
                if admin['username'] == username and admin['password_hash'] == password_hash:
                    return {'user_id': username, 'role': admin['role'], 'tenant_id': tenant_id}
        
        # 检查普通用户
        users_dir = tenant_dir / "users"
        for user_file in users_dir.glob("*.json"):
            with open(user_file, 'r') as f:
                user = json.load(f)
                if user['username'] == username and user['password_hash'] == password_hash:
                    return {'user_id': username, 'role': user['role'], 'tenant_id': tenant_id}
        
        return None
    
    def create_user(self, tenant_id: str, username: str, password: str, role: str = "user") -> Dict:
        """在租户下创建用户"""
        tenant_dir = self.data_dir / tenant_id
        if not tenant_dir.exists():
            return {'error': 'Tenant not found'}
        
        users_dir = tenant_dir / "users"
        users_dir.mkdir(exist_ok=True)
        
        user_file = users_dir / f"{username}.json"
        if user_file.exists():
            return {'error': 'User already exists'}
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with open(user_file, 'w') as f:
            json.dump({
                'username': username,
                'password_hash': password_hash,
                'role': role,
                'created_at': datetime.now().isoformat(),
                'tenant_id': tenant_id
            }, f, indent=2)
        
        # 创建用户数据目录
        user_data_dir = tenant_dir / "data" / username
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        return {'success': True, 'user_id': username}
    
    def get_user_data_path(self, tenant_id: str, user_id: str) -> Path:
        """获取用户数据路径（隔离）"""
        return self.data_dir / tenant_id / "data" / user_id
    
    def get_tenant_secrets_path(self, tenant_id: str) -> Path:
        """获取租户密钥路径（隔离）"""
        return self.data_dir / tenant_id / "secrets"

tenant_auth = TenantAuth()
