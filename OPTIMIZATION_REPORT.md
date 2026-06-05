
# ClawsJoy v5 优化建议报告

## 高优先级 (立即执行)

### 1. 修复硬编码配置
- 将 `config/security/jwt.yaml` 中的密钥移至环境变量
- 使用 `core/lib/constants.py` 统一管理端口和 URL

### 2. 处理 TODO 项
- 优先处理 `aliyun_pai.py` 中的 TODO（阿里云集成）
- 完成 `skill_evolver.py` 中的技能进化逻辑

### 3. 添加数据库连接池
- 已创建 `core/lib/db_pool.py`，需要在各模块中使用

## 中优先级 (本周完成)

### 4. 添加请求追踪
- 集成 OpenTelemetry 或 Jaeger
- 添加请求 ID 到所有日志

### 5. 完善单元测试
- 当前测试覆盖率较低
- 为核心模块添加单元测试

### 6. 优化日志
- 使用结构化日志 (JSON 格式)
- 添加敏感信息脱敏

## 低优先级 (可选)

### 7. 代码重构
- 拆分 `agent_gateway_enhanced.py` (1272 行)
- 统一异常处理

### 8. 性能优化
- 实现请求缓存
- 优化数据库查询
