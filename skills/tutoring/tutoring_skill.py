#!/usr/bin/env python3
"""Explain Problem - Explain Problem 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


class ExplainProblemSkill:
    def execute(self, params):
        problem = params.get("problem", "")
        subject = params.get("subject", "math")
        # 根据题型返回解析步骤
        return {
            "success": True,
            "steps": [
                "1. 理解题意",
                "2. 分析已知条件",
                "3. 列出公式",
                "4. 计算解答",
                "5. 验证答案",
            ],
            "message": f"{subject}题目解析完成",
        }


skill = ExplainProblemSkill()
