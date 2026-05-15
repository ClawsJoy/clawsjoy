import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
import json
from lib.data_contract import DataContract

class DesignExecutorSkill:
    name = "design_executor"
    description = "执行设计方案"
    version = "1.0.0"
    category = "execution"

    def execute(self, params):
        designs = DataContract.get_latest_design()
        if not designs:
            return {"success": False, "message": "无设计方案"}
        
        executed = []
        for design in designs:
            issue = design.get('issue', '')
            skill_chain = design.get('design', {}).get('skill_chain', [])
            executed.append({
                'issue': issue[:50],
                'actions': len(skill_chain),
                'status': 'planned'
            })
        
        return {"success": True, "executed": executed}

skill = DesignExecutorSkill()
