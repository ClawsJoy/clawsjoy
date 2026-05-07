# ClawsJoy 系统架构设计

## 🏗️ 核心引擎层 / Core Engine Layer

### 1. 任务队列 / Task Queue
**职责**：管理异步任务、优先级排序、失败重试
- 待处理队列 / Pending Queue
- 执行中队列 / Running Queue  
- 完成队列 / Completed Queue
- 失败队列 / Failed Queue

**文件**：`bin/agent_scheduler.py`, `skills/queue/`

---

### 2. 路由器 / Router
**职责**：根据意图分发任务到对应 Skill
- 意图识别 / Intent Recognition
- Skill 路由 / Skill Routing
- 降级策略 / Fallback Strategy

**文件**：`skills/router/execute.py`

---

### 3. 调度器 / Scheduler
**职责**：定时触发、并发控制、资源分配
- Cron 定时 / Cron Scheduling
- 资源监控 / Resource Monitor
- 负载均衡 / Load Balancing

**文件**：`scheduler/reliable_scheduler.py`, `crontab`

---

### 4. 工作流引擎 / Workflow Engine
**职责**：编排 Skill 执行顺序、依赖管理
- 步骤编排 / Step Orchestration
- 依赖检查 / Dependency Check
- 状态管理 / State Management
- 断点续传 / Resume from Breakpoint

**文件**：`skills/workflow_engine.py`

---

### 5. 进化引擎 / Evolution Engine
**职责**：记录执行结果、优化路由策略、自我学习
- 结果记录 / Result Logging
- 评分系统 / Scoring System
- 策略优化 / Strategy Optimization
- 反馈学习 / Feedback Learning

**文件**：`bin/evolution*.py`, `agents/self_evolve.py`

---

## 🧠 Agent 体系 / Agent System

### 6. Agent 编排器 / Agent Orchestrator
**职责**：协调各专业 Agent 分工
- 任务分配 / Task Assignment
- 进度追踪 / Progress Tracking
- 团队协作 / Team Collaboration

**文件**：`agents/orchestrator.py`

---

### 7. 自愈引擎 / Self-Healing Engine
**职责**：自动诊断、自动修复
- 错误检测 / Error Detection
- 方案匹配 / Solution Matching
- 自动执行 / Auto Execution

**文件**：`agents/self_healing.py`

---

### 8. 记忆系统 / Memory System
**职责**：存储历史、上下文、用户偏好
- 短期记忆 / Short-term Memory
- 长期记忆 / Long-term Memory
- 情景记忆 / Episodic Memory

**文件**：`skills/memory/`

---

## 🔄 数据流 / Data Flow

用户输入 / User Input
↓
路由器 / Router (意图识别)
↓
调度器 / Scheduler (定时/立即)
↓
任务队列 / Task Queue (排队)
↓
工作流引擎 / Workflow Engine (编排)
↓
┌─────────────────────────────────────┐
│ Skills 执行链 / Skill Chain │
│ Spider → Writer → Promo → Upload │
└─────────────────────────────────────┘
↓
进化引擎 / Evolution Engine (记录优化)
↓
输出 / Output

---

## 📊 组件依赖关系 / Component Dependencies

| 组件 | 依赖 | 被依赖 |
|------|------|--------|
| Task Queue | - | Scheduler, Workflow |
| Router | Memory | Scheduler |
| Scheduler | Queue, Router | Workflow |
| Workflow Engine | Scheduler, Queue | Evolution |
| Evolution Engine | Workflow | Router |
| Memory | - | Router, Evolution |

---

## 🔧 配置管理 / Configuration

| 配置 | 文件 | 说明 |
|------|------|------|
| 阈值配置 | `config/cleaner_config.json` | 磁盘、清理阈值 |
| 关键词库 | `data/keywords.json` | 动态关键词 |
| URL 库 | `data/urls/discovered.json` | 发现的采集源 |
| 知识库 | `data/knowledge/common_fixes.json` | 修复方案 |

---

## 📝 核心类 / Core Classes

```python
# 任务队列 / Task Queue
class TaskQueue:
    - pending: List[Task]
    - running: List[Task]
    - completed: List[Task]
    - failed: List[Task]
    - enqueue() / dequeue() / retry()

# 路由器 / Router  
class Router:
    - intent_parser: IntentParser
    - skill_registry: Dict[str, Skill]
    - route(intent) -> Skill

# 调度器 / Scheduler
class Scheduler:
    - cron: CronScheduler
    - interval: IntervalScheduler
    - trigger(task) -> None

# 工作流引擎 / WorkflowEngine
class WorkflowEngine:
    - steps: List[Step]
    - dependencies: Dict[str, List[str]]
    - execute() -> Dict

# 进化引擎 / EvolutionEngine  
class EvolutionEngine:
    - history: List[ExecutionRecord]
    - scores: Dict[str, float]
    - optimize() -> None
🎯 设计原则 / Design Principles
模块化 / Modular - 每个组件独立可替换

可扩展 / Extensible - 新 Skill 即插即用

容错性 / Fault-tolerant - 失败重试、降级

可观测 / Observable - 日志、监控、报告

自进化 / Self-evolving - 从结果中学习优化
*最后更新: 2026-05-06*
