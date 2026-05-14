from lib.unified_config import config
#!/usr/bin/env python3
"""
真正的学习型运维 Agent - 使用 Ollama HTTP API
"""

import subprocess
import json
import time
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class SimpleLearningAgent:
    def __init__(self):
        self.project_root = Path("/mnt/d/clawsjoy")
        self.memory_dir = self.project_root / "data" / "agent_memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.ollama_url = "http://localhost:11434"
        self.model = config.LLM["fast_model"]
        
        self.llm_available = self._test_ollama()
        self.experiences = self._load_experiences()
        self.stats = self._load_stats()
        
        print("=" * 60)
        print("🧠 学习型运维 Agent 启动")
        print(f"   Ollama: {'✅ 可用' if self.llm_available else '❌ 不可用'}")
        print(f"   模型: {self.model}")
        print(f"   历史: {len(self.experiences)} 条经验, 成功率 {self.stats['success']}/{self.stats['total']}")
        print("=" * 60)
    
    def _test_ollama(self) -> bool:
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except:
            return False
    
    def _load_experiences(self) -> List[Dict]:
        exp_file = self.memory_dir / "experiences.json"
        if exp_file.exists():
            try:
                with open(exp_file) as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_experiences(self):
        exp_file = self.memory_dir / "experiences.json"
        with open(exp_file, 'w') as f:
            json.dump(self.experiences[-100:], f, indent=2)
    
    def _load_stats(self) -> Dict:
        stats_file = self.memory_dir / "stats.json"
        if stats_file.exists():
            try:
                with open(stats_file) as f:
                    return json.load(f)
            except:
                return {"total": 0, "success": 0, "by_service": {}}
        return {"total": 0, "success": 0, "by_service": {}}
    
    def _save_stats(self):
        stats_file = self.memory_dir / "stats.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def observe(self) -> Dict:
        print("\n👁️ 观察中...")
        state = {}
        result = subprocess.run("pm2 list", shell=True, capture_output=True, text=True)
        output = result.stdout
        
        for svc in ["agent-api", "chat-api", "promo-api", "health-api"]:
            if svc in output:
                if 'errored' in output:
                    state[svc] = "errored"
                    print(f"   ⚠️ {svc}: errored")
                elif 'online' in output:
                    state[svc] = "online"
                    print(f"   ✅ {svc}: online")
                else:
                    state[svc] = "stopped"
                    print(f"   ⚠️ {svc}: stopped")
            else:
                state[svc] = "not_found"
                print(f"   ⚠️ {svc}: not_found")
        return state
    
    def think_with_llm(self, service: str, status: str) -> Dict:
        if not self.llm_available:
            return self._rule_based_fix(service)
        
        prompt = f"""运维专家。服务 {service} 状态 {status}，给出修复命令。
返回JSON: {{"analysis": "原因", "commands": ["命令"], "verify": "验证命令"}}"""
        
        try:
            resp = requests.post(f"{self.ollama_url}/api/generate", json={
                "model": self.model, "prompt": prompt, "stream": False, "temperature": 0.3
            }, timeout=60)
            if resp.status_code == 200:
                response = resp.json().get('response', '')
                json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        except Exception as e:
            print(f"   LLM失败: {e}")
        return self._rule_based_fix(service)
    
    def _rule_based_fix(self, service: str) -> Dict:
        fixes = {
            "agent-api": {
                "analysis": "重启agent-api",
                "commands": [f"cd /mnt/d/clawsjoy/bin && pm2 start agent_api.py --name agent-api -- --port 18103 2>/dev/null || pm2 restart agent-api"],
                "verify": "pm2 list | grep agent-api | grep -q online"
            },
            "chat-api": {
                "analysis": "重启chat-api",
                "commands": [f"cd /mnt/d/clawsjoy/bin && pm2 start chat_api.py --name chat-api -- --port 18109 2>/dev/null || pm2 restart chat-api"],
                "verify": "pm2 list | grep chat-api | grep -q online"
            },
            "promo-api": {
                "analysis": "重启promo-api",
                "commands": [f"cd /mnt/d/clawsjoy/bin && pm2 start promo_api.py --name promo-api -- --port 8108 2>/dev/null || pm2 restart promo-api"],
                "verify": "pm2 list | grep promo-api | grep -q online"
            },
            "health-api": {
                "analysis": "重启health-api",
                "commands": [f"cd /mnt/d/clawsjoy/bin && pm2 start health_api.py --name health-api -- --port 18105 2>/dev/null || pm2 restart health-api"],
                "verify": "pm2 list | grep health-api | grep -q online"
            }
        }
        return fixes.get(service, {"analysis": f"重启{service}", "commands": [f"pm2 restart {service}"], "verify": f"pm2 list | grep {service}"})
    
    def execute(self, commands: List[str], verify_cmd: str) -> Tuple[bool, float]:
        start = time.time()
        for cmd in commands:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if r.returncode != 0 and "error" in r.stderr.lower():
                return False, time.time() - start
        time.sleep(2)
        if verify_cmd:
            success = subprocess.run(verify_cmd, shell=True).returncode == 0
        else:
            success = True
        return success, time.time() - start
    
    def learn(self, service: str, status: str, plan: Dict, success: bool, duration: float):
        self.experiences.append({
            "id": len(self.experiences)+1, "timestamp": datetime.now().isoformat(),
            "service": service, "status": status, "commands": plan.get("commands", []),
            "success": success, "duration": round(duration, 2)
        })
        self._save_experiences()
        
        self.stats["total"] += 1
        if success:
            self.stats["success"] += 1
        if service not in self.stats["by_service"]:
            self.stats["by_service"][service] = {"total": 0, "success": 0}
        self.stats["by_service"][service]["total"] += 1
        if success:
            self.stats["by_service"][service]["success"] += 1
        self._save_stats()
        
        print(f"\n📝 学习: {service} -> {'✅成功' if success else '❌失败'} (耗时{duration:.1f}s)")
        print(f"   全局成功率: {self.stats['success']}/{self.stats['total']}")
    
    def heal(self):
        print("\n" + "=" * 60)
        state = self.observe()
        problems = [f"{svc}.{status}" for svc, status in state.items() if status != "online"]
        
        if not problems:
            print("\n✅ 所有服务正常")
            return True
        
        print(f"\n🔍 发现 {len(problems)} 个问题")
        for problem in problems:
            service = problem.split('.')[0]
            status = problem.split('.')[1]
            print(f"\n🎯 处理: {service} ({status})")
            plan = self.think_with_llm(service, status)
            print(f"💡 {plan.get('analysis', '')}")
            success, duration = self.execute(plan.get("commands", []), plan.get("verify", ""))
            self.learn(service, status, plan, success, duration)
        
        print("\n" + "=" * 60)
        print("📊 技能统计:")
        for svc, stats in self.stats["by_service"].items():
            rate = stats["success"]/max(stats["total"],1)*100
            bar = "█" * int(rate/10) + "░" * (10-int(rate/10))
            print(f"   {svc}: [{bar}] {rate:.0f}% ({stats['success']}/{stats['total']})")
        return True

def main():
    agent = SimpleLearningAgent()
    for i in range(3):
        print(f"\n{'🔄'*30}\n第 {i+1} 轮\n{'🔄'*30}")
        agent.heal()
        time.sleep(2)
    print("\n✅ 学习完成！")

if __name__ == "__main__":
    main()
