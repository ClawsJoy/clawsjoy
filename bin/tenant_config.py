import os
import json
from pathlib import Path

def read_tenant_config(tenant_id):
    """读取指定租户的配置文件内容。"""
    config_path = Path(os.path.expanduser(f'~/clawsjoy/tenants/{tenant_id}/config.json'))
    
    if not config_path.exists():
        return {"evolution_enabled": True, "tenant_id": tenant_id}
    
    with open(config_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def update_tenant_config(tenant_id, new_config):
    """更新指定租户的配置文件。"""
    config_path = Path(os.path.expanduser(f'~/clawsjoy/tenants/{tenant_id}/config.json'))
    
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件 {config_path} 不存在。")
    
    with open(config_path, 'w', encoding='utf-8') as file:
        json.dump(new_config, file, indent=2)
    
    return new_config

if __name__ == "__main__":
    # 测试代码
    tenant_id = "test_tenant"
    print(f"读取租户 {tenant_id} 配置:")
    print(json.dumps(read_tenant_config(tenant_id), indent=2))
