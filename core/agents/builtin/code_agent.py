"""代码 Agent - 专注代码生成和调试"""

from typing import Dict, Optional
from pathlib import Path
import yaml
from core.agents.base.smart_agent import SmartAgent
from core.lib.unified_config import unified_config
from core.lib.smart_adapter import smart_adapter


class CodeAgent(SmartAgent):
    """代码 Agent - 专业代码助手"""

    name = "code_agent"
    description = "代码生成和调试"
    version = "2.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._load_config()
        print("💻 代码Agent 初始化完成")

    def _load_config(self):
        """加载配置"""
        # 优先从专用配置文件加载
        config_file = Path("config/agents/code_agent.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.agent_config = yaml.safe_load(f)
        else:
            # 回退到 unified_config
            self.agent_config = unified_config.get("agents.code_agent", {})
        
        # 获取模型配置
        llm_config = self.agent_config.get("llm", {})
        self.model = llm_config.get("model", "deepseek-coder:6.7b")
        self.temperature = llm_config.get("temperature", 0.2)
        self.max_tokens = llm_config.get("max_tokens", 2048)
        self.timeout = llm_config.get("timeout", 60)

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理代码请求"""
        print(f"[代码] 收到: {user_input}")
        
        # 分析意图
        intent = self._analyze_intent(user_input)
        
        # 生成代码
        if intent == "generate":
            code = self._generate_code(user_input)
        elif intent == "debug":
            code = self._debug_code(user_input)
        elif intent == "explain":
            code = self._explain_code(user_input)
        else:
            code = self._generate_code(user_input)
        
        return {
            "success": True,
            "response": code,
            "agent": self.name,
            "user_id": self.user_id
        }

    def _analyze_intent(self, user_input: str) -> str:
        """分析用户意图"""
        user_lower = user_input.lower()
        if any(kw in user_lower for kw in ["debug", "修复", "错误", "bug"]):
            return "debug"
        if any(kw in user_lower for kw in ["解释", "说明", "explain", "what is"]):
            return "explain"
        return "generate"

    def _generate_code(self, prompt: str) -> str:
        """生成代码"""
        try:
            # 使用 smart_adapter 调用 deepseek-coder
            system_prompt = self.agent_config.get("prompts", {}).get(
                "system", "你是一个专业的代码助手。"
            )
            full_prompt = f"{system_prompt}\n\n用户需求: {prompt}\n\n请生成代码:"
            
            response = smart_adapter.generate(
                full_prompt,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response
        except Exception as e:
            return f"代码生成失败: {e}"

    def _debug_code(self, code_info: str) -> str:
        """调试代码"""
        return f"调试结果:\n```python\n# 分析: {code_info}\n```"

    def _explain_code(self, code: str) -> str:
        """解释代码"""
        return f"代码解释:\n```python\n# {code}\n```"

    def get_capabilities(self) -> list:
        """获取 Agent 能力"""
        return self.agent_config.get("capabilities", ["write_code"])


# 注意：不创建全局实例（单例模式）
