# ClawsJoy 系统能力清单 v4.0.0

## 一、核心架构能力

| 能力 | 状态 | 说明 |
|------|------|------|
| 配置驱动 | ✅ | 20+ YAML 配置文件，无硬编码 |
| 模块化设计 | ✅ | core/, lib/, agents/, skills/ 分层清晰 |
| API 网关 | ✅ | Flask, 端口 5002 |
| 路由注册中心 | ✅ | routes.yaml + 动态注册 |
| 钩子系统 | ✅ | hooks.yaml, 可插拔 |
| 版本管理 | ✅ | version_registry |

## 二、Agent 系统 (10+)

| Agent | 类型 | 能力 |
|-------|------|------|
| orchestrator | 核心 | 任务编排 |
| decision_agent | 核心 | 决策引擎（用户总管） |
| personal_butler | 核心 | 私人管家，数字分身 |
| chat_agent | 核心 | 游客对话 |
| code_agent | 专业 | 代码生成、审查 |
| video_agent | 专业 | 视频制作 |
| youtube_agent | 专业 | YouTube 运营 |
| security_agent | 专业 | 安全审计 |
| memory_manager | 专业 | 记忆管理 |
| analysis_agent | 专业 | 数据分析 |

## 三、技能系统 (70+ 分类)

| 分类 | 数量 | 示例 |
|------|------|------|
| math | 8 | add, multiply, sqrt |
| image | 5 | ai_image, remove_bg |
| video | 7 | manju_maker, add_subtitles |
| text | 5 | to_upper, reverse |
| audio | 2 | tts, whisper |
| network | 6 | http_get, download |
| memory | 10 | memory_query, auto_remember |
| self_heal | 11 | self_heal, error_analyzer |
| tools | 23 | file_processor, regex |
| development | 6 | frontend_developer, skill_weaver |
| 企业办公 | 15+ | crm, sales, meeting, document |
| 家庭生活 | 10+ | home, health, childcare, safety |
| 个人日常 | 12+ | todo, schedule, reminder, weather |

## 四、记忆系统 (L0-L4)

| 层级 | 类型 | 实现 |
|------|------|------|
| L0 | 短期记忆 | 会话级别 |
| L1 | 工作记忆 | 上下文 |
| L2 | 长期记忆 | 用户偏好 |
| L3 | 语义记忆 | 向量知识库 |
| L4 | 永久记忆 | ChromaDB, 122+ 条 |

## 五、学习与进化

| 能力 | 状态 | 说明 |
|------|------|------|
| 学习记录 | ✅ | successful_combos.json |
| 自动生成技能 | ✅ | auto_* 技能 |
| 失败模式记录 | ✅ | failure_patterns |
| LLM 决策 | ✅ | 自主调用 LLM |
| 历史反思 | ✅ | reflection 机制 |

## 六、主动服务能力

| 能力 | 状态 | 说明 |
|------|------|------|
| 感知 | ✅ | 数据源管理器 |
| 分析 | ✅ | 问题检测 |
| 决策 | ✅ | 自主决策引擎 |
| 执行 | ✅ | 清理缓存、优化技能 |
| 报告 | ✅ | 系统报告生成 |
| 通知 | ✅ | 邮件/控制台 |

## 七、安全与审计

| 能力 | 状态 |
|------|------|
| JWT 认证 | ✅ |
| AES-256 加密 | ✅ |
| 敏感信息脱敏 | ✅ |
| 审计日志 | ✅ |
| Prompt Injection 防护 | ✅ |
| 权限分层 | ✅ |

## 八、前端与客户端

| 能力 | 状态 |
|------|------|
| Web 界面 | ✅ |
| Electron 客户端 | ✅ |
| 环抱座舱 UI | ✅ |
| Agent 商店 | ✅ |
| 皮肤系统 | ✅ |
| 语音系统 | ✅ |

