# ClawsJoy 工作流文档

## 服务启动
```bash
# 启动 Docker 服务
docker-compose up -d

# 启动 Chat API
cd bin && nohup python3 chat_api_agent.py > /tmp/chat_api.log 2>&1 &

# 启动 Promo API
cd bin && nohup python3 promo_api.py > /tmp/promo_api.log 2>&1 &
API 调用示例
# 生成视频
curl -X POST http://localhost:8105/api/promo/make \
  -H "Content-Type: application/json" \
  -d '{"city":"香港","style":"科技"}'

# AI 对话
curl -X POST http://localhost:8101/api/agent \
  -H "Content-Type: application/json" \
  -d '{"text":"你好"}'
访问地址
编辑器: http://localhost:8082/joymate/editor.html

聊天: http://localhost:8082/joymate/index.html

资料库: http://localhost:8082/joymate/library.html
