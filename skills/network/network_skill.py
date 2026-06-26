"""网络检测"""
import requests

class network_skill:
    name = "network"
    description = "网络检测"
    version = "1.0.0"
    
    def execute(self, params):
        try:
            r = requests.get('https://baidu.com', timeout=5)
            return {"success": True, "online": True, "latency_ms": r.elapsed.total_seconds()*1000}
        except:
            return {"success": True, "online": False}
