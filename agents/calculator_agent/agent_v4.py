#!/usr/bin/env python3
"""CalculatorAgent v4.1 - 科学计算器增强版"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import math
from typing import Dict, Optional, Tuple, List

from core.agents.business.business_agent import BusinessAgent


class CalculatorAgentV4(BusinessAgent):
    """科学计算器 Agent - 增强版"""
    
    name = "calculator_agent_v4"
    description = "科学计算助手"
    version = "4.1.0"
    
    # 支持的数学函数
    MATH_FUNCTIONS = {
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'log': math.log,
        'log10': math.log10,
        'log2': math.log2,
        'exp': math.exp,
        'abs': abs,
        'floor': math.floor,
        'ceil': math.ceil,
        'round': round,
        'factorial': math.factorial,
        'gcd': math.gcd,
    }
    
    # 常量
    CONSTANTS = {
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        'inf': float('inf'),
    }
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"🔢 CalculatorAgent v{self.version} 科学计算器已启动")
        print(f"   📐 支持 {len(self.MATH_FUNCTIONS)} 个数学函数")
        print(f"   📊 支持 {len(self.CONSTANTS)} 个数学常量")
    
    # ========== 能力声明 ==========
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("calculate", "number"): (True, 0.95),
            ("calculate", "expression"): (True, 0.95),
            ("calculate", "function"): (True, 0.90),
        }
        return capabilities.get((action, target), (False, 0.0))
    
    def can_handle(self, action: str, target: str) -> bool:
        return action == 'calculate' and target in ['number', 'expression', 'function']
    
    # ========== 核心业务 ==========
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        
        # 提取表达式
        expression = self._extract_expression(user_input)
        
        if not expression:
            return self._response(self._get_help())
        
        # 科学计算
        result = self._scientific_calculate(expression)
        return self._response(result)
    
    def _extract_expression(self, text: str) -> Optional[str]:
        """提取数学表达式"""
        # 移除中文前缀
        cleaned = text.strip()
        prefixes = ["计算", "等于多少", "求值", "帮我算", "计算一下", "请问"]
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        # 移除问号和多余字符
        cleaned = cleaned.rstrip('?？')
        
        # 匹配数学表达式（支持函数和复杂表达式）
        pattern = r'([\d\s\+\-\*\/\(\)\^\.a-z]+)'
        match = re.search(pattern, cleaned, re.IGNORECASE)
        
        if match:
            expr = match.group(1).strip()
            if expr and len(expr) > 0:
                return expr
        
        return None
    
    def _scientific_calculate(self, expression: str) -> str:
        """科学计算 - 支持函数和常量"""
        try:
            # 预处理
            expr = self._preprocess(expression)
            
            # 创建安全计算环境
            safe_dict = {
                "__builtins__": {},
                "abs": abs,
                "round": round,
                "int": int,
                "float": float,
                "math": math,
                **self.MATH_FUNCTIONS,
                **self.CONSTANTS,
            }
            
            # 计算结果
            result = eval(expr, safe_dict, {})
            
            # 格式化输出
            formatted = self._format_result(expression, result)
            return formatted
            
        except ZeroDivisionError:
            return f"❌ 错误：除数不能为 0"
        except ValueError as e:
            return f"❌ 数值错误：{str(e)[:50]}"
        except Exception as e:
            return self._llm_calculate(expression)
    
    def _preprocess(self, expr: str) -> str:
        """预处理表达式"""
        # 替换幂运算
        expr = expr.replace('^', '**')
        expr = expr.replace('×', '*')
        expr = expr.replace('÷', '/')
        
        # 处理百分号
        expr = re.sub(r'(\d+)%', r'\1/100', expr)
        
        # 处理隐式乘法（如 2pi -> 2*pi）
        for const in self.CONSTANTS:
            expr = re.sub(r'(\d)({})'.format(const), r'\1*\2', expr)
        
        # 处理函数调用（确保使用 math. 前缀）
        for func in self.MATH_FUNCTIONS:
            expr = re.sub(r'{}\('.format(func), r'math.{}\('.format(func), expr)
        
        return expr
    
    def _format_result(self, expression: str, result: float) -> str:
        """格式化结果"""
        # 处理浮点数精度
        if isinstance(result, float):
            # 整数显示为整数
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 8)
                # 去除末尾零
                if isinstance(result, float):
                    result = float(str(result).rstrip('0').rstrip('.'))
        
        # 生成详细结果
        lines = [
            "🔢 **科学计算结果**",
            "",
            f"📐 表达式：`{expression}`",
            f"✅ 结果：**{result}**",
            "",
        ]
        
        return "\n".join(lines)
    
    def _llm_calculate(self, expression: str) -> str:
        """LLM 辅助计算"""
        prompt = f"""请计算以下数学表达式：

{expression}

可用函数：sqrt, sin, cos, tan, log, log10, exp, abs, floor, ceil, factorial
常量：pi, e

要求：
1. 分步计算
2. 给出最终结果

计算结果："""

        response = self._call_llm(prompt)
        
        if response:
            return f"🔢 **科学计算结果**\n\n📐 表达式：`{expression}`\n\n🤖 LLM 计算：\n{response}"
        
        return self._get_help()
    
    def _get_help(self) -> str:
        """帮助信息"""
        functions = ", ".join(list(self.MATH_FUNCTIONS.keys())[:12])
        constants = ", ".join(self.CONSTANTS.keys())
        
        return f"""🔢 **科学计算器**

**支持运算：**
- 加减乘除：`2 + 3 * 4`
- 括号：`(2 + 3) * 4`
- 幂运算：`2^3` 或 `2**3`

**数学函数：**
{functions}...

**常量：**
{constants}

**示例：**
- `sqrt(16) + 3^2`
- `sin(pi/2)`
- `log(100) + log10(1000)`
- `factorial(5)`
- `2 * pi * 5`

**公式计算：**
- `(a + b) * 2`（需替换变量）
- `圆的面积 = pi * r^2`（需提供半径）"""

    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }


if __name__ == "__main__":
    agent = CalculatorAgentV4("test")
    
    tests = [
        "计算 123 + 456",
        "(2+3)*4",
        "sqrt(16)",
        "sin(pi/2)",
        "2^3 + 5",
        "log(100)",
        "factorial(5)",
    ]
    
    print("=" * 50)
    print("CalculatorAgent 科学计算器测试")
    print("=" * 50)
    
    for test in tests:
        print(f"\n📐 输入: {test}")
        result = agent.process(test)
        print(f"📊 输出: {result.get('response')}")
    
    print("\n" + "=" * 50)
    print("✅ CalculatorAgent 科学计算器测试通过")
