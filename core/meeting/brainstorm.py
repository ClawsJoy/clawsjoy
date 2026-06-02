#!/usr/bin/env python3
"""Brainstorm - Brainstorm 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path


class BrainstormEngine:
    """头脑风暴引擎 - 智能会议"""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.meeting_log = Path(f"{config_helper.get_data_root()}/meeting_records.json")
        self.participants = [
            "analyst",      # 分析师 - 提供数据洞察
            "security",     # 安全员 - 风险评估
            "decision",     # 决策师 - 最终拍板
            "orchestrator", # 编排器 - 执行规划
            "self_healer"   # 自愈系统 - 修复建议
        ]
        print(f"🧠 头脑风暴引擎 v{self.VERSION} 已启动")
        print(f"   参会者: {', '.join(self.participants)}")
    
    def call_meeting(self, topic: str, context: Dict) -> Dict:
        """召开会议"""
        print(f"\n📢 召开会议: {topic}")
        print("=" * 50)

        meeting = {
            "id": f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "topic": topic,
            "time": datetime.now().isoformat(),
            "participants": self.participants,
            "discussions": [],
            "conclusions": [],
            "actions": []
        }

        # 1. 分析师发言 - 数据洞察
        analyst_view = self._analyst_speech(topic, context)
        meeting["discussions"].append({"speaker": "analyst", "content": analyst_view})
        print(f"📊 [分析师] {analyst_view.get('summary', '')[:100]}...")

        # 2. 安全员发言 - 风险评估
        security_view = self._security_speech(topic, context)
        meeting["discussions"].append({"speaker": "security", "content": security_view})
        print(f"🔒 [安全员] {security_view.get('summary', '')[:100]}...")

        # 3. 头脑风暴 - 讨论阶段
        brainstorm_results = self._brainstorm(topic, analyst_view, security_view)
        meeting["discussions"].extend(brainstorm_results)

        # 4. 得出结论
        conclusion = self._conclude(meeting["discussions"])
        meeting["conclusions"] = conclusion

        # 5. 生成行动计划
        actions = self._plan_actions(conclusion, context)
        meeting["actions"] = actions

        # 记录会议
        self._save_meeting(meeting)

        print("=" * 50)
        print(f"✅ 会议结束，生成 {len(actions)} 个行动项")

        return meeting
    
    def _analyst_speech(self, topic: str, context: Dict) -> Dict:
        """分析师发言"""
        health = context.get("health_score", 85)
        return {
            "speaker": "analyst",
            "summary": f"系统健康度 {health}/100",
            "data_insights": context.get("suggestions", []),
            "recommendations": self._generate_recommendations(health)
        }
    
    def _generate_recommendations(self, health: int) -> List:
        """生成建议"""
        recs = []
        if health < 70:
            recs.append("需要优化系统性能")
        if health < 50:
            recs.append("紧急修复故障")
        return recs
    
    def _security_speech(self, topic: str, context: Dict) -> Dict:
        """安全员发言"""
        risk_score = context.get("risk_score", 0)
        return {
            "speaker": "security",
            "summary": f"风险评分 {risk_score}/100",
            "risk_level": "high" if risk_score > 70 else "medium" if risk_score > 40 else "low",
            "concerns": ["需要审计" if risk_score > 50 else None]
        }
    
    def _brainstorm(self, topic: str, analyst_view: Dict, security_view: Dict) -> List:
        """头脑风暴"""
        discussions = []

        # 决策师发言
        discussions.append({
            "speaker": "decision",
            "content": f"基于分析师建议: {analyst_view.get('recommendations', [])}"
        })

        # 编排器发言
        discussions.append({
            "speaker": "orchestrator",
            "content": "可以编排以下任务..." if analyst_view.get('recommendations') else "等待决策"
        })

        # 自愈系统发言
        if analyst_view.get('data_insights'):
            discussions.append({
                "speaker": "self_healer",
                "content": "检测到问题，可尝试自动修复"
            })

        return discussions
    
    def _conclude(self, discussions: List) -> List:
        """得出结论"""
        conclusions = []
        for d in discussions:
            if "修复" in str(d) or "优化" in str(d):
                conclusions.append(d)
        return conclusions[:5]
    
    def _plan_actions(self, conclusions: List, context: Dict) -> List:
        """生成行动计划"""
        actions = []
        for c in conclusions:
            actions.append({
                "action": c.get("content", "待定"),
                "priority": "high" if "紧急" in str(c) else "normal",
                "assigned_to": c.get("speaker", "decision")
            })
        return actions
    
    def _save_meeting(self, meeting: Dict):
        """保存会议记录"""
        import json
        records = []
        if self.meeting_log.exists():
            try:
                with open(self.meeting_log, 'r') as f:
                    records = json.load(f)
                    if not isinstance(records, list):
                        records = []
            except:
                records = []
        records.append(meeting)
        with open(self.meeting_log, 'w') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)


brainstorm_engine = BrainstormEngine()
