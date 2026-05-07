#!/usr/bin/env python3
"""Skills 基类 - 增强错误处理"""

import time
import json
import requests
from typing import Dict, Any, Optional, Callable

class BaseSkill:
    """增强版 Skill 基类"""
    
    def __init__(self, tenant_id: str = "1", session_id: str = None):
        self.tenant_id = tenant_id
        self.session_id = session_id
        self.max_retries = 3
        self.timeout = 30
        self.backoff_factor = 2  # 重试间隔倍数
    
    def execute(self, params: Dict) -> Dict:
        """执行 Skill（子类实现）"""
        raise NotImplementedError
    
    def _call_api(self, method: str, url: str, **kwargs) -> Dict:
        """带重试和超时的 API 调用"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                kwargs['timeout'] = self.timeout
                
                if method.upper() == 'GET':
                    resp = requests.get(url, **kwargs)
                elif method.upper() == 'POST':
                    resp = requests.post(url, **kwargs)
                elif method.upper() == 'DELETE':
                    resp = requests.delete(url, **kwargs)
                else:
                    return {"error": f"Unsupported method: {method}"}
                
                if resp.status_code == 200:
                    return resp.json()
                else:
                    return {"error": f"HTTP {resp.status_code}: {resp.text[:100]}"}
                    
            except requests.exceptions.Timeout:
                last_error = f"Timeout after {self.timeout}s"
            except requests.exceptions.ConnectionError:
                last_error = "Connection error"
            except Exception as e:
                last_error = str(e)
            
            if attempt < self.max_retries - 1:
                wait = self.backoff_factor ** attempt
                time.sleep(wait)
        
        return {"error": f"Failed after {self.max_retries} retries: {last_error}"}
    
    def _fallback(self, params: Dict, error: str) -> Dict:
        """降级处理（子类可覆盖）"""
        return {
            "success": False,
            "error": error,
            "fallback": True,
            "message": "服务暂时不可用，请稍后重试"
        }
