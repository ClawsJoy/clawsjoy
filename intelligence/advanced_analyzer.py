#!/usr/bin/env python3
"""高级分析器 - 趋势、根因、预测"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

import json
import requests
from datetime import datetime, timedelta
from lib.memory_simple import memory

class AdvancedAnalyzer:
    def __init__(self):
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
    
    def get_trend(self):
        """分析成功率趋势"""
        outcomes = memory.recall_all(category='workflow_outcome')
        if len(outcomes) < 10:
            return {"trend": "数据不足", "confidence": 0.3}
        
        # 计算最近趋势
        recent = outcomes[-10:]
        success_count = len([o for o in recent if '成功' in o])
        rate = success_count / len(recent) * 100
        
        if rate >= 80:
            trend = "上升"
        elif rate >= 50:
            trend = "稳定"
        else:
            trend = "下降"
        
        return {"trend": trend, "rate": rate, "sample_size": len(recent)}
    
    def root_cause_analysis(self):
        """根因分析"""
        outcomes = memory.recall_all(category='workflow_outcome')
        fails = [o for o in outcomes if '失败' in o]
        
        if not fails:
            return {"has_issues": False, "message": "无失败记录"}
        
        # 让 LLM 分析根因
        prompt = f"""分析以下失败记录，找出根本原因：

{fails[-5:]}

输出JSON: {{"root_causes": ["原因1", "原因2"], "suggestions": ["建议1", "建议2"]}}
"""
        try:
            resp = requests.post(self.ollama_url,
                                json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
                                timeout=60)
            result = resp.json()["response"]
            import re
            match = re.search(r'\{.*\}', result, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        
        return {"has_issues": True, "message": "分析失败"}
    
    def predict_next(self):
        """预测下一次成功率"""
        outcomes = memory.recall_all(category='workflow_outcome')
        if len(outcomes) < 5:
            return {"prediction": "数据不足"}
        
        recent = outcomes[-10:]
        success_rate = len([o for o in recent if '成功' in o]) / len(recent)
        
        # 简单预测
        prediction = success_rate * 100
        
        return {
            "prediction": f"{prediction:.0f}%",
            "confidence": min(0.9, len(recent) / 20),
            "next_expected": "成功" if prediction > 50 else "可能失败"
        }
    
    def generate_report(self):
        """生成分析报告"""
        trend = self.get_trend()
        prediction = self.predict_next()
        root_cause = self.root_cause_analysis()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "trend": trend,
            "prediction": prediction,
            "root_cause": root_cause,
            "recommendations": self._get_recommendations(trend)
        }
        
        # 存储报告
        memory.remember(
            f"分析报告|趋势:{trend['trend']}|预测:{prediction['prediction']}|时间:{datetime.now().isoformat()}",
            category="advanced_analysis"
        )
        
        return report
    
    def _get_recommendations(self, trend):
        if trend['trend'] == '下降':
            return ["检查最近变更", "增加测试", "回滚到稳定版本"]
        elif trend['trend'] == '稳定':
            return ["保持当前策略", "逐步优化"]
        else:
            return ["继续推进", "记录成功经验"]

if __name__ == "__main__":
    analyzer = AdvancedAnalyzer()
    report = analyzer.generate_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
