# ClawsJoy V5 前端 API 备忘录

## 版本信息
- 版本: 5.0.0
- 更新日期: 2026-05-29
- 后端端口: 5002

---

## 一、核心 API

### 1.1 健康检查
```http
GET /api/health
#1.2 私人管家对话（同步简单对话）
POST /api/butler/chat
Content-Type: application/json

{
  "user_id": "用户名",
  "message": "你好"
}
#响应: {"success": true, "response": "小管随时在您身边~", "user_id": "用户名"}
#1.3 私人管家任务（异步复杂任务）
POST /api/butler/chat
Content-Type: application/json

{
  "user_id": "用户名",
  "message": "帮我计算 15+27"
}
#响应: {"success": true, "task_id": "20260529_xxx.json", "response": "任务已提交..."}
#二、主动推送 SSE
#2.1 订阅消息推送
// 前端 JavaScript 示例
const eventSource = new EventSource('http://localhost:5002/api/sse/subscribe?user_id=用户名');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到推送:', data);
  
  if (data.type === 'task_completed') {
    alert(`任务完成: ${data.response}`);
  }
};

eventSource.onerror = (error) => {
  console.error('SSE 连接错误:', error);
};
#2.2 推送消息格式
{
  "type": "connected",
  "user_id": "用户名"
}

{
  "type": "task_completed",
  "task_id": "20260529_xxx.json",
  "response": "计算结果: 42",
  "timestamp": "2026-05-29T10:00:00"
}
#三、任务状态查询（备选）
POST /api/agent/task/status
Content-Type: application/json

{
  "task_id": "20260529_xxx.json",
  "user_id": "用户名"
}
#响应: {"success": true, "status": "completed", "response": "42"}
#四、Agent 直接调用
#4.1 决策师
POST /api/agent/decision_agent/message
{"message": "帮我计算 15+27", "user_id": "用户名"}
#4.2 方言大师
POST /api/agent/dialect_agent/message
{"message": "阿拉宁波人", "user_id": "用户名"}
#4.3 技能执行
POST /api/skills/execute
{"skill": "add", "params": {"a": 15, "b": 27}}
#五、通信流程
用户提交任务
    ↓
返回 task_id
    ↓
后台异步处理
    ↓
SSE 推送结果
    ↓
前端展示
#六、注意事项
1.SSE 连接: 每个用户需要独立连接，使用 user_id 区分

2.任务 ID: 保存 task_id 用于调试和重试

3.超时处理: 30 秒无响应需提示用户

4.重连机制: SSE 断线后自动重连
#七、测试地址
健康检查: http://localhost:5002/api/health

技能列表: http://localhost:5002/api/skills

SSE 订阅: http://localhost:5002/api/sse/subscribe?user_id=test
后端闭环已完成！前端工程师可参考 docs/FRONTEND_API.md 进行对接。

---

## 后端完成总结

```bash
echo "=========================================="
echo "后端完善完成总结"
echo "=========================================="
echo ""
echo "✅ 文件队列通信 (to_decision/processing/to_chat)"
echo "✅ 决策师消费者 (自动轮询处理)"
echo "✅ SSE 主动推送 (实时通知前端)"
echo "✅ 任务状态查询 API"
echo "✅ 完整异步闭环"
echo ""
echo "📄 前端文档: docs/FRONTEND_API.md"
echo ""
echo "系统已就绪，可交付前端对接"

