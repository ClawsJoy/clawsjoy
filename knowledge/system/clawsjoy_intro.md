# ClawsJoy 智能助手系统

## 系统简介
ClawsJoy 是一个基于 LLM 的智慧化多 Agent 智能助手系统，支持本地部署，6GB 显存即可运行。

## 核心特性
- 多 Agent 协作：9个专业智能体协同工作
- 联邦学习：Agent 间知识共享
- 主动服务：基于用户画像的主动建议
- 方言理解：支持用户学习和使用方言
- 元认知：置信度量化、经验学习

## Agent 列表
1. ChatAgent - 对话、记忆、情感、主动建议
2. CodeAgent - 代码生成、解释、调试、优化
3. AnalysisAgent - 数据分析、框架提供
4. TranslateAgent - 多语言翻译（中英日韩法等）
5. CalculatorAgent - 科学计算
6. ButlerAgent - 私人管家、待办管理
7. Orchestrator - 任务编排、分解、调度
8. MemoryAgent - 记忆管理
9. DialectAgent - 方言学习与管理

## 技术架构
- 基类：BusinessAgent（统一业务基类）
- 包装器：WisdomWrapper（元认知、经验学习）
- 通信：AgentCommunication（Agent 间消息传递）
- 存储：本地 JSON + 向量知识库

## 开发团队
ClawsJoy 由 ClawsJoy 团队开发维护。
