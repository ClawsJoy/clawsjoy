"""WriterAgent - 业务层：内容创作"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

from typing import Dict, Optional

from core.agents.business.business_agent_v2 import BusinessAgentV2


class WriterAgent(BusinessAgentV2):
    """作家 - 业务层，执行写作任务"""

    name = "writer_agent"
    description = "智能写作助手"
    version = "3.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"✍️ 作家 v{self.version} 已上岗")

    def _execute_business(self, user_input: str, context: Dict = None) -> Dict:
        return self.process(user_input, context)

    def process(self, user_input: str, context: Dict = None) -> Dict:
        """执行写作任务"""
        print(f"[作家] 开始创作")

        # 提取分析结果
        analysis = None
        if context and isinstance(context, dict):
            analysis = context.get("previous_result")
            if analysis:
                print(f"[作家] 接收到分析结果，长度: {len(str(analysis))}")

        from core.lib.smart_adapter import smart_adapter

        if analysis and len(analysis) > 50:
            prompt = f"""请根据以下分析内容，撰写一份专业的总结报告。

【分析内容】
{analysis[:3000]}

【报告要求】
1. 标题：# 人工智能发展趋势分析报告
2. 开篇：2-3句话总结核心发现
3. 主体：分3个要点，每个要点有小标题
4. 结论：给出具体建议

请直接输出报告，不要添加任何前缀或自我介绍："""

            response = smart_adapter.generate(
                prompt, auto_select=True, max_tokens=1500, temperature=0.7
            )
        else:
            response = "请先提供分析数据，我将为您撰写详细报告。"

        # 如果响应以"（我是 ClawsJoy 助手）"开头，移除它
        if response.startswith("（我是 ClawsJoy 助手）"):
            response = response.replace("（我是 ClawsJoy 助手）", "", 1).strip()
            # 如果替换后还是以"我是"开头，继续清理
            if response.startswith("我是 ClawsJoy 助手"):
                response = response.replace("我是 ClawsJoy 助手", "", 1).strip()

        if not response or len(response) < 50:
            if analysis:
                response = f"""# 分析报告

## 核心发现
{analysis[:300]}

## 总结
基于以上分析，建议持续关注该领域发展。"""
            else:
                response = "请提供需要分析的具体内容。"

        print(f"[作家] 创作完成，长度: {len(response)}")

        return {
            "success": True,
            "response": response,
            "full_response": response,
            "agent": self.name,
            "user_id": self.user_id,
        }


writer_agent = WriterAgent()
