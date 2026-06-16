"""Calculator Agent 单元测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from agents.calculator_agent.agent_v4 import CalculatorAgentV4


class TestCalculatorAgentV4:
    """Calculator Agent V4 测试"""

    @pytest.fixture
    def agent(self, test_user_id):
        return CalculatorAgentV4(test_user_id)

    def test_basic_addition(self, agent):
        """测试加法"""
        result = agent.process("1 + 2")
        assert result["success"] is True
        assert "3" in result["response"] or "3" in str(result["output_content"])

    def test_subtraction(self, agent):
        """测试减法"""
        result = agent.process("10 - 3")
        assert result["success"] is True
        assert "7" in result["response"] or "7" in str(result["output_content"])

    def test_multiplication(self, agent):
        """测试乘法"""
        result = agent.process("5 * 6")
        assert result["success"] is True
        assert "30" in result["response"] or "30" in str(result["output_content"])

    def test_division(self, agent):
        """测试除法"""
        result = agent.process("15 / 3")
        assert result["success"] is True
        assert "5" in result["response"] or "5" in str(result["output_content"])
