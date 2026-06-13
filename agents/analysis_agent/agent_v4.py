#!/usr/bin/env python3
"""AnalysisAgent v4.0 - 智慧化数据分析智能体"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class AnalysisAgentV4(BusinessAgent):
    """数据分析 Agent - 智慧化版本"""
    
    name = "analysis_agent_v4"
    description = "智慧数据分析助手"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"📊 AnalysisAgent v{self.version} 智慧化启动")
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        """声明能力"""
        capabilities = {
            ("analyze", "data"): (True, 0.95),
            ("search", "info"): (True, 0.90),
            ("summarize", "text"): (True, 0.85),
        }
        return capabilities.get((action, target), (False, 0.0))
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """核心数据分析逻辑"""
        
        # 数据分析
        if any(kw in user_input for kw in ["分析", "统计", "趋势"]):
            result = self._analyze(user_input)
            return self._response(result)
        
        # 数据总结
        if "总结" in user_input:
            result = self._summarize(user_input)
            return self._response(result)
        
        # 默认
        return self._response(self._get_help())
    
    def _analyze(self, text: str) -> str:
        """分析数据 - 智能处理有无数据的情况"""
    
        # 检测是否提供了具体数据
        has_data = self._has_concrete_data(text)
    
        if has_data:
            # 有具体数据，进行详细分析
            prompt = f"""请分析以下数据：

用户请求：{text}

要求：
1. 提取关键指标
2. 识别趋势和异常
3. 给出 actionable 的建议
4. 输出结构清晰的分析报告"""

            response = self._call_llm(prompt)
            if response:
                return f"📊 **数据分析报告**\n\n{response}"
    
        # 没有具体数据，提供分析框架
        return self._provide_analysis_framework(text)

    def _has_concrete_data(self, text: str) -> bool:
        """检测是否包含具体数据"""
        data_indicators = [
            r'\d+',           # 数字
            r'\d+\.\d+',      # 小数
            r'\d+%',          # 百分比
            r'[0-9,]+',       # 带逗号的数字
            '元', '万', '亿',  # 金额单位
            '增长', '下降',     # 变化描述
        ]
    
        import re
        for indicator in data_indicators:
            if re.search(indicator, text):
                return True
        return False

    def _provide_analysis_framework(self, text: str) -> str:
        """提供分析框架（当没有具体数据时）"""
    
        # 识别分析类型
        analysis_type = self._identify_analysis_type(text)
    
        frameworks = {
            "sales": """📊 **销售数据分析框架**

要进行销售数据分析，请提供以下信息：

1. **基础数据**
   - 销售周期（日/周/月/年）
   - 产品/服务类别
   - 各时段销售额

2. **分析维度**
   - 同比/环比增长率
   - 产品销售排行
   - 季节性波动

3. **输出格式**
   - 我可以生成趋势图、对比表、预测模型

📝 请提供您的具体数据，我将为您生成详细分析报告。""",

            "user": """📊 **用户行为分析框架**

要进行用户行为分析，请提供：

1. **用户数据**
   - 用户数量/新增用户
   - 活跃度（DAU/MAU）
   - 留存率（次日/7日/30日）

2. **行为数据**
   - 访问时长/频率
   - 转化率/漏斗分析
   - 用户画像标签

📝 请分享相关数据，我将为您提供深入洞察。""",

            "financial": """📊 **财务数据分析框架**

财务分析需要以下信息：

1. **核心指标**
   - 收入/成本/利润
   - 毛利率/净利率
   - 资产负债情况

2. **趋势分析**
   - 历史数据（至少3个周期）
   - 预算对比

📝 请提供财务数据，我将生成分析报告。""",

            "default": f"""📊 **数据分析框架**

针对「{text[:50]}」的分析，请提供：

1. **数据内容**
   - 具体数值或数据集
   - 时间范围
   - 关键指标

2. **分析目标**
   - 想了解什么？
   - 需要什么结论？

3. **输出格式**
   - 文字报告/图表/预测

📝 请分享数据，我将为您进行专业分析。"""
        }
    
        return frameworks.get(analysis_type, frameworks["default"])

    def _identify_analysis_type(self, text: str) -> str:
        """识别分析类型"""
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["销售", "销售额", "销量", "成交"]):
            return "sales"
        if any(kw in text_lower for kw in ["用户", "客户", "访客", "活跃"]):
            return "user"
        if any(kw in text_lower for kw in ["财务", "收入", "成本", "利润", "营收"]):
            return "financial"
        return "default"
    

    def _summarize(self, text: str) -> str:
        prompt = f"请总结：{text}\n\n输出3-5个要点。"
        response = self._call_llm(prompt)
        if response:
            return f"📝 **摘要**\n\n{response}"
        return "📝 请提供需要总结的内容。"
    
    def _get_help(self) -> str:
        return """📊 **数据分析助手**

- 分析数据："分析销售数据"
- 数据总结："总结报告" """
    
    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }


if __name__ == "__main__":
    agent = AnalysisAgentV4("test")
    print("\n✅ AnalysisAgentV4 测试通过")
