import json
from pathlib import Path
from datetime import datetime
from typing import Dict

class ButlerCenter:
    def __init__(self):
        self.center_path = Path(f"{config_helper.get_data_root()}/butler_center")
        self.center_path.mkdir(parents=True, exist_ok=True)
        self.instances_file = self.center_path / "instances.json"
        self.instances = json.load(open(self.instances_file)) if self.instances_file.exists() else {}
        
    def _save(self):
        with open(self.instances_file, 'w') as f:
            json.dump(self.instances, f, indent=2)
            
    def register_butler(self, user_id: str, butler_data: Dict):
        if user_id not in self.instances:
            self.instances[user_id] = []
        butler_info = {'id': user_id, 'name': butler_data.get('name', '小管'), 'created_at': datetime.now().isoformat(), 'status': 'active'}
        self.instances[user_id].append(butler_info)
        self._save()
        return butler_info
        
    def get_stats(self) -> Dict:
        return {'total_users': len(self.instances), 'total_butlers': sum(len(v) for v in self.instances.values())}

_center = None
def get_butler_center():
    global _center
    if _center is None:
        _center = ButlerCenter()
    return _center

# ========== 配置驱动路由 Handlers ==========
def get_stats():
    """获取统计信息 - 供路由调用"""
    center = get_butler_center()
    from flask import jsonify
    return jsonify(center.get_stats())

def list_all():
    """列出所有管家 - 供路由调用"""
    center = get_butler_center()
    from flask import jsonify
    return jsonify(center.instances)

def register():
    """注册管家 - 供路由调用"""
    from flask import request, jsonify
    data = request.json
    center = get_butler_center()
    result = center.register_butler(data.get('user_id'), data)
    return jsonify(result)

def get_stats():
    from flask import jsonify
    center = get_butler_center()
    return jsonify(center.get_stats())

def get_stats():
    from flask import jsonify
    center = get_butler_center()
    return jsonify(center.get_stats())
