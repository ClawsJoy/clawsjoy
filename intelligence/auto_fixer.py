"""自动修复器 - 包装 real_fixer"""
from intelligence.real_fixer import RealFixer

class AutoFixer:
    def __init__(self):
        self.fixer = RealFixer()
    
    def auto_fix_services(self):
        """无参数版本，修复所有常见服务"""
        print("🔧 自动修复服务...")
        fixed = []
        
        # 修复网关
        if self.fixer.fix_service('gateway', 5002, 'python3 agent_gateway_web.py'):
            fixed.append('gateway')
        
        # 修复多智能体
        if self.fixer.fix_service('agent', 5005, 'python3 multi_agent_service_v2.py'):
            fixed.append('agent')
        
        # 修复文档生成
        if self.fixer.fix_service('doc', 5008, 'python3 doc_generator.py'):
            fixed.append('doc')
        
        # 修复 Ollama
        self.fixer.fix_ollama()
        
        return fixed
    
    def fix_port_conflict(self, port):
        return self.fixer.fix_port_conflict(port)
