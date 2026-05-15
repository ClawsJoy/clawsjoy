"""核心模块测试"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

class TestCore:
    
    def test_skill_loader(self):
        from lib.skill_loader_v3 import skill_loader
        assert len(skill_loader.list_skills()) > 0
        assert 'add' in skill_loader.list_skills()
    
    def test_math_add(self):
        from skills.math.add import skill
        result = skill.execute({'a': 5, 'b': 3})
        assert result['result'] == 8
    
    def test_do_anything(self):
        from skills.core.do_anything import skill
        result = skill.execute({'goal': '10 加 20'})
        assert result['success'] == True
        val = result['results'][0]['result'].get('result')
        assert val == 30
    
    def test_service_registry(self):
        from lib.service_registry_v2 import service_registry
        assert 'gateway' in service_registry.list_all()
    
    def test_skill_registry(self):
        from lib.skill_registry_v2 import skill_registry
        assert skill_registry.get_stats()['total'] > 0
    
    def test_agent_registry(self):
        from agents.multi.agent_registry_v2 import agent_registry
        assert agent_registry.get_stats()['total'] >= 3

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
