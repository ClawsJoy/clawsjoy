# Changelog

## [5.1.0] - 2026-06-11

### 新增
- 配置驱动意图路由器 (10个意图)
- 持久化记忆系统 (JSON存储)
- 安全计算器 (替代 eval)
- Web 聊天界面
- 流式响应 (SSE)
- Redis 缓存支持
- Swagger API 文档

### 优化
- 并发性能提升 (Flask 多线程)
- 缓存命中率优化
- 异常处理完善
- 代码结构重构

### 修复
- 循环导入问题
- eval 安全漏洞
- 裸 except 异常处理
- Token 认证问题

## [5.0.0] - 2026-06-01

### 新增
- 基础对话功能
- 多轮对话记忆
- 代码生成
- 数学计算

### 初始版本
- 项目初始化
- 基础架构搭建

## v9.0 — 2026-07-11 (四十八次测试优化)

### 新增
- **status_hint 规则引擎**：read_file content 顶部植入系统提示，打断逐段读取（22→14 轮）
  - 规则1：测试文件检测
  - 规则2：_calculate 方法检测（METHOD_HINTS 配置化）
- **query_index 代码索引查询**：AST 快速路径 + 关键词匹配，替代逐段读文件
- **自动测试闭环**：规则4，改→跑→失败→修复→通过，最多 3 次循环
- **Plan Mode**：复杂任务自发规划，多轮对话自然承载
- **元认知注入通道**：GLM 5.2 优化建议注入到 Agent 上下文

### 修复
- V8：/v9/task 读取 .agent_state.json 替代 .task_state.json
- V8：任务完成时同步 task_engine.transition 到 done
- 异步引擎 write_file 对齐同步版（行数保护 + 备份）
- 前端异步轮询加重试计数，超时提示
- query_index SyntaxWarning 抑制

### 优化
- 提取 _get_agent_tools() 消除 tools 定义重复（98 行 → 1 处）
- 异步引擎 max_rounds 30 → 100
- verify 参数保留，加 System Prompt 使用限制
- 清理临时文件，更新 .gitignore
