# ClawsJoy v5 瘦身建议

## 高优先级（立即执行）

### 1. 合并配置模块
当前有多个配置模块：
- `unified_config.py` (主要，保留)
- `config_helper.py` (可废弃，功能已合并)
- `config_manager.py` (可废弃)
- `config.py` (新创建，可合并到 unified_config)

**建议**: 统一使用 `unified_config.py`

### 2. 合并缓存模块
- `response_cache.py` (新，保留)
- `cache.py` (旧，可废弃)
- `SimpleCache` 类（在主网关中，可移除）

**建议**: 只保留 `response_cache.py`

### 3. 统一 Agent 基类
当前有多个基类：
- `core/agents/base/base_agent.py`
- `core/agents/base/smart_agent.py`
- `core/agents/base/communicable_agent.py`

**建议**: 合并为一个基类

## 中优先级（本周完成）

### 4. 减少配置文件数量
当前 182 个 YAML 文件，许多可以合并

### 5. 删除未使用的导入
使用 `autoflake` 自动清理

## 低优先级（可选）

### 6. 拆分大文件
- `agent_gateway_enhanced.py` (505行，可接受)
- `route_handlers.py` (1192行，需要拆分)

### 7. 统一引擎接口
45个引擎，可以统一接口规范
