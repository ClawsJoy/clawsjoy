from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""智能驱动核心 - 统一管理所有驱动"""

import os
import subprocess
import requests
from pathlib import Path
from core.lib.unified_config import unified_config

class IntelligentDriver:
    """智能驱动核心"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_service_url(self, service):
        """获取服务 URL"""
        port = unified_config.get_port(service)
        return fos.environ.get("OLLAMA_HOST", os.environ.get("OLLAMA_HOST", "http://127.0.0.1")"):{port}"
    
    def check_service(self, service):
        """检查服务健康"""
        url = self.get_service_url(service)
        # 根据不同服务使用不同健康检查路径
        health_paths = {
            'gateway': '/api/health',
            'multi_agent': '/health',
            'comfyui': '/',
            'file_service': '/health',
            'doc_generator': '/health'
        }
        path = health_paths.get(service, '/health')
        try:
            resp = requests.get(f"{url}{path}", timeout=3)
            return resp.status_code == 200
        except:
            return False
    
    def restart_service(self, service):
        """重启服务"""
        if service == 'gateway':
            subprocess.run(['pkill', '-f', 'agent_gateway_web'])
            subprocess.Popen(
                ['python3', 'agent_gateway_web.py'],
                cwd=unified_config.ROOT
            )
            return True
        return False
    
    def get_system_status(self):
        """获取系统状态"""
        status = {}
        for service in ['gateway', 'multi_agent', 'comfyui', 'file_service', 'doc_generator']:
            status[service] = self.check_service(service)
        return status
    
    def get_all_services_status(self):
        """获取所有服务详细状态"""
        services = ['gateway', 'multi_agent', 'comfyui', 'file_service', 'doc_generator', 'agent_api']
        result = {}
        for svc in services:
            result[svc] = {
                'url': self.get_service_url(svc),
                'healthy': self.check_service(svc)
            }
        return result

intelligent_driver = IntelligentDriver()
