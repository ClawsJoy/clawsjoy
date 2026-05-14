#!/usr/bin/env python3
"""真正学习的运维 Agent - 观察→记忆→匹配→执行→反馈"""

import subprocess
import json
import re
import time
from pathlib import Path
from datetime import datetime

class TrueLearningAgent:
    def __init__(self):
        self.memory_file = Path("/mnt/d/clawsjoy/data/agent_brain.json")
        self.brain = self.load_brain()
    
    def load_brain(self):
        if self.memory_file.exists():
            with open(self.memory_file) as f:
                return json.load(f)
        return {
            "knowledge": [],
            "patterns": [],
            "confidence": {},
            "total_learnings": 0
        }
    
    def save_brain(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.brain, f, indent=2)
        print(f"🧠 大脑已保存 ({self.brain['total_learnings']} 次学习)")
    
    # ========== 1. 观察 ==========
    def observe(self):
        """观察系统状态"""
        state = {}
        
        # 观察 PM2 服务
        result = subprocess.run("pm2 list", shell=True, capture_output=True, text=True)
        output = result.stdout
        
        for svc in ["agent-api", "chat-api", "promo-api", "health-api"]:
            if svc in output:
                if "errored" in output:
                    state[svc] = {"status": "errored", "need_fix": True}
                elif "online" in output:
                    state[svc] = {"status": "online", "need_fix": False}
                else:
                    state[svc] = {"status": "unknown", "need_fix": True}
            else:
                state[svc] = {"status": "not_found", "need_fix": True}
        
        # 观察 Docker
        result = subprocess.run("docker ps", shell=True, capture_output=True, text=True)
        state["web"] = {
            "status": "running" if "clawsjoy-web" in result.stdout else "stopped",
            "need_fix": "clawsjoy-web" not in result.stdout
        }
        
        return state
    
    # ========== 2. 记忆 ==========
    def remember(self, situation, action, outcome):
        """记忆经验"""
        experience = {
            "id": len(self.brain["knowledge"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "situation": situation,
            "action": action,
            "outcome": outcome,
            "success": outcome.get("success", False)
        }
        
        self.brain["knowledge"].append(experience)
        
        # 更新置信度
        action_name = action.get("name", "unknown")
        if action_name not in self.brain["confidence"]:
            self.brain["confidence"][action_name] = {"total": 0, "success": 0}
        
        self.brain["confidence"][action_name]["total"] += 1
        if outcome.get("success"):
            self.brain["confidence"][action_name]["success"] += 1
        
        self.brain["total_learnings"] += 1
        self.save_brain()
        
        print(f"📝 记住经验 #{experience['id']}: {action_name} -> {'成功' if outcome['success'] else '失败'}")
    
    # ========== 3. 匹配 ==========
    def match(self, symptom):
        """匹配已知模式"""
        # 症状到解决方案的映射库
        knowledge_base = {
            "agent-api.*(errored|not_found)": {
                "name": "fix_agent_api",
                "cmd": "cd /mnt/d/clawsjoy/bin && pm2 start agent_api.py --name agent-api -- --port 18103 2>/dev/null || pm2 restart agent-api",
                "verify": "pm2 list | grep agent-api | grep -q online"
            },
            "chat-api.*(errored|not_found)": {
                "name": "fix_chat_api",
                "cmd": "cd /mnt/d/clawsjoy/bin && pm2 start chat_api.py --name chat-api -- --port 18109 2>/dev/null || pm2 restart chat-api",
                "verify": "pm2 list | grep chat-api | grep -q online"
            },
            "promo-api.*(errored|not_found)": {
                "name": "fix_promo_api",
                "cmd": "cd /mnt/d/clawsjoy/bin && pm2 start promo_api.py --name promo-api -- --port 8108 2>/dev/null || pm2 restart promo-api",
                "verify": "pm2 list | grep promo-api | grep -q online"
            },
            "web.*stopped": {
                "name": "fix_web",
                "cmd": "cd /mnt/d/clawsjoy && docker-compose up -d web 2>/dev/null || docker start clawsjoy-web",
                "verify": "docker ps | grep -q clawsjoy-web"
            }
        }
        
        for pattern, action in knowledge_base.items():
            if re.search(pattern, symptom, re.IGNORECASE):
                # 从记忆中获取该动作的历史成功率
                confidence = self.brain["confidence"].get(action["name"], {"total": 0, "success": 0})
                rate = confidence["success"] / max(confidence["total"], 1)
                action["confidence"] = rate
                action["history"] = f"{confidence['success']}/{confidence['total']}"
                return action
        
        return None
    
    # ========== 4. 执行 ==========
    def execute(self, action):
        """执行动作"""
        print(f"🔧 执行: {action['name']} (历史成功率: {action.get('confidence', 0)*100:.0f}% - {action.get('history', '0/0')})")
        
        start_time = time.time()
        result = subprocess.run(action["cmd"], shell=True, capture_output=True, text=True)
        duration = time.time() - start_time
        
        success = result.returncode == 0
        
        # 验证
        if success:
            time.sleep(2)
            verify = subprocess.run(action["verify"], shell=True)
            success = verify.returncode == 0
        
        return {
            "success": success,
            "duration": round(duration, 2),
            "output": result.stdout[:200] if result.stdout else "",
            "action": action["name"]
        }
    
    # ========== 5. 反馈学习 ==========
    def learn_from_outcome(self, action, result, situation):
        """从结果中学习"""
        # 分析学习
        if result["success"]:
            print(f"✅ {action['name']} 成功 (耗时 {result['duration']}秒)")
            # 强化这个模式
            self._reinforce_pattern(situation, action["name"])
        else:
            print(f"❌ {action['name']} 失败")
            # 记录失败模式
            self._record_failure(situation, action["name"], result.get("output", ""))
        
        # 记忆经验
        self.remember(situation, action, result)
    
    def _reinforce_pattern(self, situation, action_name):
        """强化成功模式"""
        # 提取症状关键词
        symptom = self._extract_symptom(situation)
        
        # 查找已有模式
        for p in self.brain["patterns"]:
            if p["symptom"] == symptom and p["action"] == action_name:
                p["success_count"] += 1
                p["last_success"] = datetime.now().isoformat()
                return
        
        # 新模式
        self.brain["patterns"].append({
            "symptom": symptom,
            "action": action_name,
            "success_count": 1,
            "learned_at": datetime.now().isoformat()
        })
        print(f"🎯 学到新模式: {symptom} -> {action_name}")
    
    def _record_failure(self, situation, action_name, error_msg):
        """记录失败模式"""
        symptom = self._extract_symptom(situation)
        
        # 记录失败
        failure = {
            "symptom": symptom,
            "action": action_name,
            "error": error_msg[:100],
            "time": datetime.now().isoformat()
        }
        
        if "failures" not in self.brain:
            self.brain["failures"] = []
        self.brain["failures"].append(failure)
        
        # 只保留最近 50 条失败
        if len(self.brain["failures"]) > 50:
            self.brain["failures"] = self.brain["failures"][-50:]
        
        print(f"⚠️ 记录失败: {symptom} -> {action_name}")
    
    def _extract_symptom(self, situation):
        """从状态中提取症状"""
        for svc, info in situation.items():
            if info.get("need_fix"):
                return f"{svc}.{info.get('status', 'unknown')}"
        return "unknown"
    
    # ========== 主循环 ==========
    def heal(self):
        """治愈主循环"""
        print("=" * 60)
        print("🩺 学习型运维 Agent 启动")
        print(f"🧠 已有 {self.brain['total_learnings']} 次学习经验")
        print("=" * 60)
        
        # 1. 观察
        print("\n👁️ 观察中...")
        state = self.observe()
        
        # 2. 找出问题
        problems = []
        for svc, info in state.items():
            if info.get("need_fix"):
                problems.append(f"{svc}.{info['status']}")
                print(f"   ⚠️ {svc}: {info['status']}")
        
        if not problems:
            print("\n✅ 所有服务正常，无需修复")
            return True
        
        print(f"\n🔍 发现 {len(problems)} 个问题")
        
        # 3. 匹配并执行
        for problem in problems:
            print(f"\n🎯 处理: {problem}")
            
            # 匹配解决方案
            action = self.match(problem)
            
            if not action:
                print(f"   ❌ 未找到解决方案")
                continue
            
            # 执行
            result = self.execute(action)
            
            # 反馈学习
            self.learn_from_outcome(action, result, state)
        
        # 4. 总结
        print("\n" + "=" * 60)
        print("📊 学习总结")
        
        # 显示技能表现
        print("\n技能掌握情况:")
        for skill, stats in sorted(self.brain["confidence"].items(), key=lambda x: x[1]["total"], reverse=True):
            rate = stats["success"] / max(stats["total"], 1) * 100
            bar = "█" * int(rate / 10) + "░" * (10 - int(rate / 10))
            print(f"   {skill}: [{bar}] {rate:.0f}% ({stats['success']}/{stats['total']})")
        
        # 显示学到的模式
        if self.brain["patterns"]:
            print(f"\n🎯 学到 {len(self.brain['patterns'])} 个模式:")
            for p in self.brain["patterns"][-3:]:
                print(f"   - {p['symptom']} -> {p['action']} (成功 {p['success_count']} 次)")
        
        print("=" * 60)
        return True

if __name__ == "__main__":
    agent = TrueLearningAgent()
    
    # 连续运行 3 次，让它学习
    for i in range(3):
        print(f"\n🔄 第 {i+1} 轮学习")
        agent.heal()
        time.sleep(2)
    
    print("\n✅ 学习完成！Agent 现在会越来越聪明")
