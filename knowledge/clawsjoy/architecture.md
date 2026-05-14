# ClawsJoy 架构知识

## 服务端口
- 18109: Chat API (AI对话)
- 8108: Promo API (视频生成)
- 18103: Agent API (租户代理)
- 18110: Health API (健康检查)
- 18083: Web 前端
- 16380: Redis
- 19001: TTS 服务

## 启动顺序
1. Docker: web, redis, tts
2. PM2: chat-api, promo-api, agent-api, health-api

## 数据目录
- data/keywords.json: 关键词库
- data/urls/discovered.json: URL 库
- tenants/: 租户数据
- logs/: 日志文件
