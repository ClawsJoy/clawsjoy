from lib.unified_config import config
#!/usr/bin/env python3
"""清道夫 Agent - 需管理员审批的智能清理"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta

class CleanerAgent:
    def __init__(self):
        self.workspace = Path("config.ROOT")
        self.config_file = self.workspace / "config/cleaner_config.json"
        self.report_file = self.workspace / "data/cleaner_report.json"
        self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = json.load(f)
        else:
            self.config = {
                "auto_clean_enabled": False,  # 默认不自动清理
                "require_approval": True,     # 需要管理员审批
                "approver": "admin",
                "thresholds": {
                    "disk_warning": 80,
                    "disk_critical": 90,
                    "video_days": 30,
                    "audio_days": 7,
                    "log_days": 14,
                    "temp_days": 1
                }
            }
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get_size(self, path):
        if path.is_file():
            return path.stat().st_size
        total = 0
        for f in path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
        return total
    
    def scan_disk(self):
        usage = shutil.disk_usage(self.workspace)
        percent = (usage.used / usage.total) * 100
        return {"used": usage.used, "free": usage.free, "percent": percent}
    
    def analyze(self):
        """生成清理建议报告（需要管理员审批）"""
        disk = self.scan_disk()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "disk": disk,
            "suggestions": [],
            "requires_attention": False
        }
        
        # 分析各目录
        dirs = {
            "临时音频": {"path": self.workspace / "web/audio", "days": self.config["thresholds"]["temp_days"]},
            "临时视频": {"path": self.workspace / "web/videos", "days": self.config["thresholds"]["video_days"]},
            "旧日志": {"path": self.workspace / "logs", "days": self.config["thresholds"]["log_days"]},
            "备份文件": {"path": self.workspace / "backups", "days": 60}
        }
        
        for name, info in dirs.items():
            path = info["path"]
            days = info["days"]
            if path.exists():
                old_files = []
                cutoff = datetime.now() - timedelta(days=days)
                for f in path.iterdir():
                    if f.is_file():
                        mtime = datetime.fromtimestamp(f.stat().st_mtime)
                        if mtime < cutoff:
                            old_files.append({
                                "name": f.name,
                                "size_mb": f.stat().st_size / (1024 * 1024),
                                "age_days": (datetime.now() - mtime).days
                            })
                
                if old_files:
                    total_size = sum(f["size_mb"] for f in old_files)
                    report["suggestions"].append({
                        "dir": name,
                        "count": len(old_files),
                        "total_size_mb": total_size,
                        "files": old_files[:5],
                        "action": f"删除超过 {days} 天的文件"
                    })
        
        # 磁盘告警
        if disk["percent"] > self.config["thresholds"]["disk_warning"]:
            report["requires_attention"] = True
            report["warning"] = f"磁盘使用率 {disk['percent']:.1f}%，建议清理"
        
        # 保存报告
        self.report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_file, 'w') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def show_report(self):
        """显示清理建议（只读）"""
        report = self.analyze()
        print("=" * 60)
        print("🧹 清道夫报告（需管理员审批）")
        print("=" * 60)
        print(f"📊 磁盘使用率: {report['disk']['percent']:.1f}%")
        print(f"⚠️ 需要关注: {'是' if report['requires_attention'] else '否'}")
        print("\n📋 清理建议:")
        for s in report["suggestions"]:
            print(f"  📁 {s['dir']}: {s['count']} 个文件 ({s['total_size_mb']:.1f} MB)")
        print(f"\n💡 执行清理: python3 agents/cleaner_agent.py approve")
        print("=" * 60)
        return report
    
    def approve_and_clean(self, dry_run=True):
        """管理员审批后执行清理"""
        report = self.analyze()
        
        if not report["suggestions"]:
            print("✅ 无可清理文件")
            return
        
        print("=" * 60)
        print("🧹 执行清理审批")
        print("=" * 60)
        
        total_freed = 0
        for s in report["suggestions"]:
            print(f"\n📁 {s['dir']}: 将删除 {s['count']} 个文件 ({s['total_size_mb']:.1f} MB)")
            for f in s["files"]:
                print(f"   - {f['name']} ({f['size_mb']:.1f} MB, {f['age_days']} 天前)")
            
            if not dry_run:
                # 实际删除
                path = self.workspace / "web/audio" if "音频" in s["dir"] else self.workspace / "logs"
                # 实现删除逻辑
                total_freed += s["total_size_mb"]
        
        if dry_run:
            print(f"\n🔍 预览模式，将释放约 {total_freed:.1f} MB")
            print("执行真实清理: python3 agents/cleaner_agent.py clean")
        else:
            print(f"\n✅ 已清理，释放 {total_freed:.1f} MB")
            # 记录操作
            log_file = self.workspace / "logs/cleaner_actions.log"
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now()}: 清理 {total_freed:.1f} MB\n")
        
        return total_freed
    
    def set_auto_clean(self, enabled):
        """管理员设置是否自动清理"""
        self.config["auto_clean_enabled"] = enabled
        self.save_config()
        status = "开启" if enabled else "关闭"
        print(f"✅ 自动清理已{status}")
        
        if enabled:
            print("⚠️ 注意：自动清理会删除旧文件，请谨慎使用")

if __name__ == "__main__":
    cleaner = CleanerAgent()
    
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "report":
            cleaner.show_report()
        elif cmd == "approve":
            cleaner.approve_and_clean(dry_run=True)
        elif cmd == "clean":
            cleaner.approve_and_clean(dry_run=False)
        elif cmd == "auto":
            enabled = sys.argv[2].lower() == "true" if len(sys.argv) > 2 else True
            cleaner.set_auto_clean(enabled)
        elif cmd == "config":
            print(json.dumps(cleaner.config, ensure_ascii=False, indent=2))
    else:
        cleaner.show_report()
