#!/usr/bin/env python3
"""
安全磁盘清理 - 遵循规范，保留必要文件
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import json

class SafeCleaner:
    def __init__(self):
        self.project_root = Path("/mnt/d/clawsjoy")
        self.disk_threshold = 80  # 超过80%才清理
        self.dry_run = False  # True=预览不删除
    
    def get_disk_usage(self):
        """获取磁盘使用率"""
        result = subprocess.run(f"df -h {self.project_root} | tail -1 | awk '{{print $5}}'",
                                shell=True, capture_output=True, text=True)
        return int(result.stdout.strip().replace('%', ''))
    
    def safe_clean_logs(self):
        """安全清理日志 - 保留30天"""
        logs_dir = self.project_root / "logs"
        cutoff = datetime.now() - timedelta(days=30)
        
        cleaned = []
        for log_file in logs_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff.timestamp():
                # 压缩后删除（保留压缩包）
                if not self.dry_run:
                    subprocess.run(f"gzip {log_file}", shell=True)
                cleaned.append(log_file.name)
        
        # 清理超过90天的压缩包
        for gz_file in logs_dir.glob("*.gz"):
            if gz_file.stat().st_mtime < (datetime.now() - timedelta(days=90)).timestamp():
                if not self.dry_run:
                    gz_file.unlink()
                cleaned.append(f"{gz_file.name} (压缩包)")
        
        return cleaned
    
    def safe_clean_temp(self):
        """清理临时文件 - 保留24小时"""
        temp_patterns = ["*.tmp", "*.temp", "*.cache", "*.pyc"]
        cutoff = datetime.now() - timedelta(hours=24)
        
        cleaned = []
        for pattern in temp_patterns:
            for temp_file in self.project_root.rglob(pattern):
                if temp_file.stat().st_mtime < cutoff.timestamp():
                    if not self.dry_run:
                        temp_file.unlink()
                    cleaned.append(str(temp_file))
        
        # 清理 __pycache__
        for cache_dir in self.project_root.rglob("__pycache__"):
            if cache_dir.stat().st_mtime < cutoff.timestamp():
                if not self.dry_run:
                    subprocess.run(f"rm -rf {cache_dir}", shell=True)
                cleaned.append(str(cache_dir))
        
        return cleaned
    
    def safe_clean_backups(self):
        """清理旧备份 - 保留最近7天"""
        backup_dir = self.project_root / "backups"
        if not backup_dir.exists():
            return []
        
        cutoff = datetime.now() - timedelta(days=7)
        cleaned = []
        
        for backup in backup_dir.glob("*.sql.gz"):
            if backup.stat().st_mtime < cutoff.timestamp():
                if not self.dry_run:
                    backup.unlink()
                cleaned.append(backup.name)
        
        return cleaned
    
    def check_critical_files(self):
        """检查关键文件是否被误删"""
        critical = [
            self.project_root / ".env",
            self.project_root / "docker-compose.yml",
            self.project_root / "agents" / "engineer_agent.py",
        ]
        
        missing = [str(f) for f in critical if not f.exists()]
        if missing:
            print(f"❌ 警告：关键文件缺失 {missing}")
            return False
        return True
    
    def run(self):
        print("=" * 60)
        print("🧹 安全磁盘清理")
        print(f"时间: {datetime.now()}")
        print(f"模式: {'预览模式' if self.dry_run else '执行模式'}")
        
        usage = self.get_disk_usage()
        print(f"磁盘使用率: {usage}%")
        
        if usage < self.disk_threshold:
            print(f"✅ 磁盘使用率低于阈值 {self.disk_threshold}%，无需清理")
            return
        
        print(f"⚠️ 磁盘使用率超过阈值，开始清理...")
        
        # 执行清理
        log_cleaned = self.safe_clean_logs()
        temp_cleaned = self.safe_clean_temp()
        backup_cleaned = self.safe_clean_backups()
        
        print(f"\n📊 清理统计:")
        print(f"   日志文件: {len(log_cleaned)} 个")
        print(f"   临时文件: {len(temp_cleaned)} 个")
        print(f"   旧备份: {len(backup_cleaned)} 个")
        
        # 验证关键文件
        if self.check_critical_files():
            print("\n✅ 清理完成，关键文件完好")
        
        # 显示新使用率
        new_usage = self.get_disk_usage()
        print(f"\n磁盘使用率: {usage}% → {new_usage}%")
        print("=" * 60)

if __name__ == "__main__":
    import sys
    cleaner = SafeCleaner()
    cleaner.dry_run = "--dry" in sys.argv  # python safe_cleaner.py --dry 预览
    cleaner.run()
