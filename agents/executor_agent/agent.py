"""ExecutorAgent - 执行层"""

from typing import Dict, Optional

from core.agents.business.base_business_agent import BusinessAgent


class ExecutorAgent(BusinessAgent):
    name = "executor_agent"
    description = "任务执行器"
    version = "2.1.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"⚙️ ExecutorAgent v{self.version} 已上线")

    def _execute_business(self, user_input: str, context: Dict = None) -> Dict:
        """执行任务 - 调用大脑调度器"""
        from skills.core.do_anything import DoAnythingSkill

        brain = DoAnythingSkill()
        result = brain.execute({"goal": user_input})

        # 审计记录
        self.audit(
            action="execute_task",
            details={"input": user_input, "output": result},
            result=result.get("success", False) if isinstance(result, dict) else False,
        )

        if isinstance(result, dict):
            if result.get("success"):
                output = result.get("result") or result.get("response") or "执行完成"
                return {"success": True, "response": output}
            else:
                error_msg = result.get("error") or result.get("result") or "执行失败"
                return {"success": False, "response": error_msg}
        else:
            return {"success": False, "response": f"执行异常: 返回了 {type(result)}"}

    def handle(self, user_input: str, context: dict = None) -> dict:
        """统一入口"""
        return self._execute_business(user_input, context)
