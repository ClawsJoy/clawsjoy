"""私人管家俱乐部 - 智能驱动配置"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class ButlerClub:
    """私人管家俱乐部"""

    def __init__(self):
        self.config = self._load_config()
        # 数据目录
        self.data_root = Path("data/butler_club")
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.stats_file = self.data_root / 'stats.json'
        self._load_stats()
        print("✅ ButlerClub 初始化完成")

    def _load_config(self) -> Dict:
        """加载俱乐部配置"""
        config_path = Path('config/butler_club.yaml')
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
        return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "membership_levels": [
                {"name": "bronze", "min_interactions": 0, "color": "#CD7F32"},
                {"name": "silver", "min_interactions": 100, "color": "#C0C0C0"},
                {"name": "gold", "min_interactions": 500, "color": "#FFD700"},
                {"name": "diamond", "min_interactions": 2000, "color": "#B9F2FF"}
            ],
            "settings": {
                "default_butler_name": "小管",
                "max_rename_history": 10,
                "auto_upgrade": True
            }
        }

    def _load_stats(self):
        """加载统计数据"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            except Exception as e:
                print(f"加载统计失败: {e}")
                self._init_stats()
        else:
            self._init_stats()

    def _init_stats(self):
        """初始化统计数据"""
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
        """保存统计数据"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存统计失败: {e}")

    def get_stats(self) -> Dict:
        """获取俱乐部统计"""
        return self.stats

    def get_member(self, user_id: str) -> Optional[Dict]:
        """获取会员信息"""
        profile_file = self.data_root / f'members/{user_id}/profile.json'
        if profile_file.exists():
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def register_member(self, user_id: str, butler_name: str = None) -> Dict:
        """注册会员"""
        if butler_name is None:
            butler_name = self.config.get("settings", {}).get("default_butler_name", "小管")
        
        # 检查是否已存在
        if self.get_member(user_id):
            return {"success": False, "message": "会员已存在"}
        
        profile_dir = self.data_root / f'members/{user_id}'
        profile_dir.mkdir(parents=True, exist_ok=True)
        profile_file = profile_dir / 'profile.json'

        profile = {
            "user_id": user_id,
            "joined_at": datetime.now().isoformat(),
            "membership_level": "bronze",
            "total_interactions": 0,
            "butler_name": butler_name,
            "rename_history": [],
            "achievements": []
        }

        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

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
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(member, f, indent=2, ensure_ascii=False)
            self.stats["total_interactions"] += 1
            self._save_stats()

    def _check_level_upgrade(self, member: Dict):
        """检查等级升级"""
        interactions = member["total_interactions"]
        current = member["membership_level"]

        levels = self.config.get("membership_levels", [
            {"name": "bronze", "min_interactions": 0},
            {"name": "silver", "min_interactions": 100},
            {"name": "gold", "min_interactions": 500},
            {"name": "diamond", "min_interactions": 2000}
        ])
        
        # 找到适合的等级（从高到低）
        new_level = current
        for level in reversed(levels):
            if interactions >= level.get("min_interactions", 0):
                new_level = level["name"]
                break
        
        if new_level != current:
            # 升级
            old_level = current
            member["membership_level"] = new_level
            member["achievements"].append({
                "name": f"upgrade_to_{new_level}",
                "earned_at": datetime.now().isoformat()
            })
            # 更新统计
            if old_level in self.stats["level_distribution"]:
                self.stats["level_distribution"][old_level] -= 1
            if new_level in self.stats["level_distribution"]:
                self.stats["level_distribution"][new_level] += 1
            print(f"🎉 会员 {member['user_id']} 升级到 {new_level}！")


# 全局实例
butler_club = ButlerClub()
