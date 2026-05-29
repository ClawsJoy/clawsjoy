
---

### 报告五：给同业者的话

```markdown
# ClawsJoy v5.0.0 - 技术白皮书

## 核心理念

ClawsJoy 不是一个 AI 助手，而是一个 **AI Agent 操作系统**。核心理念是让每个用户拥有一个真正属于自己的、会成长、懂隐私的私人管家。

## 设计哲学

1. **配置驱动 > 代码驱动**
   - 所有行为通过 YAML 配置
   - 修改配置即生效，无需重新部署

2. **代理模式 > 重复加载**
   - 单数据源 unified_config
   - 所有配置管理器都是代理

3. **用户隔离 > 数据共享**
   - 每个用户独立存储目录
   - 向量记忆按用户隔离

4. **事件驱动 > 定时轮询**
   - 主动服务由事件触发
   - 闭环系统按需运行

## 技术亮点

### 1. 统一配置代理模式

```python
# 不是重新加载YAML，而是转发
class ClosedLoopConfig:
    def get(self, path):
        return unified_config.get(f"closed_loop.{path}")
###2. 6/6 闭环大脑
感知 → 分析 → 决策 → 执行 → 反馈 → 学习
###3. L0-L4 分层记忆
层级	名称	存储
L0	会话记忆	temp_sessions/
L1	短期记忆	memory.json
L2	向量记忆	ChromaDB
L3	全局记忆	agent_memory.json
L4	长期记忆	long_term.db
###4. Agent 注册中心
{
  "personal_butler": {
    "type": "core",
    "capabilities": [...],
    "status": "active"
  }
}
性能数据
指标	数据
缓存响应	0.8秒
并发支持	4路
技能数	138
代码量	10万行
开源生态
GitHub: 

文档: 

社区: 
