from lib.smart_config import smart_config
"""技能版本管理"""
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

class SkillVersionManager:
    """技能版本管理器 - 支持版本控制和热加载"""
    
    def __init__(self, versions_file="data/skill_versions.json"):
        self.versions_file = Path(versions_file)
        self.versions = self._load()
        self.watchers = {}
    
    def _load(self) -> Dict:
        if self.versions_file.exists():
            with open(self.versions_file, 'r') as f:
                return json.load(f)
        return {"skills": {}, "last_update": None}
    
    def _save(self):
        self.versions_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.versions_file, 'w') as f:
            json.dump(self.versions, f, indent=2)
    
    def _compute_hash(self, file_path: Path) -> str:
        """计算文件哈希"""
        if file_path.exists():
            return hashlib.md5(file_path.read_bytes()).hexdigest()[:8]
        return ""
    
    def register_skill(self, name: str, version: str, file_path: str, category: str):
        """注册技能版本"""
        self.versions["skills"][name] = {
            "name": name,
            "version": version,
            "file": file_path,
            "category": category,
            "hash": self._compute_hash(Path(file_path)),
            "registered_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat()
        }
        self.versions["last_update"] = datetime.now().isoformat()
        self._save()
        print(f"📦 注册技能: {name} v{version}")
    
    def check_changes(self) -> list:
        """检查文件变化"""
        changed = []
        for name, info in self.versions["skills"].items():
            current_hash = self._compute_hash(Path(info["file"]))
            if current_hash != info["hash"]:
                changed.append({
                    "name": name,
                    "old_hash": info["hash"],
                    "new_hash": current_hash,
                    "file": info["file"]
                })
                info["hash"] = current_hash
                info["last_modified"] = datetime.now().isoformat()
        if changed:
            self._save()
        return changed
    
    def get_version(self, name: str) -> Optional[Dict]:
        return self.versions["skills"].get(name)
    
    def list_all(self) -> Dict:
        return self.versions["skills"]

skill_version = SkillVersionManager()
