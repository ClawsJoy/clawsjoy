# ClawsJoy v5 配置规范

## 配置文件结构
config/
├── keywords.yaml # 统一关键词配置（核心）
├── system/ # 系统配置
├── routes/ # 路由配置
├── agents_soul/ # Agent 灵魂配置
└── engines/ # 引擎配置

## keywords.yaml 配置规范

### 1. intents（意图配置）

```yaml
intents:
  intent_name:
    name: "意图显示名称"
    keywords: ["关键词1", "关键词2"]
    skills: ["skill_name"]
    priority: 25          # 优先级 1-100
    response_template: "template_name"
###2. agent_capabilities（Agent能力声明）
agent_capabilities:
  agent_name:
    capable_of:           # 能力关键词列表
      - "关键词1"
      - "关键词2"
    priority: 25          # 路由优先级
    requires_context: false  # 是否需要上下文
###3. skills（技能关键词）
skills:
  skill_name:
    keywords: ["关键词1", "关键词2"]
###4. agent_mapping（路由映射 - 兼容旧版）
agent_mapping:
  agent_name:
    keywords: ["关键词1", "关键词2"]
##路由机制
用户输入 → 匹配 capable_of 关键词 → 优先级加权 → 选择最佳 Agent
##热重载
#自动检测：修改 keywords.yaml 后 2 秒内自动生效
#手动重载：curl -X POST http://localhost:5002/api/reload/config
##添加新 Agent
#创建 Agent 类继承 BaseAgent
#在 keywords.yaml 的 agent_capabilities 中添加能力声明
#实现 execute() 方法
#重启服务或等待自动重载
##优先级建议
#优先级	用途
#30	代码、计算等核心功能
#25	天气、翻译、视频等常用功能
#20	协作、决策、记忆等辅助功能
#15	学习、分析等后台功能
#10	聊天、问候等默认功能
##当前 Agent 能力清单
Agent	优先级	关键词数
code_agent	30	12
director_agent	25	11
weather_skill	25	10
calculator	25	12
collaboration_agent	25	7
decision_agent	25	7
vision_agent	25	8
security_agent	25	6
translate_agent	20	6
memory_agent	20	10
analysis_agent	20	6
video_agent	20	7
writer_agent	15	9
youtube_agent	20	9
dialect_agent	20	8
executor_agent	20	6
...	...	...
##版本历史
v2.0.0 (2026-06-01): 统一关键词配置，能力声明式路由
v1.0.0	2026-05-01	初始版本