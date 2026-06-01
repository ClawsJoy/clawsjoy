#!/usr/bin/env python3
"""Code Agent - 代码生成和审查"""

from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent
from core.lib.smart_adapter import smart_adapter
import re


class CodeAgent(SmartAgent):
    name = "code_agent"
    description = "代码生成和审查"
    version = "2.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._load_agent_config()
        print("💻 代码Agent 初始化完成")

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理用户输入 - 支持代码生成和代码审查"""
        print(f"[代码] 收到: {user_input}")
        
        # 检测是否为代码审查请求
        review_keywords = ['检查代码', '审查代码', 'review', '检查语法', '代码有问题', '帮我看看', '找bug', '哪里有错']
        if any(kw in user_input.lower() for kw in review_keywords):
            return self.code_review(user_input)
        
        # 默认代码生成
        result = smart_adapter.generate(
            user_input,
            auto_select=True
        )
        
        return {
            "success": True,
            "response": result,
            "agent": self.name,
            "user_id": self.user_id
        }
    
    def code_review(self, user_input: str) -> Dict:
        """代码审查功能 - 检查逻辑和语法问题"""
        
        # 提取代码块
        code_match = re.search(r'```(\w*)\n(.*?)```', user_input, re.DOTALL)
        
        if not code_match:
            return {
                "success": True,
                "response": "请提供要审查的代码，用 ``` 标记代码块。\n\n例如：\n```python\n你的代码\n```",
                "agent": self.name,
                "user_id": self.user_id
            }
        
        language = code_match.group(1) or 'python'
        code = code_match.group(2)
        
        # 构建审查提示
        review_prompt = f"""请对以下{language}代码进行审查：

```{language}
{code}
#请分析：

#语法错误

#逻辑问题

#潜在bug

#性能问题

#代码风格建议

#输出格式：

#问题: 描述问题

#建议: 如何修复

#修复后代码: (如有必要)
"""

        result = smart_adapter.generate(
        review_prompt,
        auto_select=True
        )

        return {
            "success": True,
            "response": result,
            "agent": self.name,
            "user_id": self.user_id
        }

#全局实例
code_agent = CodeAgent()
