#!/usr/bin/env python3
"""My Calc - My Calc 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


description = "my_calc 自定义计算器 加法 减法 乘法 除法 数学运算"

class MyCalcSkill:
    """计算器技能类"""
    
    def execute(self, params):
        a = params.get('a', 0)
        b = params.get('b', 0)
        op = params.get('op', 'add')
        
        if op == 'add':
            result = a + b
        elif op == 'sub':
            result = a - b
        elif op == 'mul':
            result = a * b
        elif op == 'div':
            result = a / b if b != 0 else 'error'
        else:
            result = a + b
        
        return {"result": result, "skill": "my_calc"}

skill = MyCalcSkill()
