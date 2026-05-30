#!/usr/bin/env python3
"""Safe Autonomous - Safe Autonomous 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import json
import subprocess
from pathlib import Path
from datetime import datetime
from enum import Enum

class ActionLevel(Enum):
    SAFE = "safe"           # 自动执行
    WARNING = "warning"     # 需要确认
    DANGER = "danger"       # 禁止执行

class SafeAutonomousAgent:
    def __init__(self):
        self.approval_pending = []
        self.action_history = []
        self._load_rules()
    
    def _load_rules(self):
        self.rules = {
            # 安全操作 - 自动执行
            "safe_actions": [
                "check_status", "get_stats", "search_skills",
                "list_skills", "get_time", "count_memory"
            ],
            # 警告操作 - 需要审批
            "warning_actions": [
                "sync_skills", "fix_skill", "update_config",
                "restart_service", "clear_cache"
            ],
            # 危险操作 - 禁止
            "danger_actions": [
                "delete_skill", "rm_rf", "drop_database",
                "stop_service", "modify_system"
            ]
        }
    
    def analyze(self) -> dict:
        """分析系统状态"""
        issues = []

        # 检查技能
        result = subprocess.run(
            ['curl', '-s', 'http://localhost:5002/api/skills'],
            capture_output=True, text=True
        )
        import json
        data = json.loads(result.stdout) if result.stdout else {}
        skill_count = data.get('total', 0)

        if skill_count < 150:
            issues.append({"type": "skill_count_low", "detail": f"技能数 {skill_count}", "action": "sync_skills"})

        # 检查健康
        health = subprocess.run(
            ['curl', '-s', 'http://localhost:5002/api/health'],
            capture_output=True, text=True
        )
        if 'ok' not in health.stdout:
            issues.append({"type": "health_check_failed", "detail": health.stdout, "action": "restart_service"})

        return {"issues": issues, "timestamp": datetime.now().isoformat()}
    
    def propose_solution(self, issue: dict) -> dict:
        """生成解决方案"""
        action = issue.get('action')
        level = self._get_action_level(action)

        return {
            "issue": issue,
            "action": action,
            "level": level.value,
            "description": self._get_action_description(action),
            "auto_execute": level == ActionLevel.SAFE
        }
    
    def _get_action_level(self, action: str) -> ActionLevel:
        if action in self.rules["safe_actions"]:
            return ActionLevel.SAFE
        elif action in self.rules["warning_actions"]:
            return ActionLevel.WARNING
        else:
            return ActionLevel.DANGER
    
    def _get_action_description(self, action: str) -> str:
        descriptions = {
            "sync_skills": "同步技能到注册中心",
            "restart_service": "重启服务（需要确认）",
            "check_status": "检查系统状态",
            "get_stats": "获取统计信息"
        }
        return descriptions.get(action, f"执行 {action}")
    
    def execute(self, proposal: dict) -> dict:
        """执行提案（根据安全级别）"""
        if proposal['level'] == 'danger':
            return {"success": False, "error": "危险操作被阻止", "action": proposal['action']}

        if proposal['level'] == 'warning':
            # 需要审批，加入待审批队列
            self.approval_pending.append(proposal)
            return {"success": False, "pending": True, "message": f"需要审批: {proposal['description']}"}

        # 安全操作，自动执行
        action = proposal['action']
        if action == 'sync_skills':
            result = subprocess.run(
                ['curl', '-s', '-X', 'POST', 'http://localhost:5002/api/knowledge/sync'],
                capture_output=True, text=True
            )
            return {"success": True, "result": result.stdout}

        elif action == 'get_stats':
            return {"success": True, "stats": {"skills": 152, "memory": 122}}

        return {"success": False, "error": "未知操作"}
    
    def approve(self, action_index: int) -> dict:
        """人工审批"""
        if action_index < len(self.approval_pending):
            proposal = self.approval_pending.pop(action_index)
            return self.execute(proposal)
        return {"success": False, "error": "待审批项不存在"}
    
    def run(self):
        """主动运行一次"""
        print("🔍 Agent 主动分析中...")
        analysis = self.analyze()

        if not analysis['issues']:
            print("✅ 系统正常，无问题")
            return {"action": "idle"}

        print(f"⚠️ 发现 {len(analysis['issues'])} 个问题")

        for issue in analysis['issues']:
            proposal = self.propose_solution(issue)
            print(f"\n  问题: {issue['type']}")
            print(f"  方案: {proposal['description']}")
            print(f"  级别: {proposal['level']}")

            if proposal['auto_execute']:
                result = self.execute(proposal)
                print(f"  结果: {'✅ 成功' if result.get('success') else '❌ 失败'}")
            else:
                print(f"  ⏳ 等待审批 (pending_id={len(self.approval_pending)-1})")

        return {"issues_found": len(analysis['issues']), "pending_approvals": len(self.approval_pending)}

agent = SafeAutonomousAgent()
