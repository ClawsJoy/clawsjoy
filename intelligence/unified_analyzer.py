#!/usr/bin/env python3
"""统一数据源分析器 - 整合所有数据源，给出改进建议"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

import json
import requests
from datetime import datetime
from lib.memory_simple import memory

class UnifiedAnalyzer:
    def __init__(self):
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        self.data_sources = {}
    
    def collect_all_data(self):
        """收集所有数据源"""
        sources = {
            'workflow_outcome': '任务执行结果',
            'error_knowledge': '错误修复知识库',
            'calibration_log': '时长校准记录',
            'quality_gate': '质量检验记录',
            'task_success_reference': '成功任务参考',
            'video_performance': '视频表现数据',
            'user_feedback': '用户反馈',
            'quality_issue': '质量问题',
            'solution': '解决方案',
            'parameter_formula': '参数公式'
        }
        
        for cat, desc in sources.items():
            items = memory.recall_all(category=cat)
            self.data_sources[cat] = {
                'desc': desc,
                'count': len(items),
                'samples': items[-3:] if items else []
            }
        
        return self.data_sources
    
    def analyze(self):
        """综合分析"""
        self.collect_all_data()
        
        # 构建分析 prompt
        summary = f"""数据源统计:
- 工作流记录: {self.data_sources['workflow_outcome']['count']}条
- 错误知识: {self.data_sources['error_knowledge']['count']}条
- 用户反馈: {self.data_sources['user_feedback']['count']}条
- 质量问题: {self.data_sources['quality_issue']['count']}条
- 成功参考: {self.data_sources['task_success_reference']['count']}条
- 视频表现: {self.data_sources['video_performance']['count']}条

关键用户反馈:
{chr(10).join(self.data_sources['user_feedback']['samples'])}

关键质量问题:
{chr(10).join(self.data_sources['quality_issue']['samples'])}

成功经验:
{chr(10).join(self.data_sources['task_success_reference']['samples'])}
"""
        
        prompt = f"""你是 ClawsJoy 系统分析师。基于以下数据，分析系统问题并提出改进建议。

{summary}

输出 JSON:
{{
    "summary": "整体评估",
    "critical_issues": ["关键问题1", "关键问题2"],
    "suggestions": {{
        "script": ["脚本优化建议"],
        "image": ["图片优化建议"],
        "video": ["视频优化建议"],
        "process": ["流程优化建议"]
    }},
    "priority_actions": ["优先行动1", "优先行动2"],
    "next_improvement": "下一步改进方向"
}}
"""
        
        try:
            resp = requests.post(self.ollama_url,
                                json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
                                timeout=90)
            result = resp.json()["response"]
            import re
            match = re.search(r'\{.*\}', result, re.DOTALL)
            if match:
                analysis = json.loads(match.group())
            else:
                analysis = {"error": "解析失败", "raw": result[:200]}
        except Exception as e:
            analysis = {"error": str(e)}
        
        # 存储分析结果
        memory.remember(
            f"统一分析|{datetime.now().isoformat()}|{analysis.get('summary', '')[:50]}",
            category='unified_analysis'
        )
        
        return analysis

if __name__ == "__main__":
    analyzer = UnifiedAnalyzer()
    result = analyzer.analyze()
    print(json.dumps(result, indent=2, ensure_ascii=False))
