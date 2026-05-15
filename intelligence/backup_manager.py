"""智能备份管理器 - 自动备份重要数据"""
import json
import shutil
import tarfile
from pathlib import Path
from datetime import datetime
from collections import deque
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

class BackupManager:
    def __init__(self):
        self.backup_dir = Path("/mnt/d/backups/clawsjoy")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.data_dirs = ['data', 'logs', 'skills', 'agents', 'intelligence']
        self.backup_history = deque(maxlen=10)
        
    def create_backup(self):
        """创建备份"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"clawsjoy_backup_{timestamp}.tar.gz"
        
        print(f"📦 创建备份: {backup_file.name}")
        
        with tarfile.open(backup_file, 'w:gz') as tar:
            for dir_name in self.data_dirs:
                dir_path = Path(dir_name)
                if dir_path.exists():
                    tar.add(dir_path, arcname=dir_name)
        
        # 记录备份历史
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        self.backup_history.append({
            'file': str(backup_file),
            'timestamp': timestamp,
            'size_mb': round(size_mb, 2)
        })
        
        # 保存备份历史
        history_file = self.backup_dir / "backup_history.json"
        with open(history_file, 'w') as f:
            json.dump(list(self.backup_history), f, indent=2)
        
        print(f"✅ 备份完成: {size_mb:.1f} MB")
        return str(backup_file)
    
    def list_backups(self):
        """列出所有备份"""
        backups = sorted(self.backup_dir.glob("clawsjoy_backup_*.tar.gz"))
        return [{'name': b.name, 'size': f"{b.stat().st_size / (1024*1024):.1f} MB", 
                 'modified': datetime.fromtimestamp(b.stat().st_mtime).isoformat()} 
                for b in backups]
    
    def clean_old_backups(self, keep=5):
        """清理旧备份"""
        backups = sorted(self.backup_dir.glob("clawsjoy_backup_*.tar.gz"))
        to_delete = backups[:-keep] if len(backups) > keep else []
        
        for backup in to_delete:
            backup.unlink()
            print(f"🗑️ 删除旧备份: {backup.name}")
        
        return len(to_delete)

if __name__ == "__main__":
    manager = BackupManager()
    manager.create_backup()
    print(f"\n📋 备份列表:")
    for b in manager.list_backups()[:3]:
        print(f"   {b['name']} ({b['size']})")
