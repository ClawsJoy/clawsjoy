#!/usr/bin/env python3
"""
真正的学习型运维 Agent - 修复版（优化LLM调用）
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
        self.model = "qwen2.5:3b"  # 使用3B更快
        
        self.llm_available = self._test_ollama()
        self.experiences = self._load_experiences()
        self.stats = self._load_stats()
        
        print("=" * 60)
        print("🧠 学习型运维 Agent 启动 (修复版)")
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
                # 找到包含该服务的行
                lines = output.split('\n')
                found = False
                for line in lines:
                    if svc in line:
                        found = True
                        if 'errored' in line:
                            state[svc] = "errored"
                            print(f"   ⚠️ {svc}: errored")
                        elif 'online' in line:
                            state[svc] = "online"
                            print(f"   ✅ {svc}: online")
                        else:
                            state[svc] = "stopped"
                            print(f"   ⚠️ {svc}: stopped")
                        break
                if not found:
                    state[svc] = "not_found"
                    print(f"   ⚠️ {svc}: not_found")
            else:
                state[svc] = "not_found"
                print(f"   ⚠️ {svc}: not_found")
        return state
    
    def think_with_llm(self, service: str, status: str) -> Dict:
        """使用LLM思考，带重试和更好的解析"""
        if not self.llm_available:
            return self._rule_based_fix(service)
        
        # 更清晰的prompt，强制JSON格式
        prompt = f"""你是运维专家。服务 {service} 状态是 {status}，需要修复。

项目路径: /mnt/d/clawsjoy
可用命令: pm2, docker, docker-compose

请返回JSON格式（不要有其他文字）：
{{"analysis": "简短原因分析", "commands": ["具体bash命令"], "verify": "验证命令"}}"""
        
        for attempt in range(2):  # 重试一次
            try:
                resp = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.1,  # 降低温度，输出更稳定
                        "num_predict": 256    # 限制输出长度
                    },
                    timeout=60
                )
                
                if resp.status_code == 200:
                    response = resp.json().get('response', '')
                    print(f"   🤔 LLM响应: {response[:100]}...")
                    
                    # 尝试提取JSON
                    # 方法1：找 {...}
                    json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
                    if json_match:
                        try:
                            plan = json.loads(json_match.group())
                            if "commands" in plan:
                                print(f"   ✅ LLM分析: {plan.get('analysis', '无')[:50]}")
                                return plan
                        except:
                            pass
                    
                    # 方法2：如果没找到，尝试从文本中提取命令
                    commands = re.findall(r'(?:pm2|docker|cd).*?(?:\||$)', response)
                    if commands:
                        return {
                            "analysis": f"LLM建议修复{service}",
                            "commands": [cmd.strip() for cmd in commands[:2]],
                            "verify": f"pm2 list | grep {service} | grep -q online"
                        }
                        
            except Exception as e:
                print(f"   ⚠️ LLM尝试{attempt+1}失败: {e}")
                time.sleep(1)
        
        # 降级到规则引擎
        return self._rule_based_fix(service)
    
    def _rule_based_fix(self, service: str) -> Dict:
        """规则引擎兜底"""
        fixes = {
            "agent-api": {
                "analysis": "重启agent-api服务",
                "commands": [f"cd /mnt/d/clawsjoy/bin && pm2 start agent_api.py --name agent-api -- --port 18103 2>/dev/null || pm2 restart agent-api"],
                "verify": "pm2 list | grep agent-api | grep -q online"
            },
            "chat-api": {
                "analysis": "重启chat-api服务",
                "commands": [f"cd /mnt/d/clawsjoy/bin && pm2 start chat_api.py --name chat-api -- --port 18109 2>/dev/null || pm2 restart chat-api"],
                "verify": "pm2 list | grep chat-api | grep -q online"
            },
            "promo-api": {
                "analysis": "重启promo-api服务",
                "commands": [f"cd /mnt/d/clawsjoy/bin && pm2 start promo_api.py --name promo-api -- --port 8108 2>/dev/null || pm2 restart promo-api"],
                "verify": "pm2 list | grep promo-api | grep -q online"
            },
            "health-api": {
                "analysis": "重启health-api服务",
                "commands": [f"cd /mnt/d/clawsjoy/bin && pm2 start health_api.py --name health-api -- --port 18105 2>/dev/null || pm2 restart health-api"],
                "verify": "pm2 list | grep health-api | grep -q online"
            }
        }
        return fixes.get(service, {
            "analysis": f"尝试重启{service}",
            "commands": [f"pm2 restart {service}"],
            "verify": f"pm2 list | grep {service}"
        })
    
    def execute(self, commands: List[str], verify_cmd: str) -> Tuple[bool, float]:
        start = time.time()
        for cmd in commands:
            print(f"   🔧 执行: {cmd[:80]}...")
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if r.returncode != 0 and r.stderr and ("error" in r.stderr.lower() or "fail" in r.stderr.lower()):
                print(f"   ❌ 失败: {r.stderr[:100]}")
                return False, time.time() - start
        
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
        
        return success, duration
    
    def learn(self, service: str, status: str, plan: Dict, success: bool, duration: float):
        """学习经验"""
        self.experiences.append({
            "id": len(self.experiences)+1,
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "status": status,
            "analysis": plan.get("analysis", ""),
            "commands": plan.get("commands", []),
            "success": success,
            "duration": round(duration, 2)
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
        
        rate = self.stats["success"]/max(1, self.stats["total"])*100
        print(f"\n📝 学习: {service} -> {'✅成功' if success else '❌失败'} ({duration:.1f}s)")
        print(f"   全局成功率: {self.stats['success']}/{self.stats['total']} ({rate:.0f}%)")
    
    def heal(self):
        print("\n" + "=" * 60)
        state = self.observe()
        
        # 找出问题
        problems = [(svc, status) for svc, status in state.items() if status != "online"]
        
        if not problems:
            print("\n✅ 所有服务正常")
            return True
        
        print(f"\n🔍 发现 {len(problems)} 个问题")
        
        for service, status in problems:
            print(f"\n🎯 处理: {service} ({status})")
            
            # 思考方案
            plan = self.think_with_llm(service, status)
            print(f"💡 {plan.get('analysis', '')}")
            
            # 执行
            success, duration = self.execute(plan.get("commands", []), plan.get("verify", ""))
            
            # 学习
            self.learn(service, status, plan, success, duration)
        
        # 显示统计
        print("\n" + "=" * 60)
        print("📊 技能掌握情况:")
        for svc, stats in sorted(self.stats["by_service"].items()):
            rate = stats["success"]/max(stats["total"],1)*100
            bar = "█" * int(rate/10) + "░" * (10 - int(rate/10))
            print(f"   {svc}: [{bar}] {rate:.0f}% ({stats['success']}/{stats['total']})")
        print("=" * 60)
        return True

def main():
    agent = SimpleLearningAgent()
    
    # 运行多轮学习
    for i in range(3):
        print(f"\n{'🔄'*30}")
        print(f"第 {i+1} 轮学习")
        print(f"{'🔄'*30}")
        agent.heal()
        time.sleep(2)
    
    print("\n✅ 学习完成！Agent已记录所有经验")

if __name__ == "__main__":
    main()
