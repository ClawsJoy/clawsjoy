#!/usr/bin/env python3
"""数据分析 Agent - 系统分析和优化建议"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from intelligence.unified_analyzer import UnifiedAnalyzer
from lib.agent_registry import agent_registry
from lib.memory_simple import memory
from lib.file_exchange import file_exchange


class AnalysisAgent(BaseAgent):
    """数据分析 Agent - 分析系统数据，给出优化建议"""
    
    name = "analysis_agent"
    description = "数据分析师 - 分析系统数据，提供优化建议"
    version = "2.0.0"
    type = "core"

    capabilities = [
        {"name": "data_analysis", "description": "分析系统数据源，识别问题和机会"},
        {"name": "optimization_suggestion", "description": "给出可执行的优化建议"},
        {"name": "health_assessment", "description": "评估系统健康度"},
        {"name": "anomaly_detection", "description": "检测异常模式和性能瓶颈"}
    ]

    def __init__(self):
        super().__init__(agent_id="analysis_agent")
        self.analyzer = UnifiedAnalyzer()
        self.remember("数据分析 Agent 已启动，监控所有数据源", shared=True)
        print("📊 数据分析 Agent 初始化完成")
    
    def analyze_all_sources(self) -> Dict:
        """分析所有数据源"""
        return self.analyzer.analyze()
    
    def get_insights(self) -> List[Dict]:
        """获取分析洞察"""
        report = self.analyze_all_sources()
        insights = []
        
        for suggestion in report.get('suggestions', []):
            insights.append({
                "type": suggestion.get("level", "info"),
                "message": suggestion.get("message", ""),
                "action": suggestion.get("action", "review")
            })
        
        for insight in report.get('llm_insights', []):
            insights.append({
                "type": "llm",
                "message": insight,
                "action": "consider"
            })
        
        return insights
    
    def send_suggestions(self, target_agent: str = "decision_agent"):
        """发送建议到指定 Agent"""
        insights = self.get_insights()
        
        if not insights:
            print("暂无新建议")
            return
        
        file_exchange.send(
            to_agent=target_agent,
            data={
                "from": self.name,
                "action": "optimization_suggestion",
                "data": {
                    "timestamp": datetime.now().isoformat(),
                    "insights": insights,
                    "health_score": self.analyze_all_sources().get("summary", {}).get("health_score", 0)
                }
            }
        )
        print(f"📨 已发送 {len(insights)} 条建议到 {target_agent}")
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理用户请求"""
        print(f"分析请求: {user_input[:50]}...")
        
        if "健康" in user_input or "health" in user_input.lower():
            report = self.analyze_all_sources()
            return {
                "success": True,
                "response": f"系统健康度: {report['summary']['health_score']}/100，{report['suggestions'][0]['message'] if report['suggestions'] else '运行良好'}",
                "report": report
            }
        
        if "建议" in user_input or "suggest" in user_input.lower():
            insights = self.get_insights()
            return {
                "success": True,
                "response": f"发现 {len(insights)} 条优化建议",
                "insights": insights
            }
        
        return {
            "success": True,
            "response": "我可以分析系统健康度和提供优化建议。请说'健康检查'或'给我建议'"
        }


analysis_agent = AnalysisAgent()


if __name__ == "__main__":
    print(f"数据分析 Agent v{analysis_agent.version}")
    
    # 注册到注册中心
    agent_registry.register("analysis_agent", {
        "name": "数据分析师",
        "type": "core",
        "version": analysis_agent.version,
        "capabilities": [c["name"] for c in analysis_agent.capabilities]
    })
    print("✅ 已注册到 agent_registry")
    
    # 测试分析
    result = analysis_agent.analyze_all_sources()
    print(f"健康度: {result['summary']['health_score']}/100")
    print(f"建议数: {len(result.get('suggestions', []))}")
