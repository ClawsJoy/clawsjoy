#!/usr/bin/env python3
"""Stateful Skill 基类 - 集成状态管理"""

import time
import json
import requests
from typing import Dict, Any, Optional
from state_manager import SkillStateManager

class StatefulSkill:
    """带状态管理的 Skill 基类"""
    
    def __init__(self, skill_name: str, tenant_id: str = "1", session_id: str = None):
        self.skill_name = skill_name
        self.tenant_id = tenant_id
        self.session_id = session_id or f"session_{int(time.time())}"
        self.state_manager = SkillStateManager()
        self.max_retries = 3
        self.timeout = 30
        self.backoff_factor = 2
    
    def get_state(self) -> Dict:
        """获取当前状态"""
        return self.state_manager.load_state(self.skill_name, self.session_id, self.tenant_id) or {}
    
    def save_state(self, state: Dict) -> bool:
        """保存状态"""
        return self.state_manager.save_state(self.skill_name, self.session_id, state, self.tenant_id)
    
    def update_state(self, updates: Dict) -> bool:
        """更新状态"""
        return self.state_manager.update_state(self.skill_name, self.session_id, updates, self.tenant_id)
    
    def clear_state(self) -> bool:
        """清除状态"""
        return self.state_manager.delete_state(self.skill_name, self.session_id, self.tenant_id)
    
    def _call_api(self, method: str, url: str, **kwargs) -> Dict:
        """带重试的 API 调用"""
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
    
    def execute(self, params: Dict) -> Dict:
        """执行 Skill（子类必须实现）"""
        raise NotImplementedError

if __name__ == "__main__":
    print("✅ Stateful Skill 基类已加载")
