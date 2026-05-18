
ClawsJoy 4.0 Agent 手册
Agent 类型
DecisionAgent
用户总管

负责调度和决策

文件: agents/decision_agent_v3.py

ChatAgent
话术生成

调用 LLM 生成自然回复

文件: agents/chat_agent.py

ExecutorAgent
技能执行

调用技能注册表

文件: agents/executor_agent.py

Agent 通信
发送消息
file_exchange.send(to_agent="decision", data={"action": "...", "data": {...}})
接收消息
message = file_exchange.receive("agent_name")
技能调用
执行技能
from lib.skill_registry_v4 import skill_registry
result = skill_registry.execute_skill("ai-image-gen", {"prompt": "..."})
记忆存储
存储
results = memory.recall(query="关键词", category="conversation")
