"""Orchestrator V6 - 语义理解 + 纯配置驱动（零硬编码）"""

from typing import Dict


class OrchestratorV6:
    """智能体编排器 V6 - 完全配置驱动"""

    def __init__(self, user_id: str = "anonymous"):
        self.user_id = user_id
        self._intent_map = None
        self._capabilities = None

    def _get_capabilities(self):
        """获取 agent_capabilities 配置"""
        if self._capabilities is not None:
            return self._capabilities
        try:
            from core.lib.unified_config import unified_config
            self._capabilities = unified_config.get("keywords.agent_capabilities", {})
            return self._capabilities
        except Exception as e:
            print(f"⚠️ 加载 capabilities 失败: {e}")
            return {}

    def _build_intent_map(self):
        """从 capabilities 自动构建 intent → agent 映射"""
        capabilities = self._get_capabilities()
        intent_map = {}
        
        for agent_name, agent_config in capabilities.items():
            # 1. agent 名称本身
            intent_map[agent_name] = agent_name
            # 2. 去掉 _agent 后缀
            base_name = agent_name.replace('_agent', '')
            intent_map[base_name] = agent_name
            # 3. 去掉 _skill 后缀
            base_name2 = agent_name.replace('_skill', '')
            intent_map[base_name2] = agent_name
            
            # 4. 从 capable_of 关键词中提取常用 intent 别名
            for keyword in agent_config.get('capable_of', []):
                # 短关键词（2-4字）作为 intent 别名
                if 2 <= len(keyword) <= 4:
                    intent_map[keyword] = agent_name
                # 英文关键词
                if keyword.isalpha() and len(keyword) <= 10:
                    intent_map[keyword.lower()] = agent_name
        
        print(f"[OrchestratorV6] 从配置生成 {len(intent_map)} 个 intent 映射")
        return intent_map

    def _get_intent_map(self):
        """获取 intent 映射（懒加载）"""
        if self._intent_map is None:
            self._intent_map = self._build_intent_map()
        return self._intent_map

    def smart_route(self, message: str) -> str:
        """智能路由 - 语义理解 + 纯配置映射"""
        try:
            from engine.semantic import semantic_engine
            result = semantic_engine.understand(message)
            intent = result.intent
            confidence = result.confidence

            if confidence >= 0.2:
                intent_map = self._get_intent_map()
                if intent in intent_map:
                    target = intent_map[intent]
                    print(f"[OrchestratorV6] {intent}({confidence:.2f}) → {target}")
                    return target
            
            return "chat_agent"
            
        except Exception as e:
            print(f"[OrchestratorV6] 错误: {e}")
            return "chat_agent"

    def decompose_task(self, task: str) -> Dict:
        """任务分解"""
        try:
            from engine.semantic import semantic_engine
            result = semantic_engine.understand(task)
            intent = result.intent
            return {
                'intent': intent,
                'subtasks': []
            }
        except:
            return {'intent': 'unknown', 'subtasks': []}


orchestrator_v6 = OrchestratorV6()
