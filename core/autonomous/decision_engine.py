#!/usr/bin/env python3
"""Decision Engine - Decision Engine 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class DecisionEngine:
    def __init__(self):
        self.cycle_count = 0
        self.decisions = []

    def sense(self) -> Dict:
        """感知：收集系统状态"""
        # 获取技能状态
        skill_result = subprocess.run(
            ['curl', '-s', 'http://localhost:5002/api/skills'],
            capture_output=True, text=True
        )
        import json
        skills = json.loads(skill_result.stdout) if skill_result.stdout else {}

        # 获取健康状态
        health_result = subprocess.run(
            ['curl', '-s', 'http://localhost:5002/api/health'],
            capture_output=True, text=True
        )

        return {
            "skills_count": skills.get('total', 0),
            "health": health_result.stdout,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze(self, state: Dict) -> Dict:
        """分析：找出问题"""
        issues = []

        if state['skills_count'] < 150:
            issues.append("skills_count_low")

        if 'ok' not in state.get('health', ''):
            issues.append("health_check_failed")

        return {
            "issues": issues,
            "severity": "high" if issues else "normal",
            "timestamp": datetime.now().isoformat()
        }
    
    def decide(self, analysis: Dict) -> Dict:
        """决策：决定做什么"""
        if analysis['issues']:
            return {
                "action": "fix_issues",
                "target": analysis['issues'][0],
                "priority": "high"
            }
        else:
            return {
                "action": "optimize",
                "target": "system_performance",
                "priority": "low"
            }
    
    def act(self, decision: Dict) -> Dict:
        """行动：执行决策"""
        if decision['action'] == 'fix_issues':
            if decision['target'] == 'skills_count_low':
                # 尝试恢复技能
                result = subprocess.run(
                    ['curl', '-s', '-X', 'POST', 'http://localhost:5002/api/knowledge/sync'],
                    capture_output=True, text=True
                )
                return {"success": True, "result": "技能同步已触发", "output": result.stdout}

        elif decision['action'] == 'optimize':
            return {"success": True, "result": "系统优化中", "action": "optimize"}

        return {"success": False, "result": "未知决策"}
    
    def learn(self, action_result: Dict):
        """学习：记录并改进"""
        self.decisions.append({
            "timestamp": datetime.now().isoformat(),
            "action": action_result,
            "cycle": self.cycle_count
        })

        # 保存到永久记忆
        memory_file = Path(f"{config_helper.get_data_root()}/autonomous/decisions.json")
        memory_file.parent.mkdir(exist_ok=True)
        with open(memory_file, 'w') as f:
            json.dump(self.decisions, f, indent=2)
    
    def run_cycle(self) -> Dict:
        """执行一个完整闭环"""
        self.cycle_count += 1
        print(f"\n🔄 闭环 #{self.cycle_count}")

        # 感知
        state = self.sense()
        print(f"  📡 感知: 技能数={state['skills_count']}")

        # 分析
        analysis = self.analyze(state)
        print(f"  🔍 分析: 问题={analysis['issues']}")

        # 决策
        decision = self.decide(analysis)
        print(f"  🎯 决策: {decision['action']} -> {decision.get('target', 'none')}")

        # 行动
        result = self.act(decision)
        print(f"  ⚡ 行动: {result.get('result')}")

        # 学习
        self.learn(result)
        print(f"  📚 学习: 已记录，总决策数={len(self.decisions)}")

        return result

engine = DecisionEngine()
