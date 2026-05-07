#!/usr/bin/env python3
"""工程师 Agent - 系统运维、监控、自修复"""

import subprocess
import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path

class EngineerAgent:
    def __init__(self):
        self.status_file = Path("/mnt/d/clawsjoy/data/system_status.json")
        self.log_file = Path("/mnt/d/clawsjoy/logs/engineer.log")
        self.load_status()
    
    def load_status(self):
        if self.status_file.exists():
            with open(self.status_file) as f:
                self.status = json.load(f)
        else:
            self.status = {"services": {}, "health_checks": [], "fixes": []}
    
    def save_status(self):
        with open(self.status_file, 'w') as f:
            json.dump(self.status, f, ensure_ascii=False, indent=2)
    
    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {msg}"
        print(log_msg)
        with open(self.log_file, 'a') as f:
            f.write(log_msg + "\n")
    
    def check_services(self):
        """检查所有服务状态"""
        services = {
            "chat_api": {"url": "http://localhost:8101/api/agent", "method": "POST", "data": {"text": "ping"}},
            "promo_api": {"url": "http://localhost:8105/api/promo/make", "method": "POST", "data": {"city": "test"}},
            "web": {"url": "http://localhost:8082/", "method": "GET"},
            "joymate_api": {"url": "http://localhost:8093/api/tasks", "method": "GET"},
            "tts": {"url": "http://localhost:9000/api/tts", "method": "POST", "data": {"text": "test"}}
        }
        
        results = {}
        for name, config in services.items():
            try:
                if config["method"] == "GET":
                    resp = requests.get(config["url"], timeout=5)
                else:
                    resp = requests.post(config["url"], json=config.get("data", {}), timeout=5)
                
                if resp.status_code < 500:
                    results[name] = {"status": "ok", "code": resp.status_code}
                else:
                    results[name] = {"status": "error", "code": resp.status_code}
            except Exception as e:
                results[name] = {"status": "down", "error": str(e)}
        
        self.status["services"] = results
        self.save_status()
        return results
    
    def restart_service(self, service_name):
        """重启指定服务"""
        self.log(f"尝试重启 {service_name}")
        
        commands = {
            "promo_api": "cd /mnt/d/clawsjoy/bin && pkill -f promo_api; nohup python3 promo_api.py > /tmp/promo_api.log 2>&1 &",
            "chat_api": "cd /mnt/d/clawsjoy/bin && pkill -f chat_api_agent; nohup python3 chat_api_agent.py > /tmp/chat_api.log 2>&1 &",
            "web": "cd /mnt/d/clawsjoy && docker-compose restart web",
            "all": "cd /mnt/d/clawsjoy && docker-compose restart"
        }
        
        if service_name in commands:
            result = subprocess.run(commands[service_name], shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"✅ {service_name} 重启成功")
                self.status["fixes"].append({"service": service_name, "action": "restart", "result": "success", "time": datetime.now().isoformat()})
                return True
            else:
                self.log(f"❌ {service_name} 重启失败: {result.stderr}", "ERROR")
                return False
        return False
    
    def auto_fix(self):
        """自动修复已知问题"""
        fixes = []
        
        # 检查并修复各个服务
        for name, info in self.status["services"].items():
            if info.get("status") == "down":
                self.log(f"发现服务异常: {name}")
                if self.restart_service(name):
                    fixes.append({"service": name, "fix": "restart"})
                time.sleep(2)
        
        return fixes
    
    def health_report(self):
        """生成健康报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "services": self.status["services"],
            "summary": {
                "total": len(self.status["services"]),
                "ok": sum(1 for s in self.status["services"].values() if s.get("status") == "ok"),
                "error": sum(1 for s in self.status["services"].values() if s.get("status") == "error"),
                "down": sum(1 for s in self.status["services"].values() if s.get("status") == "down")
            },
            "recent_fixes": self.status["fixes"][-5:]
        }
        
        return report
    
    def run_health_check(self):
        """执行完整健康检查"""
        self.log("🏥 开始健康检查...")
        
        # 1. 检查服务
        services = self.check_services()
        self.log(f"服务状态: {len([s for s in services.values() if s['status']=='ok'])}/{len(services)} 正常")
        
        # 2. 尝试修复
        fixes = self.auto_fix()
        if fixes:
            self.log(f"执行了 {len(fixes)} 次修复")
        
        # 3. 生成报告
        report = self.health_report()
        
        # 4. 保存报告
        report_file = Path(f"data/health_report_{datetime.now().strftime('%Y%m%d')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report

if __name__ == "__main__":
    engineer = EngineerAgent()
    
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "check":
            result = engineer.check_services()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif cmd == "fix":
            result = engineer.auto_fix()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif cmd == "report":
            result = engineer.health_report()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif cmd == "run":
            result = engineer.run_health_check()
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认执行健康检查
        result = engineer.run_health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    def learn_fix(self, problem, symptom, solution):
        """学习新的修复方案"""
        fix = {
            "problem": problem,
            "symptom": symptom,
            "solution": solution,
            "learned_at": str(datetime.now())
        }
        
        # 保存到知识库
        import json
        from pathlib import Path
        kb_file = Path("/mnt/d/clawsjoy/data/knowledge/common_fixes.json")
        if kb_file.exists():
            with open(kb_file) as f:
                kb = json.load(f)
            kb["fixes"].append(fix)
            with open(kb_file, 'w') as f:
                json.dump(kb, f, indent=2)
        self.log(f"📚 学习了新修复方案: {problem}")
        return fix
    
    def get_learning_stats(self):
        """获取学习统计"""
        import json
        from pathlib import Path
        kb_file = Path("/mnt/d/clawsjoy/data/knowledge/common_fixes.json")
        if kb_file.exists():
            with open(kb_file) as f:
                kb = json.load(f)
            return {
                "total_fixes": len(kb.get("fixes", [])),
                "fixes": [f["problem"] for f in kb.get("fixes", [])]
            }
        return {"total_fixes": 0, "fixes": []}

    def self_learn_from_errors(self):
        """从错误日志中学习故障模式"""
        from pathlib import Path
        import re
        
        log_dir = Path("/mnt/d/clawsjoy/logs")
        error_patterns = {}
        
        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_size > 0:
                with open(log_file) as f:
                    content = f.read()
                # 提取错误模式
                errors = re.findall(r'ERROR|Error|Exception|failed|timeout', content)
                for err in errors[:20]:
                    error_patterns[err] = error_patterns.get(err, 0) + 1
        
        # 记录高频错误模式
        new_knowledge = []
        for pattern, count in error_patterns.items():
            if count > 3:  # 出现超过3次
                new_knowledge.append({
                    "pattern": pattern,
                    "count": count,
                    "learned_at": time.time()
                })
        
        if new_knowledge:
            self.status["learned_patterns"] = new_knowledge
            self.save_status()
            print(f"🔧 自我学习: 记录了 {len(new_knowledge)} 个错误模式")
        
        return new_knowledge
    
    def auto_heal_loop(self, interval_minutes=10):
        """自动修复循环"""
        import time
        while True:
            print(f"🔧 工程师自动巡检 (间隔{interval_minutes}分钟)")
            self.self_learn_from_errors()
            self.auto_fix()
            time.sleep(interval_minutes * 60)

    def self_learn_from_errors(self):
        """从错误日志中学习故障模式"""
        from pathlib import Path
        import re
        
        log_dir = Path("/mnt/d/clawsjoy/logs")
        error_patterns = {}
        
        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_size > 0:
                with open(log_file) as f:
                    content = f.read()
                # 提取错误模式
                errors = re.findall(r'ERROR|Error|Exception|failed|timeout', content)
                for err in errors[:20]:
                    error_patterns[err] = error_patterns.get(err, 0) + 1
        
        # 记录高频错误模式
        new_knowledge = []
        for pattern, count in error_patterns.items():
            if count > 3:  # 出现超过3次
                new_knowledge.append({
                    "pattern": pattern,
                    "count": count,
                    "learned_at": time.time()
                })
        
        if new_knowledge:
            self.status["learned_patterns"] = new_knowledge
            self.save_status()
            print(f"🔧 自我学习: 记录了 {len(new_knowledge)} 个错误模式")
        
        return new_knowledge
    
    def auto_heal_loop(self, interval_minutes=10):
        """自动修复循环"""
        import time
        while True:
            print(f"🔧 工程师自动巡检 (间隔{interval_minutes}分钟)")
            self.self_learn_from_errors()
            self.auto_fix()
            time.sleep(interval_minutes * 60)

    def self_learn_from_errors(self):
        """从错误日志中学习故障模式"""
        from pathlib import Path
        import re
        
        log_dir = Path("/mnt/d/clawsjoy/logs")
        error_patterns = {}
        
        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_size > 0:
                with open(log_file) as f:
                    content = f.read()
                # 提取错误模式
                errors = re.findall(r'ERROR|Error|Exception|failed|timeout', content)
                for err in errors[:20]:
                    error_patterns[err] = error_patterns.get(err, 0) + 1
        
        # 记录高频错误模式
        new_knowledge = []
        for pattern, count in error_patterns.items():
            if count > 3:  # 出现超过3次
                new_knowledge.append({
                    "pattern": pattern,
                    "count": count,
                    "learned_at": time.time()
                })
        
        if new_knowledge:
            self.status["learned_patterns"] = new_knowledge
            self.save_status()
            print(f"🔧 自我学习: 记录了 {len(new_knowledge)} 个错误模式")
        
        return new_knowledge
    
    def auto_heal_loop(self, interval_minutes=10):
        """自动修复循环"""
        import time
        while True:
            print(f"🔧 工程师自动巡检 (间隔{interval_minutes}分钟)")
            self.self_learn_from_errors()
            self.auto_fix()
            time.sleep(interval_minutes * 60)
