"""服务注册与发现 - 轻量级实现"""
import json
import requests
from pathlib import Path
from datetime import datetime

class ServiceRegistry:
    def __init__(self, registry_file="data/service_registry.json"):
        self.registry_file = Path(registry_file)
        self.services = self._load()
    
    def _load(self):
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save(self):
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(self.services, f, indent=2)
    
    def register(self, name, port, host="localhost", health_path="/api/health"):
        """注册服务"""
        self.services[name] = {
            "name": name,
            "host": host,
            "port": port,
            "health_path": health_path,
            "url": f"http://{host}:{port}",
            "registered_at": datetime.now().isoformat(),
            "status": "active"
        }
        self._save()
        print(f"✅ 服务已注册: {name} -> {self.services[name]['url']}")
        return True
    
    def unregister(self, name):
        if name in self.services:
            del self.services[name]
            self._save()
            print(f"❌ 服务已注销: {name}")
    
    def get(self, name):
        return self.services.get(name)
    
    def get_url(self, name):
        service = self.get(name)
        return service["url"] if service else None
    
    def list_all(self):
        return list(self.services.keys())
    
    def health_check(self, name):
        service = self.get(name)
        if not service:
            return False
        try:
            resp = requests.get(f"{service['url']}{service['health_path']}", timeout=3)
            return resp.status_code == 200
        except:
            return False

# 全局实例
service_registry = ServiceRegistry()
