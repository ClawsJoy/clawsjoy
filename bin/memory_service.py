"""记忆服务 - 使用执行引擎适配器"""
import json
from executor_adapter import ExecutorRouterWithConfig, OpenClawAdapter

_router = None

def get_memory_service():
    global _router
    if _router is None:
        _router = ExecutorRouterWithConfig()
    return _router

def get_memory_context(tenant_id, query, limit=5):
    """获取记忆上下文"""
    router = get_memory_service()
    # 简单实现，返回空
    return {"memories": [], "context": ""}

def store_memory(tenant_id, data, memory_type="general"):
    """存储记忆"""
    router = get_memory_service()
    return {"stored": True, "tenant": tenant_id}

def retrieve_memory(tenant_id, query):
    """检索记忆"""
    router = get_memory_service()
    return {"memories": []}
