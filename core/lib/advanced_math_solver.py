"""高级数学求解器 - 支持更多题型"""

import re
from typing import Optional, Tuple, Dict, Any

class AdvancedMathSolver:
    """解决各类数学问题"""
    
    @staticmethod
    def solve_work_problem(question: str) -> Optional[str]:
        """解决工作效率问题"""
        # 匹配合作问题
        patterns = [
            r'甲单独(\d+)小时.*?乙单独(\d+)小时',
            r'甲需要(\d+)小时.*?乙需要(\d+)小时',
            r'A(\d+)小时.*?B(\d+)小时',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question)
            if match:
                a = float(match.group(1))
                b = float(match.group(2))
                
                rate_a = 1 / a
                rate_b = 1 / b
                combined = rate_a + rate_b
                time_needed = 1 / combined
                
                return f"""合作需要 {time_needed:.1f} 小时完成工作。

解题：
• 甲效率: 1/{a:.0f} = {rate_a:.3f}
• 乙效率: 1/{b:.0f} = {rate_b:.3f}
• 合效率: {rate_a:.3f} + {rate_b:.3f} = {combined:.3f}
• 时间: 1 ÷ {combined:.3f} = {time_needed:.1f} 小时

答案：{time_needed:.1f} 小时"""
        return None
    
    @staticmethod
    def solve_percentage(question: str) -> Optional[str]:
        """解决百分比问题"""
        # 匹配百分比
        pattern = r'(\d+)\s*%\s*of\s*(\d+)'
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            percent = float(match.group(1))
            total = float(match.group(2))
            result = (percent / 100) * total
            return f"{percent}% of {total:.0f} = {result:.2f}"
        
        # 匹配"多少的百分之几"
        pattern = r'(\d+)\s*是\s*(\d+)\s*的\s*百分之几'
        match = re.search(pattern, question)
        if match:
            part = float(match.group(1))
            whole = float(match.group(2))
            percent = (part / whole) * 100
            return f"{part:.0f} 是 {whole:.0f} 的 {percent:.1f}%"
        
        return None
    
    @staticmethod
    def solve_speed_distance(question: str) -> Optional[str]:
        """解决速度距离问题"""
        # 速度×时间=距离
        pattern = r'速度(\d+).*?时间(\d+)'
        match = re.search(pattern, question)
        if match:
            speed = float(match.group(1))
            time = float(match.group(2))
            distance = speed * time
            return f"距离 = 速度 × 时间 = {speed} × {time} = {distance} 单位"
        return None

math_solver = AdvancedMathSolver()
