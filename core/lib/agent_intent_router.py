from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""Agent 意图路由器 - 帮助 Agent 理解用户意图并自动路由"""
from core.lib.memory_vector import vector_memory
from core.lib.clawsjoy_config import clawsjoy_config


class AgentIntentRouter:
    """Agent 意图路由器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        """初始化路由向量库"""
        self._ensure_routes_vectorized()
    
    def _ensure_routes_vectorized(self):
        """确保所有路由已向量化"""
        # 检查是否已有路由向量
        results = vector_memory.search("route", category="route", n=1)
        if not results:
            self._vectorize_all_routes()
    
    def _vectorize_all_routes(self):
        """向量化所有路由（供 Agent 使用）"""
        routes_config = clawsjoy_config.get('registry.routes.routes', [])
        
        for route in routes_config:
            path = route.get('path')
            method = route.get('method')
            handler = route.get('handler')
            description = route.get('description', '')
            
            # 构建 Agent 可理解的描述
            text = f"{method} {path}: {description}"
            
            vector_memory.add(
                text=text,
                category="route",
                metadata={
                    "path": path,
                    "method": method,
                    "handler": handler,
                    "description": description
                }
            )
        print(f"✅ 已向量化 {len(routes_config)} 条路由，供 Agent 使用")
    
    def route(self, user_intent: str) -> dict:
        """根据用户意图路由到合适的 API"""
        results = vector_memory.search(user_intent, category="route", n=3)
        
        for r in results:
            if r['similarity'] >= 0.3:
                return {
                    "success": True,
                    "path": r['metadata'].get('path'),
                    "method": r['metadata'].get('method'),
                    "handler": r['metadata'].get('handler'),
                    "confidence": r['similarity'],
                    "description": r['metadata'].get('description')
                }
        
        return {
            "success": False,
            "message": f"无法理解意图: {user_intent}",
            "suggestions": [r['metadata'].get('description') for r in results[:2]] if results else []
        }
    
    def suggest(self, user_intent: str) -> str:
        """返回建议的路由路径"""
        result = self.route(user_intent)
        return result.get('path') if result.get('success') else None


agent_router = AgentIntentRouter()
