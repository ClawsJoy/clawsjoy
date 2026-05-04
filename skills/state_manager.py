#!/usr/bin/env python3
"""Skills 状态管理模块 - Redis 存储"""

import json
import redis
from datetime import datetime
from typing import Dict, Any, Optional

class SkillStateManager:
    """Skills 状态管理器"""
    
    def __init__(self, redis_host='localhost', redis_port=6379, db=0):
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=db, decode_responses=True)
        self.ttl = 3600 * 24  # 默认 24 小时过期
    
    def _get_key(self, skill_name: str, session_id: str, tenant_id: str = "1") -> str:
        """生成 Redis Key"""
        return f"skill:state:{tenant_id}:{skill_name}:{session_id}"
    
    def save_state(self, skill_name: str, session_id: str, state: Dict, tenant_id: str = "1") -> bool:
        """保存状态"""
        key = self._get_key(skill_name, session_id, tenant_id)
        data = {
            "state": json.dumps(state),
            "skill": skill_name,
            "session_id": session_id,
            "tenant_id": tenant_id,
            "updated_at": datetime.now().isoformat()
        }
        return self.redis.hset(key, mapping=data) and self.redis.expire(key, self.ttl)
    
    def load_state(self, skill_name: str, session_id: str, tenant_id: str = "1") -> Optional[Dict]:
        """加载状态"""
        key = self._get_key(skill_name, session_id, tenant_id)
        data = self.redis.hgetall(key)
        if not data:
            return None
        return json.loads(data.get("state", "{}"))
    
    def update_state(self, skill_name: str, session_id: str, updates: Dict, tenant_id: str = "1") -> bool:
        """更新状态（合并）"""
        current = self.load_state(skill_name, session_id, tenant_id) or {}
        current.update(updates)
        return self.save_state(skill_name, session_id, current, tenant_id)
    
    def delete_state(self, skill_name: str, session_id: str, tenant_id: str = "1") -> bool:
        """删除状态"""
        key = self._get_key(skill_name, session_id, tenant_id)
        return bool(self.redis.delete(key))
    
    def get_all_skills_state(self, tenant_id: str = "1") -> Dict:
        """获取租户下所有 Skills 状态"""
        pattern = f"skill:state:{tenant_id}:*:*"
        keys = self.redis.keys(pattern)
        result = {}
        for key in keys:
            data = self.redis.hgetall(key)
            if data:
                result[key] = {
                    "skill": data.get("skill"),
                    "session_id": data.get("session_id"),
                    "updated_at": data.get("updated_at")
                }
        return result

if __name__ == "__main__":
    # 测试
    sm = SkillStateManager()
    print("✅ 状态管理模块已加载")
    print(f"Redis 连接: {sm.redis.ping()}")
