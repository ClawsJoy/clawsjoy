#!/usr/bin/env python3
"""会学习的智能体 - 集成学习模块"""

from core.agent.smart_agent import SmartAgent
from core.agent.learner import agent_learner


class LearningAgent(SmartAgent):
    """会学习的智能体"""
    
    VERSION = "2.0.0"
    
    def process(self, user_input: str, context=None):
        """处理请求并学习"""
        
        # 调用父类处理
        result = super().process(user_input, context)
        
        # 记录学习数据
        agent_learner.record_interaction(
            user_input=user_input,
            skill=result.get('skill', 'unknown'),
            params=result.get('params', {}),
            success=result.get('success', False),
            response=result.get('response', ''),
            llm_analyzed=result.get('llm_analyzed', False)
        )
        
        # 如果是成功的交互，更新模式
        if result.get('success') and result.get('skill'):
            agent_learner.update_patterns(user_input, result['skill'], True)
        
        return result
    
    def get_learning_report(self):
        """获取学习报告"""
        return agent_learner.get_report()


learning_agent = LearningAgent()


if __name__ == "__main__":
    print(f"学习型智能体 v{learning_agent.VERSION}")
    
    # 测试几次
    tests = [
        "生成一个中年男人的形象",
        "画一只猫咪",
        "每天提醒我喝水"
    ]
    
    for t in tests:
        result = learning_agent.process(t)
        print(f"\n{t}")
        print(f"  -> {result.get('response')[:50]}...")
        print(f"  -> 成功: {result.get('success')}")
    
    print("\n" + agent_learner.get_report())
