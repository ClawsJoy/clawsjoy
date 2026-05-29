"""私人管家俱乐部 - 智能驱动配置"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from core.lib.unified_config import unified_config

class ButlerClub:
    """私人管家俱乐部"""
    
    def __init__(self):
        self.config = self._load_config()
        self.data_root = Path(self.config.get('data', {}).get('root', f'{config_helper.get_data_root()}/butler_club'))
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.stats_file = self.data_root / 'stats.json'
        self._load_stats()
    
    def _load_config(self) -> Dict:
        config_path = Path('config/butler_club.yaml')
        if config_path.exists():
            with open(config_path) as f:
                return unified_config.get('butler_club', {})
        return {}
    
    def _load_stats(self):
        if self.stats_file.exists():
            with open(self.stats_file) as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                "total_members": 0,
                "total_butlers": 0,
                "total_interactions": 0,
                "level_distribution": {"bronze": 0, "silver": 0, "gold": 0, "diamond": 0},
                "most_popular_name": "小管",
                "updated_at": datetime.now().isoformat()
            }
            self._save_stats()
    
    def _save_stats(self):
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def get_stats(self) -> Dict:
        """获取俱乐部统计"""
        return self.stats
    
    def get_member(self, user_id: str) -> Optional[Dict]:
        """获取会员信息"""
        profile_file = self.data_root / f'members/{user_id}/profile.json'
        if profile_file.exists():
            with open(profile_file) as f:
                return json.load(f)
        return None
    
    def register_member(self, user_id: str, butler_name: str = "小管") -> Dict:
        """注册会员"""
        profile_dir = self.data_root / f'members/{user_id}'
        profile_dir.mkdir(parents=True, exist_ok=True)
        profile_file = profile_dir / 'profile.json'
        
        if profile_file.exists():
            return {"success": False, "message": "会员已存在"}
        
        profile = {
            "user_id": user_id,
            "joined_at": datetime.now().isoformat(),
            "membership_level": "bronze",
            "total_interactions": 0,
            "butler_name": butler_name,
            "rename_history": [],
            "achievements": []
        }
        
        with open(profile_file, 'w') as f:
            json.dump(profile, f, indent=2)
        
        self.stats["total_members"] += 1
        self.stats["total_butlers"] += 1
        self.stats["level_distribution"]["bronze"] += 1
        self._save_stats()
        
        return {"success": True, "user_id": user_id, "butler_name": butler_name}
    
    def record_interaction(self, user_id: str):
        """记录交互"""
        member = self.get_member(user_id)
        if member:
            member["total_interactions"] += 1
            self._check_level_upgrade(member)
            profile_file = self.data_root / f'members/{user_id}/profile.json'
            with open(profile_file, 'w') as f:
                json.dump(member, f, indent=2)
            self.stats["total_interactions"] += 1
            self._save_stats()
    
    def _check_level_upgrade(self, member: Dict):
        """检查等级升级"""
        interactions = member["total_interactions"]
        current = member["membership_level"]
        
        levels = self.config.get('membership_levels', [])
        for level in levels:
            if interactions >= level.get('min_interactions', 0):
                if level['name'] != current:
                    # 升级
                    old_level = current
                    member["membership_level"] = level['name']
                    member["achievements"].append({
                        "name": f"upgrade_to_{level['name']}",
                        "earned_at": datetime.now().isoformat()
                    })
                    # 更新统计
                    if old_level in self.stats["level_distribution"]:
                        self.stats["level_distribution"][old_level] -= 1
                    self.stats["level_distribution"][level['name']] += 1


# 全局实例
butler_club = ButlerClub()
