#!/usr/bin/env python3
"""
学习型运维 Agent V2 - 带服务管理方式上下文
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
        self.model = "qwen2.5:3b"
        
        # 服务管理方式映射
        self.service_type = {
            "agent-api": "pm2",
            "chat-api": "pm2",
            "promo-api": "pm2",
            "health-api": "pm2",
            "web": "docker",
            "postgres": "docker",
            "redis": "docker"
        }
        
        self.llm_available = self._test_ollama()
        self.experiences = self._load_experiences()
        self.stats = self._load_stats()
        
        print("=" * 60)
        print("🧠 学习型运维 Agent V2 (带服务上下文)")
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
                lines = output.split('\n')
                for line in lines:
                    if svc in line:
                        if 'errored' in line:
                            state[svc] = "errored"
                            print(f"   ⚠️ {svc}: errored (PM2)")
                        elif 'online' in line:
                            state[svc] = "online"
                            print(f"   ✅ {svc}: online")
                        else:
                            state[svc] = "stopped"
                            print(f"   ⚠️ {svc}: stopped")
                        break
            else:
                state[svc] = "not_found"
                print(f"   ⚠️ {svc}: not_found")
        return state
    
    def get_historical_success(self, service: str) -> str:
        """获取历史成功率作为参考"""
        if service in self.stats["by_service"]:
            stats = self.stats["by_service"][service]
            rate = stats["success"]/max(stats["total"],1)*100
            return f"历史成功率: {rate:.0f}% ({stats['success']}/{stats['total']})"
        return "无历史记录"
    
    def think_with_llm(self, service: str, status: str) -> Dict:
        """LLM思考 - 带正确的服务管理上下文"""
        if not self.llm_available:
            return self._rule_based_fix(service)
        
        manager = self.service_type.get(service, "pm2")
        history = self.get_historical_success(service)
        
        # 提供正确的命令模板
        if manager == "pm2":
            cmd_template = f"cd /mnt/d/clawsjoy/bin && pm2 start {service.replace('-api', '_api.py')} --name {service} --port PORT 2>/dev/null || pm2 restart {service}"
            verify_template = f"pm2 list | grep {service} | grep -q online"
        else:
            cmd_template = f"docker restart {service}"
            verify_template = f"docker ps | grep {service}"
        
        prompt = f"""你是运维专家。服务 {service} 状态 {status}。

重要：{service} 是由 PM2 管理的 Node.js/Python 服务，不是 Docker 容器！
修复方式：使用 pm2 命令，不要用 docker。

{history}

可用命令模板：
- 启动/重启: {cmd_template}
- 查看日志: pm2 logs {service} --lines 20
- 检查状态: pm2 list

返回JSON格式：
{{"analysis": "原因分析", "commands": ["具体修复命令"], "verify": "{verify_template}"}}"""
        
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.1,
                    "num_predict": 300
                },
                timeout=60
            )
            
            if resp.status_code == 200:
                response = resp.json().get('response', '')
                print(f"   🤔 LLM: {response[:80]}...")
                
                # 提取JSON
                json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
                if json_match:
                    try:
                        plan = json.loads(json_match.group())
                        if "commands" in plan:
                            print(f"   ✅ 方案: {plan.get('analysis', '')[:40]}")
                            return plan
                    except:
                        pass
        except Exception as e:
            print(f"   ⚠️ LLM错误: {e}")
        
        return self._rule_based_fix(service)
    
    def _rule_based_fix(self, service: str) -> Dict:
        """规则引擎 - 使用正确的PM2命令"""
        # 端口映射
        ports = {
            "agent-api": 18103,
            "chat-api": 18109,
            "promo-api": 8108,
            "health-api": 18105
        }
        
        port = ports.get(service, 18000)
        script = service.replace('-api', '_api.py')
        
        return {
            "analysis": f"重启 {service} (PM2管理)",
            "commands": [
                f"cd /mnt/d/clawsjoy/bin && pm2 start {script} --name {service} -- --port {port} 2>/dev/null || pm2 restart {service}"
            ],
            "verify": f"pm2 list | grep {service} | grep -q online"
        }
    
    def execute(self, commands: List[str], verify_cmd: str) -> Tuple[bool, float, str]:
        start = time.time()
        error_msg = ""
        
        for cmd in commands:
            print(f"   🔧 {cmd[:100]}...")
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if r.returncode != 0:
                error_msg = r.stderr[:200]
                if "error" in error_msg.lower() or "fail" in error_msg.lower():
                    print(f"   ❌ 命令失败")
                    return False, time.time() - start, error_msg
        
        time.sleep(2)
        
        if verify_cmd:
            verify_result = subprocess.run(verify_cmd, shell=True)
            success = verify_result.returncode == 0
        else:
            success = True
        
        duration = time.time() - start
        
        if success:
            print(f"   ✅ 成功 ({duration:.1f}s)")
        else:
            print(f"   ❌ 验证失败")
        
        return success, duration, error_msg
    
    def learn(self, service: str, status: str, plan: Dict, success: bool, duration: float, error_msg: str = ""):
        """学习经验"""
        self.experiences.append({
            "id": len(self.experiences)+1,
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "status": status,
            "analysis": plan.get("analysis", ""),
            "commands": plan.get("commands", []),
            "success": success,
            "duration": round(duration, 2),
            "error": error_msg[:200]
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
        
        print(f"\n📝 学习: {service} -> {'✅成功' if success else '❌失败'} ({duration:.1f}s)")
        print(f"   {self.get_historical_success(service)}")
    
    def heal(self):
        print("\n" + "=" * 60)
        state = self.observe()
        
        problems = [(svc, status) for svc, status in state.items() if status != "online"]
        
        if not problems:
            print("\n✅ 所有服务正常")
            return True
        
        print(f"\n🔍 发现 {len(problems)} 个问题")
        
        for service, status in problems:
            print(f"\n🎯 处理: {service} ({status})")
            plan = self.think_with_llm(service, status)
            print(f"💡 {plan.get('analysis', '')}")
            
            success, duration, error = self.execute(plan.get("commands", []), plan.get("verify", ""))
            self.learn(service, status, plan, success, duration, error)
        
        print("\n" + "=" * 60)
        print("📊 技能统计:")
        for svc, stats in sorted(self.stats["by_service"].items()):
            rate = stats["success"]/max(stats["total"],1)*100
            bar = "█" * int(rate/10) + "░" * (10 - int(rate/10))
            print(f"   {svc}: [{bar}] {rate:.0f}% ({stats['success']}/{stats['total']})")
        return True

def main():
    agent = SimpleLearningAgent()
    for i in range(3):
        print(f"\n{'🔄'*30}\n第 {i+1} 轮学习\n{'🔄'*30}")
        agent.heal()
        time.sleep(2)
    print("\n✅ 学习完成！")

if __name__ == "__main__":
    main()
