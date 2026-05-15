"""数学技能测试"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

import pytest
from skills.math.add import skill as add_skill
from skills.math.multiply import skill as mul_skill
from skills.math.divide import skill as div_skill

class TestMathSkills:
    
    def test_add(self):
        result = add_skill.execute({'a': 5, 'b': 3})
        assert result['success'] == True
        assert result['result'] == 8
    
    def test_add_negative(self):
        result = add_skill.execute({'a': -5, 'b': 3})
        assert result['result'] == -2
    
    def test_multiply(self):
        result = mul_skill.execute({'a': 5, 'b': 3})
        assert result['result'] == 15
    
    def test_divide(self):
        result = div_skill.execute({'a': 10, 'b': 2})
        assert result['result'] == 5
    
    def test_divide_by_zero(self):
        result = div_skill.execute({'a': 10, 'b': 0})
        assert result['success'] == False
        assert 'error' in result

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
