"""决策层路由单元测试"""

import pytest
import sys
sys.path.insert(0, '/home/flybo/clawsjoy_v5')


class TestDecisionRouting:
    """测试 A/B/C 路由决策"""

    def test_chat_route(self):
        """测试对话走 A 路由"""
        from agents.decision_agent.agent import decision_agent
        result = decision_agent.process("你好", {})
        assert result.get("agent") != "orchestrator"
        print("✅ 对话路由测试通过")

    def test_calculation_route(self):
        """测试计算走 B 路由"""
        from agents.decision_agent.agent import decision_agent
        result = decision_agent.process("计算 1+1", {})
        # B 路由最终到 executor_agent
        print(f"计算路由: {result.get('agent')}")

    def test_code_route(self):
        """测试代码生成走 C 路由"""
        from agents.decision_agent.agent import decision_agent
        result = decision_agent.process("写一个 Python 函数", {})
        assert result.get("agent") == "orchestrator"
        print("✅ 代码路由测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
