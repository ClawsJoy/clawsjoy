
ClawsJoy 4.0 架构师指南
架构决策
Agent 通信
使用异步文件夹交割 (lib/file_exchange.py)

支持内存队列和文件队列并存

安全设计
用户数据隔离 (data/users/{user_id}/)

加密存储 (lib/user_crypto.py)

JWT 认证 + HTTPS

配置驱动
所有配置在 config/driver/*.yaml

支持热加载

扩展点
添加新 Agent
继承 BaseAgent

实现 process 方法

注册到 config/agents.yaml

添加新技能
创建 skills/{name}/SKILL.md

创建 skills/{name}/scripts/main.py

系统自动发现

添加脱敏规则
编辑 config/driver/desensitization.yaml

性能指标
Agent 响应: < 100ms

LLM 调用: < 30s

图像生成: < 60s

