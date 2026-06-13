"""主动服务模块 - 基于用户画像的主动建议"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict


class ProactiveService:
    """主动服务管理器"""
    
    def __init__(self, storage_dir: str = "data/proactive"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 用户画像
        self._user_profiles: Dict[str, Dict] = {}
        
        # 建议模板
        self._suggestion_templates = {
            "time_based": [
                {"hour": 6, "suggestion": "☀️ 早上好！需要我帮您规划今天的工作吗？"},
                {"hour": 12, "suggestion": "🍜 午饭时间到了，需要帮您推荐餐厅吗？"},
                {"hour": 18, "suggestion": "🌆 下班时间，需要帮您总结今天的工作吗？"},
                {"hour": 22, "suggestion": "🌙 晚安！需要设置明早的提醒吗？"},
            ],
            "activity_based": [
                {"pattern": "完成.*任务", "suggestion": "🎉 恭喜完成任务！需要我帮您规划下一个吗？"},
                {"pattern": "学习.*Python", "suggestion": "📚 学习Python是个好选择！需要推荐学习资源吗？"},
            ]
        }
        
        self._running = False
        self._thread = None
        
        print(f"💡 主动服务模块已初始化")
    
    def update_user_profile(self, user_id: str, interaction: Dict):
        """更新用户画像"""
        if user_id not in self._user_profiles:
            self._user_profiles[user_id] = {
                "name": "",
                "preferences": [],
                "habits": {"active_hours": [], "frequent_topics": []},
                "interaction_count": 0,
                "last_active": None,
                "created_at": datetime.now().isoformat()
            }
        
        profile = self._user_profiles[user_id]
        profile["interaction_count"] += 1
        profile["last_active"] = datetime.now().isoformat()
        
        # 更新偏好
        if "preference" in interaction:
            profile["preferences"].append(interaction["preference"])
        
        # 更新活跃时间
        hour = datetime.now().hour
        profile["habits"]["active_hours"].append(hour)
        profile["habits"]["active_hours"] = profile["habits"]["active_hours"][-50:]
        
        self._save_user_profile(user_id)
    
    def get_suggestions(self, user_id: str, context: Dict = None) -> List[str]:
        """获取主动建议"""
        suggestions = []
        profile = self._user_profiles.get(user_id, {})
        
        # 基于时间的建议
        current_hour = datetime.now().hour
        for template in self._suggestion_templates["time_based"]:
            if template["hour"] == current_hour:
                suggestions.append(template["suggestion"])
        
        # 基于用户偏好的建议
        if profile.get("preferences"):
            recent_prefs = profile["preferences"][-3:]
            if recent_prefs:
                suggestions.append(f"💡 根据您的偏好，推荐关注：{', '.join(recent_prefs)}")
        
        # 基于活跃度的建议
        if profile.get("interaction_count", 0) > 100:
            suggestions.append("🏆 您是活跃用户！需要什么帮助吗？")
        
        return suggestions[:3]
    
    def start(self):
        """启动主动服务后台线程"""
        if self._running:
            return
        
        self._running = True
        
        def _loop():
            print("💡 主动服务后台线程已启动")
            while self._running:
                time.sleep(300)  # 每5分钟检查一次
                # 这里可以添加主动推送逻辑
        
        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """停止主动服务"""
        self._running = False
    
    def _save_user_profile(self, user_id: str):
        """保存用户画像"""
        profile_file = self.storage_dir / f"{user_id}.json"
        with open(profile_file, 'w') as f:
            json.dump(self._user_profiles[user_id], f, indent=2, ensure_ascii=False)
    
    def _load_user_profile(self, user_id: str):
        """加载用户画像"""
        profile_file = self.storage_dir / f"{user_id}.json"
        if profile_file.exists():
            try:
                with open(profile_file, 'r') as f:
                    self._user_profiles[user_id] = json.load(f)
            except:
                pass


# 全局实例
proactive_service = ProactiveService()
proactive_service.start()
