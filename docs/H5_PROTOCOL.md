# ClawsJoy H5 前端协议

## 前端 → 后端

POST /v5/execute
```json
{"user_input": "我头晕", "user_id": "grandma_001"}

##后端 → 前端
###普通回复：
{"success": true, "response": "食饱矣，天气确实不错", "type": "reply"}
###动作指令：
{
  "success": true,
  "response": "正在呼叫儿子(138xxxx)...",
  "type": "action",
  "action": "dial",
  "phone": "138xxxx"
}
###短信指令：
{
  "success": true,
  "response": "已通知儿子",
  "type": "action",
  "action": "sms",
  "phone": "138xxxx",
  "message": "您家老人说头晕，请关注"
}
###前端执行
if (data.type === "action") {
  if (data.action === "dial") {
    window.location.href = `tel:${data.phone}`;
  } else if (data.action === "sms") {
    window.location.href = `sms:${data.phone}?body=${encodeURIComponent(data.message)}`;
  }
}
