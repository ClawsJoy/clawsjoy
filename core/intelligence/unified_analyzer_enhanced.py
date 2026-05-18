#!/usr/bin/env python3
"""统一分析器增强版 - 覆盖所有数据源"""

import sys
from lib.llm_config import llm_config
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
import json
import requests
from datetime import datetime
from lib.memory_simple import memory
from lib.memory_vector import vector_memory

class UnifiedAnalyzerEnhanced:
    def __init__(self):
        self.ollama_url = llm_config.get_ollama_url()
        self.data_sources = {}

    def collect_all_data(self):
        """收集所有数据源（完整版）"""
        sources = {
            # 核心工作流
            'workflow_outcome': '任务执行结果',
            'error_knowledge': '错误修复知识库',
            'calibration_log': '时长校准记录',
            'quality_gate': '质量检验记录',
            'task_success_reference': '成功任务参考',
            # 视频相关
            'video_performance': '视频表现数据',
            'video_metadata': '视频元数据',
            'video_uploads': '视频上传记录',
            'channel_stats': '频道统计数据',
            # 用户反馈
            'user_feedback': '用户反馈',
            'user_satisfaction': '用户满意度',
            'task_failure': '任务失败记录',
            # 质量问题
            'quality_issue': '质量问题',
            'solution': '解决方案',
            'parameter_formula': '参数公式',
            # 智能监控
            'success_monitoring': '成功率监控',
            'system_monitoring': '系统监控',
            'auto_tuning': '自动调优',
            'trend_analysis': '趋势分析',
            'performance_predictions': '性能预测',
            # 大脑学习
            'ai_learned': 'AI学习记录',
            'self_review_log': '自评日志',
            'executed_decisions': '执行决策',
            'intelligence_analysis': '智能分析',
        }

        for cat, desc in sources.items():
            items = memory.recall_all(category=cat)
            self.data_sources[cat] = {
                'desc': desc,
                'count': len(items),
                'samples': items[-3:] if items else []
            }
        
        # 添加向量记忆数据
        try:
            stats = vector_memory.get_stats()
            self.data_sources['vector_memory'] = {
                'desc': '向量语义记忆',
                'count': stats['total_vectors'],
                'samples': vector_memory.list_all(limit=5)
            }
        except:
            pass
        
        # 添加系统性能数据
        try:
            import psutil
            self.data_sources['system_performance'] = {
                'desc': '系统性能指标',
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        except:
            pass
        
        return self.data_sources

    def calculate_success_rate(self):
        """计算成功率"""
        outcomes = memory.recall_all(category='workflow_outcome')
        if not outcomes:
            return 0
        recent = outcomes[-20:]
        success = len([o for o in recent if '成功' in o])
        return success / len(recent) * 100

    def analyze(self):
        """综合分析"""
        self.collect_all_data()
        success_rate = self.calculate_success_rate()
        
        # 构建分析报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "success_rate": success_rate,
            "data_summary": {},
            "insights": [],
            "recommendations": []
        }
        
        for cat, info in self.data_sources.items():
            if isinstance(info, dict) and 'count' in info:
                report["data_summary"][cat] = info['count']
        
        # 生成洞察
        if success_rate < 50:
            report["insights"].append(f"成功率偏低 ({success_rate:.0f}%)，需要优化")
            report["recommendations"].append("建议检查失败任务并优化工作流")
        
        if len(self.data_sources.get('error_knowledge', {}).get('samples', [])) > 0:
            report["insights"].append("错误知识库有内容，可自动修复")
        
        # 存储报告
        memory.remember(
            f"增强分析|{datetime.now().isoformat()}|成功率:{success_rate:.0f}%",
            category="enhanced_analysis"
        )
        
        return report

if __name__ == "__main__":
    analyzer = UnifiedAnalyzerEnhanced()
    result = analyzer.analyze()
    print(json.dumps(result, indent=2, ensure_ascii=False))
