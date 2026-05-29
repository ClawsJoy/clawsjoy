"""LLM 智能执行器 - 兜底方案"""

from core.lib.smart_adapter import smart_adapter


class LLMExecutor:
    """LLM 智能执行器"""
    
    name = "llm_executor"
    
    def execute(self, goal: str, params: dict = None) -> dict:
        """执行 LLM 推理"""
        try:
            response = smart_adapter.generate(goal, auto_select=True)
            if response and len(response) > 0:
                return {"success": True, "response": response, "source": "llm"}
            else:
                # 降级：使用简单回应
                return {"success": True, "response": f"收到您的请求：{goal[:50]}...", "source": "llm_fallback"}
        except Exception as e:
            return {"success": False, "error": str(e)}


llm_executor = LLMExecutor()
