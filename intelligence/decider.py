"""智能决策器 - 提供建议，不自动执行"""

import requests
from agent_core.brain_enhanced import brain

class SmartDecider:
    def __init__(self):
        self.suggestions = []
    
    def analyze(self):
        stats = brain.get_stats()
        
        suggestions = []
        if stats['success_rate'] < 0.8:
            suggestions.append("成功率偏低，建议增加训练数据")
        if stats['total_experiences'] < 30:
            suggestions.append("经验不足，建议多使用系统")
        
        return suggestions
    
    def suggest(self):
        suggestions = self.analyze()
        for s in suggestions:
            print(f"💡 建议: {s}")
        
        # 记录到大脑，但不自动执行
        brain.record_experience(
            agent="decider",
            action="生成建议",
            result={"suggestions": suggestions}
        )
        
        return suggestions

if __name__ == "__main__":
    decider = SmartDecider()
    decider.suggest()
