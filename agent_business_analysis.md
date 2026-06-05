# ClawsJoy v5 Agent 业务逻辑分析

## 1. ChatAgent - 通用对话
- 继承: SmartAgent
- 核心功能: 日常对话、问候、感谢、告别
- 特色: 原子技能（天气、计算、时间、随机数）、话本匹配、名字识别
- 业务逻辑: 原子技能 → 话本 → 状态回答 → LLM 兜底

## 2. CodeAgent - 代码生成
- 继承: SmartAgent
- 核心功能: 代码生成、代码解释、代码优化
- 特色: 多语言支持、代码格式化
- 业务逻辑: 意图识别 → 代码生成 → 格式化输出

## 3. Orchestrator - 智能路由
- 继承: SmartAgent
- 核心功能: 四引擎智能路由（LLM→Vector→Config→Rule）
- 特色: 社会协作路由、任务分解
- 业务逻辑: 社会协作 → LLM → 向量 → 配置 → 规则 → 默认

## 4. DecisionAgent - 决策
- 继承: SmartAgent
- 核心功能: 智能决策、方案评估
- 特色: 多维度评估、置信度计算

## 5. AnalysisAgent - 分析
- 继承: SmartAgent
- 核心功能: 数据分析、报告生成
- 特色: 统计分析、可视化建议

## 6. ExecutorAgent - 执行
- 继承: SmartAgent
- 核心功能: 任务执行、工作流触发
- 特色: 并行执行、状态跟踪

## 7. TranslateAgent - 翻译
- 继承: SmartAgent
- 核心功能: 多语言翻译
- 特色: 方言支持、实时翻译

## 8. VisionAgent - 视觉
- 继承: SmartAgent
- 核心功能: 图像识别、OCR、人脸检测
- 特色: 多模型支持

## 9. VideoAgent - 视频
- 继承: SmartAgent
- 核心功能: 视频处理、剪辑、分析
- 特色: 多格式支持

## 10. MemoryAgent - 记忆
- 继承: SmartAgent
- 核心功能: 记忆管理、知识库
- 特色: 长期记忆、短期记忆、向量检索

## 11. YouTubeAgent - YouTube经营
- 继承: SmartAgent
- 核心功能: 脚本生成、标题生成、描述生成
- 特色: 频道分析、内容创意

## 12. DirectorAgent - 导演
- 继承: SmartAgent
- 核心功能: 任务编排、流程控制
- 特色: 多 Agent 协调

## 13. WriterAgent - 写作
- 继承: SmartAgent
- 核心功能: 文章写作、润色、改写
- 特色: 多种写作风格

## 14. DialectAgent - 方言
- 继承: SmartAgent
- 核心功能: 方言识别、方言翻译
- 特色: 多种方言支持

## 15. CollaborationAgent - 协作
- 继承: SmartAgent
- 核心功能: 多 Agent 协作、任务分发
- 特色: 负载均衡、结果聚合

## 16. VideoIndexerAgent - 视频索引
- 继承: SmartAgent
- 核心功能: 视频索引、内容分析
- 特色: 标签提取、场景识别

## 17. 基类能力（所有 Agent 共有）
- BaseAgent: 安全边界、法律合规、生命伦理、永久记忆
- CommunicableAgent: 情感识别、联邦学习、可解释性、审计日志
- SmartAgent: 自我认知、智能决策、经验学习、反思优化、任务分解

