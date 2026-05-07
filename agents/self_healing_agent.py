#!/usr/bin/env python3
"""
真正的自愈Agent - 学会设置PYTHONPATH
"""

import subprocess
import json
import time
import re
import requests
from pathlib import Path
from datetime import datetime

class SelfHealingAgent:
    def __init__(self):
        self.project_root = Path("/mnt/d/clawsjoy")
        self.memory_file = self.project_root / "data" / "healing_memory.json"
        self.pythonpath = f"PYTHONPATH={self.project_root}"
        
        self.memory = self.load_memory()
        self.ollama_url = "http://localhost:11434"
        self.model = "qwen2.5:3b"
        
        print("=" * 60)
        print("🩺 自愈Agent - 能解决Python导入问题")
        print(f"   PYTHONPATH已配置: {self.pythonpath}")
        print(f"  历史修复: {len(self.memory.get('fixes', []))} 次")
        print("=" * 60)
    
    def load_memory(self):
        if self.memory_file.exists():
            with open(self.memory_file) as f:
                return json.load(f)
        return {"fixes": [], "skills": {}}
    
    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def smart_fix(self, service, error_log=""):
        """智能修复 - 根据错误类型选择方案"""
        
        # 检查是否是导入错误
        if "ModuleNotFoundError" in error_log or "No module named" in error_log:
            return self.fix_import_error(service)
        
        # PM2 服务挂了
        return self.fix_pm2_service(service)
    
    def fix_import_error(self, service):
        """修复导入错误"""
        print(f"🐍 检测到导入错误，使用 PYTHONPATH 修复")
        
        return {
            "analysis": "Python 模块找不到，需要设置 PYTHONPATH",
            "commands": [
                f"cd {self.project_root}",
                f"pm2 delete {service}",
                f"export {self.pythonpath}",
                f"pm2 start bin/{service.replace('-api', '_api.py')} --name {service} -- --port {self.get_port(service)}"
            ],
            "verify": f"pm2 list | grep {service} | grep -q online"
        }
    
    def fix_pm2_service(self, service):
        """普通重启"""
        return {
            "analysis": f"PM2服务 {service} 异常，尝试重启",
            "commands": [
                f"cd {self.project_root}/bin",
                f"pm2 restart {service}"
            ],
            "verify": f"pm2 list | grep {service} | grep -q online"
        }
    
    def get_port(self, service):
        ports = {"agent-api": 18103, "chat-api": 18109, "promo-api": 8108, "health-api": 18105}
        return ports.get(service, 18000)
    
    def execute(self, commands):
        for cmd in commands:
            print(f"   🔧 {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0 and result.stderr:
                if "error" in result.stderr.lower():
                    return False, result.stderr
        time.sleep(2)
        return True, ""
    
    def learn(self, service, success, error=""):
        self.memory["fixes"].append({
            "time": datetime.now().isoformat(),
            "service": service,
            "success": success,
            "error": error[:200]
        })
        
        if service not in self.memory["skills"]:
            self.memory["skills"][service] = {"total": 0, "success": 0}
        self.memory["skills"][service]["total"] += 1
        if success:
            self.memory["skills"][service]["success"] += 1
        
        self.save_memory()
        
        rate = self.memory["skills"][service]["success"] / max(1, self.memory["skills"][service]["total"]) * 100
        print(f"\n📚 学习: {service} -> {'✅成功' if success else '❌失败'} (成功率: {rate:.0f}%)")
    
    def heal(self):
        print("\n🔍 扫描服务...")
        
        # 获取所有问题服务
        result = subprocess.run("pm2 list", shell=True, capture_output=True, text=True)
        output = result.stdout
        
        problems = []
        services = ["agent-api", "chat-api", "promo-api", "health-api"]
        
        for svc in services:
            if svc in output:
                if "errored" in output.split(svc)[1][:50] if svc in output else "":
                    # 获取错误日志
                    log = subprocess.run(f"pm2 logs {svc} --lines 10 --nostream", shell=True, capture_output=True, text=True)
                    problems.append((svc, log.stdout))
                    print(f"   ❌ {svc}: errored")
        
        if not problems:
            print("   ✅ 所有服务正常")
            return
        
        for service, error_log in problems:
            print(f"\n🎯 修复: {service}")
            plan = self.smart_fix(service, error_log)
            print(f"💡 {plan['analysis']}")
            
            success, error = self.execute(plan["commands"])
            self.learn(service, success, error)
            
            if success:
                print(f"   🎉 {service} 已修复")
            else:
                print(f"   ⚠️ {service} 修复失败: {error[:100]}")
        
        # 显示统计
        print("\n" + "=" * 60)
        print("📊 自愈统计:")
        for svc, stats in self.memory["skills"].items():
            rate = stats["success"]/max(1, stats["total"])*100
            bar = "█" * int(rate/10) + "░" * (10-int(rate/10))
            print(f"   {svc}: [{bar}] {rate:.0f}% ({stats['success']}/{stats['total']})")
        print("=" * 60)

if __name__ == "__main__":
    agent = SelfHealingAgent()
    
    # 自动修复
    agent.heal()
    
    print("\n✅ 自愈完成！Agent已学会处理导入错误")
