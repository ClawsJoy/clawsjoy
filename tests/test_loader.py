"""技能加载器测试"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from lib.skill_loader_v3 import skill_loader

class TestSkillLoader:
    
    def test_list_skills(self):
        skills = skill_loader.list_skills()
        assert len(skills) > 0
        assert 'add' in skills
    
    def test_get_skill(self):
        skill = skill_loader.get_skill('add')
        assert skill is not None
    
    def test_execute(self):
        result = skill_loader.execute('add', {'a': 5, 'b': 3})
        assert result['success'] == True
        assert result['result'] == 8
    
    def test_categories(self):
        categories = skill_loader.get_categories()
        assert 'math' in categories
        assert categories['math']['count'] > 0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
