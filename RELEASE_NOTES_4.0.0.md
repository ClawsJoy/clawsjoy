# ClawsJoy 4.0.0 发布说明

## 发布日期
2026-05-18

## 新增特性

### 🤖 Agent 系统
- 新增 10 个智能 Agent（决策、聊天、执行、采集、安全、管家、分析等）
- Agent 间异步通信（文件交换机制）
- Agent 注册发现机制
- Agent 健康检查和自动恢复

### 🎯 技能系统
- 20+ 原子技能
- 技能注册中心
- 技能热加载
- 技能参数模板

### 🔒 安全体系
- JWT 身份认证
- HTTPS 加密通信
- 用户数据隔离
- 敏感信息脱敏（19种模式）
- 端到端加密存储

### 🧠 记忆系统
- L0 会话层
- L1 日记忆层
- L2 长期记忆层
- L3 向量检索层
- 用户偏好学习

### 📊 监控体系
- 看门狗进程监控
- 旁路指标采集
- 健康检查 API
- 服务状态 API
- 数据分析 Agent

### 🚀 部署
- Docker 容器化
- 一键启停脚本
- 自动备份脚本
- Systemd 服务支持

## 技术栈

- Python 3.13
- Flask
- JWT
- ChromaDB (向量数据库)
- Ollama (LLM)
- ComfyUI (图像生成)

## 升级指南

从 3.x 升级到 4.0 请参考 [升级文档](docs/UPGRADE.md)

## 已知问题

- preference_service 部分路由需要完善
- ComfyUI 需要手动下载模型

## 贡献者

感谢所有参与 ClawsJoy 4.0 开发的贡献者。

## 下载

- GitHub Release: https://github.com/clawsjoy/clawsjoy/releases/tag/v4.0.0
- Docker 镜像: docker pull clawsjoy/clawsjoy:4.0.0

---

**🚀 ClawsJoy 4.0 - 智能体操作系统**
