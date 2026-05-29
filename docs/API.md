
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
