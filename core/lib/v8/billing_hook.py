#!/usr/bin/env python3
"""v8 记账钩子 — 集成 ledger + 适配器"""

from core.lib.v8.roster_engine import roster_engine
from core.lib.v8.ledger import ledger
from core.lib.v8.adapters.factory import get_adapter


def execute_with_ledger(server_id: str, agent_name: str, prompt: str,
                        system_prompt: str = "", history: list = None,
                        workspace: str = "/sandbox/default") -> dict:
    """
    统一执行入口：
    1. 查花名册 → 获取模型和 Key
    2. 获取适配器 → 执行
    3. 记账 + 记事
    """
    member = roster_engine.get(server_id, agent_name)
    if not member:
        # 降级：走本地 Ollama
        from core.lib.llm_client import llm_client
        result = llm_client.generate(prompt)
        return {"success": True, "content": result, "tokens": 0, "model": "ollama"}

    model = member.get("model", "")
    api_key = member.get("api_key", "")
    unit_price = member.get("unit_price", 0)

    adapter = get_adapter(model, api_key=api_key)
    if adapter is None:
        # 本地 Ollama
        from core.lib.llm_client import llm_client
        result = llm_client.generate(prompt)
        return {"success": True, "content": result, "tokens": 0, "model": "ollama"}

    result = adapter.execute(prompt, system_prompt, history,
                             workspace=workspace if "claude-code" in model else None)

    # 记账
    if result["success"] and result["tokens"] > 0:
        cost = ledger.record_cost(
            server_id=server_id,
            agent_name=agent_name,
            position=member.get("position", ""),
            model=model,
            tokens=result["tokens"],
            unit_price=unit_price,
            summary=prompt[:100],
        )
        result["cost"] = cost["cost"]

    # 记事
    ledger.record_event(
        server_id=server_id,
        agent_name=agent_name,
        position=member.get("position", ""),
        action=prompt[:50],
        summary=result.get("content", "")[:200],
        cost=result.get("cost", 0),
        status="completed" if result["success"] else "failed",
    )

    return result
