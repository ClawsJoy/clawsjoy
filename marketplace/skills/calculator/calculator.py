#!/usr/bin/env python3
"""计算器技能 - OpenClaw 兼容示例"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.skill_system_v2 import BaseSkill, SkillManifest, SkillCategory, SkillPermission

class CalculatorSkill(BaseSkill):
    """高级计算器技能"""
    
    def _get_manifest(self):
        return SkillManifest(
            name="calculator",
            version="1.0.0",
            description="Advanced calculator with expression support",
            author="ClawsJoy",
            category=SkillCategory.UTILITY,
            permissions=SkillPermission.PUBLIC,
            inputs=[
                {"name": "expression", "type": "string", "required": True, 
                 "description": "Math expression (e.g., '2+3*4', 'sqrt(16)')"},
                {"name": "precision", "type": "integer", "default": 2, 
                 "description": "Decimal precision"}
            ],
            outputs=[
                {"name": "result", "type": "number", "description": "Calculation result"},
                {"name": "expression", "type": "string", "description": "Original expression"}
            ],
            examples=[
                "calculator expression='10/3' precision=2",
                "calculator expression='2**10'",
                "calculator expression='(5+3)*2'"
            ]
        )
    
    def execute(self, params):
        import math
        expression = params.get('expression', '')
        precision = params.get('precision', 2)
        
        if not expression:
            return {'success': False, 'error': 'No expression provided'}
        
        # 安全检查
        allowed = set('0123456789+-*/().% sqrt pow abs')
        safe_expr = ''.join(c for c in expression if c in allowed or c.isalpha())
        
        # 安全地计算
        try:
            # 允许的数学函数
            safe_dict = {
                'sqrt': math.sqrt, 'pow': pow, 'abs': abs,
                'pi': math.pi, 'e': math.e
            }
            result = eval(safe_expr, {"__builtins__": {}}, safe_dict)
            
            if isinstance(result, float):
                result = round(result, precision)
            
            return {
                'success': True,
                'result': result,
                'expression': expression,
                'formatted': f"{expression} = {result}"
            }
        except Exception as e:
            return {'success': False, 'error': f'Invalid expression: {e}'}

# 自动注册
calculator = CalculatorSkill()

skill = CalculatorSkill()
