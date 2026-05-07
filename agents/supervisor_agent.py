#!/usr/bin/env python3
"""
全能运维主管Agent - 管理所有日常维护任务
"""

import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime

class SupervisorAgent:
    def __init__(self):
        self.project_root = Path("/mnt/d/clawsjoy")
        self.logs_dir = self.project_root / "logs"
        self.backup_dir = self.project_root / "backups"
        
        # 任务清单
        self.tasks = [
            ("磁盘清理", self.clean_disk),
            ("日志压缩", self.rotate_logs),
            ("内存检查", self.check_memory),
            ("端口检查", self.check_ports),
            ("备份验证", self.verify_backups),
            ("旧文件清理", self.clean_old_files),
        ]
    
    def clean_disk(self):
        """清理磁盘"""
        # 获取磁盘使用率
        result = subprocess.run("df -h /mnt/d | tail -1 | awk '{print $5}'", 
                                shell=True, capture_output=True, text=True)
        used = result.stdout.strip().replace('%', '')
        
        if int(used) > 80:
            print(f"⚠️ 磁盘使用率 {used}%，开始清理...")
            
            # 清理超过7天的日志
            subprocess.run(f"find {self.logs_dir} -name '*.log' -mtime +7 -delete", shell=True)
            # 清理临时文件
            subprocess.run(f"find {self.project_root} -name '*.tmp' -delete", shell=True)
            
            print(f"✅ 磁盘清理完成")
            return True
        return False
    
    def rotate_logs(self):
        """压缩大日志"""
        result = subprocess.run(f"find {self.logs_dir} -name '*.log' -size +100M", 
                                shell=True, capture_output=True, text=True)
        if result.stdout:
            for log in result.stdout.strip().split('\n'):
                if log:
                    subprocess.run(f"gzip {log}", shell=True)
                    print(f"✅ 已压缩: {log}")
            return True
        return False
    
    def check_memory(self):
        """检查内存使用"""
        result = subprocess.run("pm2 list | grep -E '([0-9]+\\.[0-9]+)mb' | awk '{print $10, $12}'",
                                shell=True, capture_output=True, text=True)
        
        restarted = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    service = parts[0]
                    memory = parts[1].replace('mb', '')
                    if float(memory) > 500:  # 超过500MB
                        subprocess.run(f"pm2 restart {service}", shell=True)
                        restarted.append(service)
        
        if restarted:
            print(f"🔄 已重启高内存服务: {', '.join(restarted)}")
            return True
        return False
    
    def check_ports(self):
        """检查端口冲突"""
        ports = {"agent-api": 18103, "chat-api": 18109, "promo-api": 8108}
        
        for service, port in ports.items():
            # 检查端口是否被监听
            result = subprocess.run(f"netstat -tlnp 2>/dev/null | grep ':{port}'", 
                                    shell=True, capture_output=True, text=True)
            if not result.stdout:
                print(f"⚠️ {service} 端口 {port} 未监听，尝试重启...")
                subprocess.run(f"pm2 restart {service}", shell=True)
                return True
        return False
    
    def verify_backups(self):
        """验证备份"""
        backup_files = list(self.backup_dir.glob("*.sql.gz"))
        if not backup_files:
            print("⚠️ 没有备份文件，创建备份...")
            subprocess.run(f"cd {self.project_root} && ./bin/backup.sh", shell=True)
            return True
        
        # 检查最新备份是否超过24小时
        latest = max(backup_files, key=lambda x: x.stat().st_mtime)
        age = datetime.now().timestamp() - latest.stat().st_mtime
        
        if age > 86400:  # 24小时
            print(f"⚠️ 备份超过24小时，更新备份...")
            subprocess.run(f"cd {self.project_root} && ./bin/backup.sh", shell=True)
            return True
        return False
    
    def clean_old_files(self):
        """清理旧文件"""
        # 清理超过30天的旧日志压缩包
        subprocess.run(f"find {self.logs_dir} -name '*.gz' -mtime +30 -delete", shell=True)
        # 清理超过7天的临时文件
        subprocess.run(f"find /tmp -name 'clawsjoy_*' -mtime +1 -delete 2>/dev/null", shell=True)
        return True
    
    def run(self):
        print("=" * 60)
        print("🔧 运维主管Agent启动")
        print(f"时间: {datetime.now()}")
        print("=" * 60)
        
        executed = []
        for task_name, task_func in self.tasks:
            try:
                if task_func():
                    executed.append(task_name)
            except Exception as e:
                print(f"❌ {task_name} 失败: {e}")
        
        if executed:
            print(f"\n✅ 已执行: {', '.join(executed)}")
        else:
            print("\n✅ 所有检查通过，无需操作")
        
        print("=" * 60)

if __name__ == "__main__":
    agent = SupervisorAgent()
    agent.run()
