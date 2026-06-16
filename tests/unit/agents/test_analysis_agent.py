"""Analysis Agent 单元测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from agents.analysis_agent.agent_v4 import AnalysisAgentV4 as AnalysisAgentV4


class TestAnalysisAgentV4:
    """Analysis Agent V4 测试"""

    @pytest.fixture
    def agent(self, test_user_id):
        return AnalysisAgentV4(test_user_id)

    def test_analysis_without_data(self, agent):
        """测试无数据时的分析"""
        result = agent.process("分析销售数据")
        assert result["success"] is True
        assert "数据" in result["response"] or "框架" in result["response"]

    def test_extract_data(self, agent):
        """测试数据提取"""
        text = "数据：123, 456, 789"
        data = agent._extract_data(text)
        assert data is not None

    def test_identify_analysis_type(self, agent):
        """测试分析类型识别"""
        assert agent._identify_analysis_type("销售数据分析") == "sales"
        assert agent._identify_analysis_type("用户行为分析") == "user"
        assert agent._identify_analysis_type("财务报告") == "financial"
        assert agent._identify_analysis_type("普通问题") == "default"
