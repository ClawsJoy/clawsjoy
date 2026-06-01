# ClawsJoy v6.0 原子引擎待转化清单

## ✅ 已完成
- [x] semantic_engine (语义理解)
- [x] profile_engine (用户画像)
- [x] knowledge_engine (知识图谱)
- [x] skill_matrix_engine (技能矩阵)
- [x] reasoning_engine (推理)
- [x] planning_engine (规划)
- [x] active_engine (主动学习)
- [x] memory_engine (记忆)

## ⏳ 待转化

### P0 - 高优先级
- [ ] event_engine - 事件驱动引擎 (复用 core/lib/event_bus.py)
- [ ] workflow_engine - 工作流引擎 (复用 core/lib/workflow_executor.py)

### P1 - 中优先级
- [ ] monitoring_engine - 监控引擎 (复用 core/lib/monitoring.py)
- [ ] scheduler_engine - 调度引擎 (复用 core/lib/smart_scheduler.py)

### P2 - 低优先级
- [ ] tenant_engine - 租户引擎 (复用 core/lib/tenant_manager.py)
- [ ] ratelimit_engine - 限流引擎 (复用 core/lib/rate_limit_manager.py)
- [ ] audit_engine - 审计引擎 (复用 core/security/auditor.py)
- [ ] hook_engine - Hook引擎 (复用 core/lib/hook_manager.py)

## 转化原则
1. 直接复用现有成熟模块，只做薄封装
2. 统一接口: process(), get_stats(), reload()
3. 集成到 engine.* 统一入口
4. 支持热重载和配置驱动
