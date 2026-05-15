"""智能配置管理器 - 动态配置管理"""
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

class ConfigManager:
    def __init__(self):
        self.config_file = Path("data/smart_config.json")
        self.load_config()
        
    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'settings': {
                    'auto_backup': True,
                    'backup_interval_hours': 24,
                    'log_retention_days': 7,
                    'health_check_interval_seconds': 30,
                    'auto_heal': True,
                    'performance_alert_threshold': 80,
                    'learning_rate': 0.3,
                    'exploration_rate': 0.2
                },
                'history': []
            }
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key, default=None):
        """获取配置值"""
        return self.config['settings'].get(key, default)
    
    def set(self, key, value):
        """设置配置值"""
        old_value = self.config['settings'].get(key)
        self.config['settings'][key] = value
        
        # 记录变更
        self.config['history'].append({
            'timestamp': datetime.now().isoformat(),
            'key': key,
            'old': old_value,
            'new': value
        })
        
        self.save_config()
        print(f"⚙️ 配置更新: {key} = {value}")
    
    def auto_tune(self):
        """自动调优配置"""
        from agent_core.brain_enhanced import brain
        stats = brain.get_stats()
        success_rate = stats.get('success_rate', 0.5)
        
        changes = []
        
        # 根据成功率调整学习率
        if success_rate > 0.85:
            new_rate = min(0.5, self.get('learning_rate', 0.3) + 0.05)
            if new_rate != self.get('learning_rate'):
                self.set('learning_rate', new_rate)
                changes.append(f"学习率 -> {new_rate}")
        elif success_rate < 0.6:
            new_rate = max(0.1, self.get('learning_rate', 0.3) - 0.05)
            if new_rate != self.get('learning_rate'):
                self.set('learning_rate', new_rate)
                changes.append(f"学习率 -> {new_rate}")
        
        return changes

if __name__ == "__main__":
    manager = ConfigManager()
    print("📋 当前配置:")
    for k, v in manager.config['settings'].items():
        print(f"   {k}: {v}")
    
    changes = manager.auto_tune()
    if changes:
        print(f"\n🔄 自动调优: {changes}")
