# ClawsJoy Soul 系统文档

## 概述
Soul 系统是 ClawsJoy 的核心，赋予 LLM 身份、价值观、情感。

## 六根架构

| 根 | 实现 | 文件 |
|---|------|------|
| 语言之根 | 方言学习 | `dialect_helper.py` |
| 关系之根 | 名字记忆、交互追踪 | `soul_injector.py` |
| 行为之根 | 话本系统 | `scriptbook.yaml` |
| 身份之根 | Soul 注入 | `soul_injector.py` |
| 价值之根 | 危险检测 | `soul_injector.py` |
| 情感之根 | 情绪状态 | `soul_injector.py` |

## 数据存储
- `data/relationship/{user_id}.json` - 用户关系数据
- `data/dialect/{user_id}.json` - 方言词库
- `data/federated/knowledge.json` - 联邦学习知识库

## API
- `POST /api/v5/wisdom/chat` - 对话接口
- `GET /api/v5/agent/list` - Agent 列表
- `GET /api/v5/wisdom/decision/stats` - 决策统计
