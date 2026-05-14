"""数据保障层 - 事务 + 备份 + 校验"""

import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from threading import Lock

class DataGuard:
    def __init__(self):
        self.locks = {}
        self.backup_dir = Path("data/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_lock(self, file_path):
        if file_path not in self.locks:
            self.locks[file_path] = Lock()
        return self.locks[file_path]
    
    def atomic_write(self, file_path: Path, data: dict) -> bool:
        """原子写入 - 事务保证"""
        lock = self._get_lock(str(file_path))
        with lock:
            # 1. 备份原文件
            if file_path.exists():
                backup_file = self.backup_dir / f"{file_path.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                shutil.copy(file_path, backup_file)
            
            # 2. 写入临时文件
            temp_file = file_path.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # 3. 校验
            with open(temp_file, 'r') as f:
                try:
                    json.load(f)
                except:
                    temp_file.unlink()
                    return False
            
            # 4. 原子替换
            temp_file.replace(file_path)
            return True
    
    def get_md5(self, file_path: Path) -> str:
        if file_path.exists():
            return hashlib.md5(file_path.read_bytes()).hexdigest()
        return ""

data_guard = DataGuard()
