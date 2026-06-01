"""技能矩阵引擎单元测试"""

import pytest
from engine.skill_matrix.core import skill_matrix_engine

class TestSkillMatrixEngine:
    """技能矩阵引擎测试"""
    
    def test_get_stats(self):
        """测试统计信息"""
        stats = skill_matrix_engine.get_stats()
        assert 'skills' in stats
        assert stats['skills'] > 0
    
    def test_search_code(self):
        """测试代码技能搜索"""
        results = skill_matrix_engine.search("写代码", top_k=3)
        assert len(results) > 0
        assert any('code' in r.get('name', '').lower() for r in results)
    
    def test_search_weather(self):
        """测试天气技能搜索"""
        results = skill_matrix_engine.search("天气", top_k=3)
        assert len(results) > 0
    
    def test_process(self):
        """测试处理接口"""
        result = skill_matrix_engine.process("测试查询")
        assert result is not None
