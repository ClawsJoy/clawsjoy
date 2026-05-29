# ClawsJoy 变更日志

## [3.0.0] - 2026-05-17

### 新增
- 版本化管理系统 v1.0.03
- 版本注册中心（JSON + YAML）
- 统一导入入口 `lib/version_registry.py`
- 版本管理规范 `VERSION_SPEC.md`

### 修复
- 监控成功率从 37.5% 修正为 100%
- `success_monitor.py` 数据源改为从日志读取
- `active_runner.log` 统计逻辑优化

### 清理
- 移除 10 个冗余 `agent_gateway_*.py` 变体
- 建立 `.version_backup/` 基线存储

### 架构
- 系统版本锁定为 3.0.0
- 模块独立版本化管理
- 配置版本化目录 `config/version/`

---

## 版本号说明

- 系统版本: `VERSION` 文件
- 模块版本: `v<ver>_<date>` 格式
- 配置版本: `config/version/v<ver>_<date>/`

---

*更多细节请参考 `VERSION_SPEC.md`*
## [5.0.0] - 2026-05-26

### 修复内容
- unified_config 统一配置入口
- 向量记忆简化版 (vector_memory_simple)
- 私人管家向量记忆召回
- 技能推荐向量索引
- routes.yaml 路由完善
- 用户数据资产管理
- Diffusion Studio 图像生成集成

### 固化文件
- core/lib/unified_config.py
- core/tenant/hot_reload_manager.py
- core/agents/personal_butler_v2.py
- api/skill_market.py
- config/routes.yaml
- lib/memory.py
- lib/user_data_manager.py
