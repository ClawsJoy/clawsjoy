from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
"""分析师 Agent - 分析翻译质量，提供学习建议"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List

from core.lib.smart_adapter import smart_adapter

class AnalystAgent:
    """分析师 Agent - 负责分析和优化翻译学习"""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self._load_data()
        print(f"📊 分析师 Agent v{self.VERSION} 已启动")
    
    def _load_data(self):
        """加载翻译数据"""
        memory_file = Path(f"{get_data_root()}/translate_memory.json")
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}
        
        self.translation_cache = self.data.get('translation_cache', {})
        self.success_patterns = self.data.get('success_patterns', [])
        self.failed_patterns = self.data.get('failed_patterns', [])
    
    def analyze(self) -> Dict:
        """分析翻译质量，生成学习建议"""
        
        # 1. 高频未命中分析
        all_queries = [p['query'] for p in self.success_patterns] + [p['query'] for p in self.failed_patterns]
        query_counts = Counter(all_queries)
        
        # 高频但不在缓存中的查询
        high_freq_missing = []
        for query, count in query_counts.items():
            if count > 2 and query not in self.translation_cache:
                high_freq_missing.append({"query": query, "count": count})
        
        # 2. 成功率分析
        total_success = len(self.success_patterns)
        total_failed = len(self.failed_patterns)
        success_rate = total_success / (total_success + total_failed) if (total_success + total_failed) > 0 else 0
        
        # 3. 失败模式分析
        failed_queries = [p['query'] for p in self.failed_patterns]
        failed_patterns = Counter(failed_queries).most_common(5)
        
        # 4. 生成学习建议
        suggestions = []
        
        for item in high_freq_missing[:10]:
            suggestions.append({
                "type": "add_to_cache",
                "query": item['query'],
                "priority": item['count'],
                "suggestion": f"建议将 '{item['query']}' 加入翻译缓存"
            })
        
        for query, count in failed_patterns:
            suggestions.append({
                "type": "review_translation",
                "query": query,
                "priority": count,
                "suggestion": f"翻译 '{query}' 失败 {count} 次，建议人工审核"
            })
        
        # 5. 生成学习报告
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_success": total_success,
                "total_failed": total_failed,
                "success_rate": round(success_rate, 3),
                "cache_size": len(self.translation_cache),
                "high_freq_missing": len(high_freq_missing)
            },
            "suggestions": suggestions[:10],
            "failed_patterns": failed_patterns[:5]
        }
    
    def generate_learning_batch(self) -> List[Dict]:
        """生成批量学习数据"""
        analysis = self.analyze()
        learning_batch = []
        
        for sug in analysis.get('suggestions', []):
            if sug['type'] == 'add_to_cache':
                learning_batch.append({
                    "action": "cache_translation",
                    "query": sug['query'],
                    "priority": sug['priority']
                })
        
        return learning_batch
    
    def get_weekly_report(self) -> Dict:
        """生成周报"""
        # 按天统计
        daily_stats = defaultdict(lambda: {"success": 0, "failed": 0})
        
        for p in self.success_patterns:
            day = p['timestamp'][:10]
            daily_stats[day]['success'] += 1
        
        for p in self.failed_patterns:
            day = p['timestamp'][:10]
            daily_stats[day]['failed'] += 1
        
        return {
            "period": "last_7_days",
            "daily_stats": dict(daily_stats),
            "total_cache": len(self.translation_cache),
            "success_rate": self.analyze()['summary']['success_rate']
        }


analyst_agent = AnalystAgent()

    def analyze_anomaly(self, anomaly: Dict) -> Dict:
        """分析异常，给出建议"""
        analysis = {
            "anomaly_id": anomaly.get("id", "unknown"),
            "type": anomaly.get("type", "unknown"),
            "severity": "medium",
            "root_cause": "unknown",
            "recommendations": []
        }
        
        if anomaly.get("type") == "vector_mismatch":
            diff = anomaly.get("dif", 0)
            if abs(diff) > 10:
                analysis["severity"] = "high"
                analysis["root_cause"] = "数据丢失或重复插入"
                analysis["recommendations"].append({
                    "action": "reindex_vector",
                    "description": "重建向量索引",
                    "priority": "high"
                })
            else:
                analysis["severity"] = "medium"
                analysis["root_cause"] = "翻译不精准导致匹配失败"
                analysis["recommendations"].append({
                    "action": "optimize_translation",
                    "description": "语言大师优化翻译",
                    "priority": "medium"
                })
        
        return analysis
    
    def request_meeting(self, anomaly: Dict, analysis: Dict) -> Dict:
        """请求召开会议"""
        from core.agents.meeting_system import meeting_system
        from core.agents.meeting_system import MeetingLevel
        
        level = MeetingLevel.WARNING
        if analysis.get("severity") == "high":
            level = MeetingLevel.CRITICAL
        
        meeting = meeting_system.trigger_meeting(
            issue=anomaly,
            level=level
        )
        
        # 记录分析师的分析结果
        meeting_system.record_discussion(
            meeting_id=meeting["id"],
            speaker="analyst",
            content=f"分析结果: {analysis.get('root_cause')}, 建议: {analysis.get('recommendations')}"
        )
        
        return meeting
