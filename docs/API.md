
#ClawsJoy API 文档
#基础信息
Base URL: http://localhost:5002

响应格式: JSON

#端点列表
#健康检查
GET /api/health
响应:
{"service": "gateway", "status": "ok", "version": "3.0"}
#技能列表
GET /api/skills
响应:
{"skills": ["add", "multiply", "..."], "total": 63}
#执行技能
POST /api/skills/execute
Content-Type: application/json

{"skill": "add", "params": {"a": 10, "b": 20}}
响应:
{"success": true, "result": 30}
#大脑调度
POST /api/agent/v3/do_anything
Content-Type: application/json

{"goal": "25 乘 4"}
响应:
{"success": true, "results": [...]}
#服务列表
GET /api/services
Prometheus 监控
GET /metrics
Swagger 文档
GET /apidocs/
#错误码
状态码	说明
200	成功
400	请求错误
404	资源不存在
500	服务器错误

# ClawsJoy API 文档 v4.0

## 基础信息
- Base URL: `http://localhost:5002`
- 响应格式: JSON
- 认证方式: JWT Bearer Token (可选)

---

## 智慧对话接口 (v4.0 新增)

### POST /api/v5/wisdom/chat

智慧对话接口，支持自然语言和标准化 JSON 输入。

**请求参数:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| user_id | string | 是 | - | 用户ID |
| agent | string | 否 | chat_agent | Agent 名称 |
| message | string | 否* | - | 自然语言消息 |
| action | string | 否* | chat | 动作类型 (chat/code/translate/calculate) |
| target | string | 否* | text | 目标类型 (text/code/number) |
| raw_input | string | 否* | - | 原始输入 |

*注: message 或 raw_input 至少提供一个

**支持的 Agent:**

| Agent | 说明 | 版本 |
|-------|------|------|
| chat_agent | 对话、记忆、情感、主动建议 | v4.0 |
| code_agent | 代码生成、解释、调试、优化 | v4.0 |
| analysis_agent | 数据分析、框架提供 | v4.0 |
| butler_agent | 私人管家、待办管理 | v4.0 |
| translate_agent | 多语言翻译 (中英日韩法德等) | v4.0 |
| calculator_agent | 科学计算 (sqrt/sin/cos/log等) | v4.0 |
| orchestrator | 任务编排、分解、调度 | v4.0 |
| decision_agent | 路由决策、置信度校准 | v4.0 |

**请求示例:**

```bash
# 自然语言输入
curl -X POST http://localhost:5002/api/v5/wisdom/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test", "agent":"chat_agent", "message":"我叫张三"}'

# 标准化 JSON 输入
curl -X POST http://localhost:5002/api/v5/wisdom/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test", "action":"chat", "target":"text", "raw_input":"你好"}'

# 代码生成
curl -X POST http://localhost:5002/api/v5/wisdom/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test", "agent":"code_agent", "message":"写一个快速排序函数"}'

# 翻译
curl -X POST http://localhost:5002/api/v5/wisdom/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test", "agent":"translate_agent", "message":"中译英：你好世界"}'

# 科学计算
curl -X POST http://localhost:5002/api/v5/wisdom/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test", "agent":"calculator_agent", "message":"sqrt(16) + 3^2"}'
###响应示例:
{
  "success": true,
  "response": "你好，张三！我记住你了。",
  "agent": "chat_agent_v4",
  "meta_cognition": {
    "confidence": 0.635,
    "strategy": "wisdom_wrapped"
  },
  "output_data": {
    "wisdom": {
      "experience_count": 1,
      "self_confidence": 0.635
    }
  }
}
决策管理接口 (v4.0 新增)
GET /api/v5/wisdom/decision/stats
获取决策学习统计。

请求参数:

参数	类型	必填	说明
user_id	string	是	用户ID
响应示例:
{
  "total_decisions": 10,
  "recent_accuracy": 0.85,
  "agents_calibrated": 8,
  "agent_accuracies": {
    "chat_agent": 0.92,
    "code_agent": 0.88
  }
}
POST /api/v5/wisdom/decision/feedback
提供决策反馈（用于学习）。

请求参数:

参数	类型	必填	说明
user_id	string	是	用户ID
task_id	int	是	决策任务ID
was_correct	bool	是	是否正确
correct_agent	string	否	正确的 Agent
请求示例:
curl -X POST http://localhost:5002/api/v5/wisdom/decision/feedback \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test", "task_id":0, "was_correct":true}'
GET /api/v5/wisdom/decision/history
获取决策历史。

请求参数:

参数	类型	必填	说明
user_id	string	是	用户ID
limit	int	否	返回条数，默认50
Agent 管理接口 (v4.0 新增)
GET /api/v5/agent/list
列出所有已注册的 Agent。

响应示例:
{
  "success": true,
  "agents": {
    "chat_agent": {
      "type": "v4_wisdom",
      "version": "4.0.0",
      "status": "active"
    },
    "code_agent": {
      "type": "v4_wisdom",
      "version": "4.0.0",
      "status": "active"
    }
  },
  "stats": {
    "total": 48,
    "active": 48
  }
}
POST /api/v5/agent/register
注册新 Agent。

请求参数:

参数	类型	必填	说明
name	string	是	Agent 名称
type	string	否	Agent 类型
version	string	否	版本号
POST /api/v5/agent/enable / disable
启用/禁用 Agent。

请求参数:

参数	类型	必填	说明
name	string	是	Agent 名称
原有接口 (兼容)
GET /health
健康检查
curl http://localhost:5002/health
GET /api/endpoints
列出所有端点

GET /api/skills/list
列出所有技能

POST /api/skills/execute
执行技能

POST /api/agent/v3/do_anything
大脑调度接口

GET /metrics
Prometheus 监控指标

GET /apidocs/
Swagger UI 文档

错误码
状态码	说明
200	成功
400	请求参数错误
401	未认证
403	无权限
404	资源不存在
500	服务器内部错误
版本历史
版本	日期	说明
v4.0.0	2026-06-13	智慧化系统发布
v3.0.0	2026-05-01	三层协作架构
v2.0.0	2026-03-01	多 Agent 系统
v1.0.0	2026-01-01	初始版本
Swagger UI
启动服务后访问: http://localhost:5002/apidocs/

