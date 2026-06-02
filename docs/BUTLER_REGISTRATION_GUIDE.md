# ClawsJoy 私人管家注册开发指南

## 版本信息
- 版本: 1.0.0
- 更新日期: 2026-05-28
- 适用系统: ClawsJoy v5.0+

---

## 一、概述

私人管家是 ClawsJoy 系统中的**用户数字资产**，每个用户拥有独立的私人管家实例。与普通 Agent 不同，私人管家：

- **用户隔离**：每个用户的数据完全独立
- **动态创建**：通过 `create_butler(user_id)` 按需创建
- **俱乐部体系**：会员等级、成长系统
- **长期记忆**：L0-L4 渐进式记忆架构

---

## 二、架构设计
┌─────────────────────────────────────────────────────────────────────────────┐
│ 私人管家架构 │
├─────────────────────────────────────────────────────────────────────────────┤
│ │
│ 用户 A ──→ create_butler("user_a") ──→ ButlerV4 实例 A │
│ │ │ │
│ │ ├── memory (L0-L4) │
│ │ ├── llm (智能对话) │
│ │ └── club (俱乐部权益) │
│ │ │
│ 用户 B ──→ create_butler("user_b") ──→ ButlerV4 实例 B │
│ │
│ 数据存储: data/users/{user_id}/butler_memory/ │
│ │
└─────────────────────────────────────────────────────────────────────────────┘

---

## 三、快速开始

### 3.1 创建私人管家实例

```python
from core.butler.butler_v4 import create_butler

# 为特定用户创建管家实例
butler = create_butler(user_id="zhangsan")

# 处理用户消息
result = butler.process("你好，我叫张三")
print(result.get("response"))
3.2 API 调用
# 对话接口
curl -X POST http://localhost:5002/api/butler/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "zhangsan", "message": "你好"}'

# 响应
{
  "response": "您好！我是小管，您的私人管家。",
  "success": true,
  "user_id": "zhangsan"
}
3.3 管家改名
curl -X POST http://localhost:5002/api/butler/rename \
  -H "Content-Type: application/json" \
  -d '{"user_id": "zhangsan", "name": "小智"}'
3.4 待办管理
# 添加待办
curl -X POST http://localhost:5002/api/butler/todo \
  -H "Content-Type: application/json" \
  -d '{"user_id": "zhangsan", "task": "买牛奶"}'

# 查看待办
curl -X GET "http://localhost:5002/api/butler/todo?user_id=zhangsan"
四、俱乐部体系
4.1 会员等级
等级	需求交互次数	权益
青铜	0+	改名、聊天
白银	100+	+ 进化学习
黄金	500+	+ 数据导出
钻石	1000+	+ 多管家管理
4.2 俱乐部 API
# 获取俱乐部统计
curl -X GET http://localhost:5002/api/butler/club/stats

# 获取成员信息
curl -X GET "http://localhost:5002/api/butler/club/member?user_id=zhangsan"

# 获取排行榜
curl -X GET http://localhost:5002/api/butler/club/leaderboard
五、配置说明
5.1 管家配置 (config/butler/butler.yaml)
version: "4.0.0"

# 管家身份
identity:
  default_name: "小管"
  role: "私人管家"
  motto: "您的信任，我的使命"

# 人格特质
personality:
  type: "warm"  # warm, professional, humorous, concise
  traits:
    - "体贴"
    - "忠诚"
    - "细心"

# LLM 配置
llm:
  provider: "ollama"
  model: "qwen2.5:3b"
  temperature: 0.7
5.2 俱乐部配置 (config/butler_club.yaml)
butler_club:
  enabled: true
  membership_levels:
    - name: "bronze"
      min_interactions: 0
      features: ["rename", "chat"]
    - name: "silver"
      min_interactions: 100
      features: ["rename", "chat", "evolution"]
六、记忆系统 (L0-L4)
层级	名称	存储	用途
L0	会话层	内存	当前对话上下文
L1	日记忆层	JSON	短期记忆
L2	长期层	JSON	长期偏好
L3	向量层	ChromaDB	语义检索
L4	索引层	JSON	快速索引
# 存储偏好
butler.memory.remember_preference("coffee", "美式")

# 召回偏好
coffee = butler.memory.recall_preference("coffee")
七、数据隔离
每个用户的私人管家数据完全隔离
data/users/
├── zhangsan/
│   └── butler_memory/
│       ├── l0_session.json      # 会话记忆
│       ├── l1_daily.json         # 日记忆
│       ├── l2_long.json          # 长期记忆
│       ├── l3_vector/            # 向量记忆
│       └── l4_index.json         # 记忆索引
├── lisi/
│   └── butler_memory/
│       └── ...
八、开发新功能
8.1 扩展管家能力
# core/butler/butler_v4.py

class ButlerV4:
    # 添加新方法
    def get_weather(self, city: str) -> str:
        """获取天气"""
        # 实现天气查询
        pass

    def set_reminder(self, time: str, content: str) -> dict:
        """设置提醒"""
        # 实现提醒功能
        pass
8.2 添加新的记忆类型
# 在 memory_manager.py 中添加
def remember_habit(self, habit: str, frequency: str):
    """记住用户习惯"""
    self._store_memory("habit", habit, {"frequency": frequency})
8.3 扩展俱乐部权益
# config/butler_club.yaml
membership_levels:
  - name: "platinum"
    min_interactions: 5000
    features: ["rename", "chat", "evolution", "export", "multi_butler", "voice"]
九、常见问题
Q1: 私人管家与普通 Agent 的区别？
特性	私人管家	普通 Agent
用户隔离	✅ 独立实例	共享实例
记忆持久化	✅ L0-L4	基础记忆
俱乐部体系	✅	❌
创建方式	create_butler(user_id)	注册到管理器
数据位置	data/users/{user_id}/butler_memory/	data/users/{user_id}/agents/
Q2: 如何为已有用户创建管家？
管家会在第一次调用时自动创建，无需手动操作。

Q3: 管家记忆多久会丢失？
L0 会话记忆：会话结束清除

L1 日记忆：保留 7 天

L2 长期记忆：永久保留

L3 向量记忆：永久保留

Q4: 俱乐部等级如何升级？
每次与管家对话都会增加交互次数，达到门槛自动升级。
十、最佳实践
用户隔离：始终使用正确的 user_id

异步处理：长时间任务使用异步

记忆管理：定期清理过期记忆

俱乐部激励：鼓励用户多交互升级

个性化：利用偏好记忆提供个性化服务

十一、参考
核心模块: core/butler/butler_v4.py

记忆管理: core/butler/memory_manager.py

LLM 客户端: core/butler/llm_client.py

俱乐部配置: config/butler_club.yaml

管家配置: config/butler/butler.yaml

本指南基于 ClawsJoy v5.0 编写，私人管家是用户的数字资产

私人管家注册手册已创建，包含：
- 架构设计
- 快速开始
- API 使用
- 俱乐部体系
- 记忆系统
- 数据隔离
- 开发扩展
- 常见问题
- 最佳实践
